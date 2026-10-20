"""Markdown report for one eval run, optionally compared with another (SPEC §10.5)."""

from collections.abc import Callable

from dip.eval.bootstrap import Interval, bootstrap
from dip.eval.matchers import Counts
from dip.eval.runs import RunMeta
from dip.eval.scorer import (
    FieldResult,
    GroupScore,
    Metric,
    aggregate,
    headline_metric,
    per_field,
    slice_recall,
)
from dip.eval.slices import Slice
from dip.eval.validation_metrics import ValidationMetrics
from dip.schema.registry import FIELDS, FIELDS_BY_NAME, FieldType

GroupOf = Callable[[str], str | None]


def _by_type(field: str) -> str:
    return FIELDS_BY_NAME[field].field_type.value


def _by_family(field: str) -> str | None:
    family = FIELDS_BY_NAME[field].clause_family
    return family.value if family else None


def _overall(field: str) -> str:
    return "all fields"


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{100 * value:.1f}"


def _ci(interval: Interval | None) -> str:
    return "—" if interval is None else f"{100 * interval.low:.0f}-{100 * interval.high:.0f}"


def _table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def _group_rows(
    scores: dict[str, GroupScore], cis: dict[str, dict[str, Interval]], order: list[str]
) -> list[list[str]]:
    rows = []
    for group in order:
        if group not in scores:
            continue
        s = scores[group]
        rows.append(
            [
                group,
                str(s.fields),
                str(s.micro.support),
                _pct(s.micro.precision),
                _pct(s.micro.recall),
                f"**{_pct(s.micro_f1)}**",
                _ci(cis["micro"].get(group)),
                _pct(s.macro_f1),
                _ci(cis["macro"].get(group)),
            ]
        )
    return rows


_GROUP_HEADER = ["", "fields", "support", "P", "R", "micro F1", "95% CI", "macro F1", "95% CI"]


def _grouped(
    results: list[FieldResult], metric: Metric | None, group_of: GroupOf
) -> tuple[dict[str, GroupScore], dict[str, dict[str, Interval]]]:
    return aggregate(per_field(results, metric), group_of), bootstrap(results, metric, group_of)


def render(
    meta: RunMeta,
    results: list[FieldResult],
    baseline: tuple[RunMeta, list[FieldResult]] | None = None,
    validation: ValidationMetrics | None = None,
) -> str:
    type_order = [t.value for t in FieldType]
    family_order = sorted({g for f in FIELDS if (g := _by_family(f.name))})

    headline, headline_ci = _grouped(results, None, _by_type)
    overall, overall_ci = _grouped(results, None, _overall)
    presence, presence_ci = _grouped(results, Metric.PRESENCE, _by_type)
    family, family_ci = _grouped(results, Metric.PRESENCE, _by_family)

    parts = [
        f"# Eval report: `{meta.run_id}`",
        "",
        _table(
            ["system", "split", "contracts", "git", "created (UTC)", "cost/contract", "p50 / p95"],
            [
                [
                    meta.system,
                    meta.split,
                    f"{meta.n_predicted}/{meta.n_docs}",
                    f"`{meta.git_sha}`{' (dirty)' if meta.git_dirty else ''}",
                    f"{meta.created_at:%Y-%m-%d %H:%M}",
                    _cost(meta),
                    f"{meta.latency_p50_s:.1f}s / {meta.latency_p95_s:.1f}s",
                ]
            ],
        ),
        "",
        "Percentages. **Headline metric**: presence for clauses, value for typed fields. "
        "Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count "
        "equally. CIs: 1,000 bootstrap resamples of contracts.",
        "",
        "## Headline by field type",
        "",
        _table(
            _GROUP_HEADER,
            _group_rows(headline, headline_ci, type_order)
            + _group_rows(overall, overall_ci, ["all fields"]),
        ),
        "",
        "## Presence by field type",
        "",
        "Did the system find the field at all? For typed fields this includes clauses that "
        "mention the field without a derivable value.",
        "",
        _table(_GROUP_HEADER, _group_rows(presence, presence_ci, type_order)),
        "",
        "## Clause families (presence)",
        "",
        _table(_GROUP_HEADER, _group_rows(family, family_ci, family_order)),
        "",
        "## Per field",
        "",
        "Sorted by headline F1, worst first. Support = gold positives in this split.",
        "",
        _per_field_table(results),
        "",
        "## Phrasing slice (presence recall)",
        "",
        "Canonical = gold text contains the field's obvious wording (`canonical_cues` in the "
        "registry). A large gap means the system only finds clauses phrased the expected way.",
        "",
        _slice_table(results),
    ]
    if validation is not None:
        parts += ["", *_validation_section(validation)]
    if baseline:
        parts += ["", *_comparison(results, *baseline)]
    return "\n".join(parts) + "\n"


def _per_field_table(results: list[FieldResult]) -> str:
    headline = per_field(results, None)
    presence = per_field(results, Metric.PRESENCE)
    span = per_field(results, Metric.SPAN)
    field_ci = bootstrap(results, None, _overall)["field"]

    def sort_key(name: str) -> tuple[bool, float, str]:
        f1 = headline.get(name, Counts()).f1
        return (f1 is None, f1 if f1 is not None else 0.0, name)

    rows = []
    for name in sorted(headline, key=sort_key):
        spec = FIELDS_BY_NAME[name]
        counts = headline[name]
        rows.append(
            [
                f"`{name}`",
                spec.field_type.value,
                headline_metric(spec.field_type).value,
                str(counts.support),
                _pct(counts.precision),
                _pct(counts.recall),
                f"**{_pct(counts.f1)}**",
                _ci(field_ci.get(name)),
                _pct(presence.get(name, Counts()).f1),
                _pct(span[name].f1) if name in span else "",
            ]
        )
    header = [
        "field",
        "type",
        "metric",
        "support",
        "P",
        "R",
        "F1",
        "95% CI",
        "presence F1",
        "span F1",
    ]
    return _table(header, rows)


def _slice_table(results: list[FieldResult]) -> str:
    by_field = slice_recall(results)
    pooled = {s: sum((v.get(s, Counts()) for v in by_field.values()), Counts()) for s in Slice}
    rows = []
    for name in sorted(by_field):
        canon = by_field[name].get(Slice.CANONICAL, Counts())
        other = by_field[name].get(Slice.NON_CANONICAL, Counts())
        gap = (
            f"{100 * (canon.recall - other.recall):+.1f}"
            if canon.recall is not None and other.recall is not None
            else "—"
        )
        rows.append(
            [
                f"`{name}`",
                _pct(canon.recall),
                str(canon.support),
                _pct(other.recall),
                str(other.support),
                gap,
            ]
        )
    canon, other = pooled[Slice.CANONICAL], pooled[Slice.NON_CANONICAL]
    rows.append(
        [
            "**all**",
            _pct(canon.recall),
            str(canon.support),
            _pct(other.recall),
            str(other.support),
            f"{100 * (canon.recall - other.recall):+.1f}" if canon.recall and other.recall else "—",
        ]
    )
    return _table(["field", "canonical R", "n", "non-canonical R", "n", "gap"], rows)


def _comparison(
    results: list[FieldResult], other_meta: RunMeta, other: list[FieldResult]
) -> list[str]:
    ours = aggregate(per_field(results, None), _by_type)
    theirs = aggregate(per_field(other, None), _by_type)
    rows = []
    for group in [t.value for t in FieldType]:
        a, b = ours.get(group), theirs.get(group)
        if a is None or b is None:
            continue
        delta = (
            f"{100 * (a.micro_f1 - b.micro_f1):+.1f}"
            if a.micro_f1 is not None and b.micro_f1 is not None
            else "—"
        )
        rows.append([group, _pct(b.micro_f1), _pct(a.micro_f1), delta])

    ours_f, theirs_f = per_field(results, None), per_field(other, None)
    deltas = sorted(
        (
            ((ours_f[f].f1 or 0.0) - (theirs_f[f].f1 or 0.0), f)
            for f in ours_f.keys() & theirs_f.keys()
        ),
    )
    movers = deltas[:5] + deltas[-5:]
    field_rows = [
        [f"`{f}`", _pct(theirs_f[f].f1), _pct(ours_f[f].f1), f"{100 * d:+.1f}"] for d, f in movers
    ]
    return [
        f"## Compared with `{other_meta.run_id}` ({other_meta.system})",
        "",
        _table(["field type", "before F1", "after F1", "Δ"], rows),
        "",
        "Biggest movers (headline F1):",
        "",
        _table(["field", "before", "after", "Δ"], field_rows),
    ]


def _cost(meta: RunMeta) -> str:
    if not meta.n_docs:
        return "-"
    base = float(meta.config.get("base_cost_usd", 0.0)) if meta.derived_from else 0.0
    total = (base + meta.usage.cost_usd) / meta.n_docs
    extra = (
        f" (incl. ${meta.usage.cost_usd / meta.n_docs:.4f} re-ask)"
        if meta.usage.cost_usd and meta.derived_from
        else ""
    )
    return f"${total:.4f}{extra}"


def _validation_section(v: ValidationMetrics) -> list[str]:
    fp_real = v.false_positives - v.false_positives_ungrounded
    rows = [
        [
            "valid outputs (no L1/L2 issue)",
            f"{v.contracts_valid}/{v.contracts}",
            _pct(v.valid_output_rate),
        ],
        ["quotes found in the contract", f"{v.quotes_grounded}/{v.quotes}", _pct(v.grounding_rate)],
        [
            "values with no grounded evidence",
            f"{v.values_unsupported}/{v.values}",
            _pct(v.unsupported_rate),
        ],
        [
            "false positives, ungrounded (**hallucinated**)",
            f"{v.false_positives_ungrounded}/{v.false_positives}",
            _pct(v.hallucination_rate),
        ],
        ["false positives, grounded (over-triggers)", f"{fp_real}/{v.false_positives}", ""],
        ["correct fields whose quote wasn't found", str(v.true_positives_ungrounded), ""],
    ]
    codes = ", ".join(f"`{code}` {n}" for code, n in v.issues_by_code.items()) or "none recorded"
    return [
        "## Validation",
        "",
        "Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive "
        "with no grounded quote is a hallucination; one backed by real text is an over-trigger "
        "(wrong legal reading). They need different fixes.",
        "",
        _table(["", "count", "%"], rows),
        "",
        f"Validation issues: {codes}.",
    ]
