"""Derived runs: re-process a saved run's predictions without re-extracting (D6, D7).

``dip validate <run_id> --policy drop`` grounds and checks the base run's
predictions and writes a new run. It costs nothing unless ``--reask`` is given,
in which case contracts with validation errors get one follow-up LLM call for
just the failing fields, and that spend goes into the derived run's ledger.
"""

import datetime as dt
from collections import defaultdict
from pathlib import Path

from dip.eval.runs import (
    USAGE_LEDGER,
    Prediction,
    RunMeta,
    _quantile,
    git_state,
    load_meta,
    load_predictions,
    split_texts,
)
from dip.extract.convert import to_domain
from dip.extract.extractor import OpenAIExtractor
from dip.extract.system import Usage
from dip.schema.domain import ContractFields, ValidationIssue, field_of
from dip.schema.registry import FIELDS, FIELDS_BY_NAME, FieldGroup
from dip.validate.validator import Policy, validate

_CALL_NAMES = {"all", *(g.value for g in FieldGroup)}


def problems_for(prediction: Prediction, issues: list[ValidationIssue]) -> dict[str, list[str]]:
    """Field -> feedback for everything worth re-asking: validation errors and L1/L2 issues."""
    problems: dict[str, list[str]] = defaultdict(list)
    for issue in issues:
        if issue.severity != "error":
            continue
        if issue.code == "unsupported_value":
            quotes = [e.quote[:200] for e in field_of(prediction.fields, issue.field).evidence]
            quoted = "; ".join(repr(q) for q in quotes) or "no quote"
            problems[issue.field].append(
                f"Your answer had no supporting text in the contract (you quoted: {quoted})."
            )
        elif issue.code in ("exception_without_restriction", "license_property_without_grant"):
            problems[issue.field].append(
                f"You marked this present, but {issue.message}. Check whether the contract "
                "really contains this clause."
            )
        elif issue.code == "date_order":
            for name in ("expiration_date", "effective_date", "agreement_date"):
                problems[name].append(f"Dates are inconsistent: {issue.message}.")
        else:
            problems[issue.field].append(issue.message)
    for raw in prediction.issues:
        target, _, message = raw.partition(":")
        if target in FIELDS_BY_NAME:
            problems[target].append(f"Your answer couldn't be used:{message}")
        elif target in _CALL_NAMES:  # a whole call failed (refusal, truncation, API error)
            for spec in FIELDS:
                if target in ("all", spec.group.value):
                    problems[spec.name].append("Your previous answer for this was missing.")
    return dict(problems)


def _merge(base: ContractFields, fresh: ContractFields, fields: set[str]) -> ContractFields:
    """Replace ``fields`` in ``base`` with their re-asked values."""
    typed = {n: getattr(fresh, n) for n in fields if n in ContractFields.model_fields}
    clauses = {n: getattr(fresh.clauses, n) for n in fields if n not in ContractFields.model_fields}
    return base.model_copy(update={**typed, "clauses": base.clauses.model_copy(update=clauses)})


def validate_run(
    base_dir: Path,
    data_dir: Path,
    runs_dir: Path,
    policy: Policy,
    reasker: OpenAIExtractor | None = None,
    max_cost_usd: float | None = None,
    enforce_rules: bool = False,
) -> Path:
    base = load_meta(base_dir)
    predictions = load_predictions(base_dir)
    texts = split_texts(data_dir, base.split)
    now = dt.datetime.now(dt.UTC)
    suffix = (
        f"validate-{policy.value}"
        + ("-enforce" if enforce_rules else "")
        + ("-reask" if reasker else "")
    )
    run_id = f"{now:%Y%m%d-%H%M%S}-{base.system}+{suffix}-{base.split}"
    run_dir = runs_dir / run_id
    (run_dir / "predictions").mkdir(parents=True)
    ledger = run_dir / USAGE_LEDGER
    ledger.touch()  # derived runs always have a ledger, so the base run's cost isn't counted twice

    def record(usage: Usage) -> None:
        with ledger.open("a", encoding="utf-8") as f:
            f.write(usage.model_dump_json() + "\n")

    reask_usage: dict[str, Usage] = {}
    reask_issues: dict[str, list[str]] = {}
    if reasker is not None:
        first = {d: validate(p.fields, texts[d], policy) for d, p in predictions.items()}
        problems = {d: problems_for(predictions[d], first[d].issues) for d in predictions}
        answers = reasker.reask(texts, problems, max_cost_usd, record)
        for doc_id, (llm_fields, usage, issues) in answers.items():
            fresh, convert_issues = to_domain(llm_fields)
            asked = set(problems[doc_id])
            predictions[doc_id] = predictions[doc_id].model_copy(
                update={"fields": _merge(predictions[doc_id].fields, fresh, asked)}
            )
            reask_usage[doc_id] = usage
            reask_issues[doc_id] = issues + convert_issues

    total = Usage()
    for doc_id, prediction in predictions.items():
        result = validate(prediction.fields, texts[doc_id], policy, enforce_rules=enforce_rules)
        usage = reask_usage.get(doc_id, Usage())
        total += usage
        # Extraction issues that a re-ask fixed are gone; keep only those still relevant.
        issues = reask_issues.get(doc_id, prediction.issues) if reasker else prediction.issues
        (run_dir / "predictions" / f"{doc_id}.json").write_text(
            Prediction(
                doc_id=doc_id,
                fields=result.fields,
                usage=prediction.usage + usage,
                issues=issues,
                validation_issues=result.issues,
            ).model_dump_json(indent=2),
            "utf-8",
        )

    sha, dirty = git_state()
    latencies = [p.usage.latency_s for p in predictions.values()]
    meta = RunMeta(
        run_id=run_id,
        created_at=now,
        system=f"{base.system}+{suffix}",
        split=base.split,
        n_docs=base.n_docs,
        n_predicted=len(predictions),
        git_sha=sha,
        git_dirty=dirty,
        config={
            **base.config,
            "validation_policy": policy.value,
            "reask": reasker is not None,
            "enforce_rules": enforce_rules,
            "base_cost_usd": base.usage.cost_usd,
        },
        usage=total,
        latency_p50_s=_quantile(latencies, 0.5),
        latency_p95_s=_quantile(latencies, 0.95),
        issues=sum(len(v) for v in reask_issues.values()),
        derived_from=base.run_id,
    )
    (run_dir / "run.json").write_text(meta.model_dump_json(indent=2), "utf-8")
    return run_dir
