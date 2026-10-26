"""Bootstrap confidence intervals over documents (SPEC §10.4).

Resample the *contracts* with replacement, recompute the metric, repeat. The
spread of the recomputed metric is how much the score would move with a
different sample of contracts of the same kind. With ~100 test contracts and
rare clauses, that spread is often wider than the difference between two
systems: the CI is what tells you whether a change is real.
"""

import random
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from dip.eval.matchers import Counts
from dip.eval.scorer import FieldResult, Metric, aggregate, wants

DEFAULT_ITERATIONS = 1000
DEFAULT_SEED = 0


@dataclass(frozen=True)
class Interval:
    low: float
    high: float


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return float("nan")
    index = q * (len(sorted_values) - 1)
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (index - lower)


def bootstrap(
    results: Iterable[FieldResult],
    metric: Metric | None,
    group_of: Callable[[str], str | None],
    iterations: int = DEFAULT_ITERATIONS,
    seed: int = DEFAULT_SEED,
) -> dict[str, dict[str, Interval]]:
    """95% percentile intervals for micro F1, macro F1, and per-field F1.

    Returns ``{"micro": {group: Interval}, "macro": {group: Interval}, "field": {...}}``.
    Groups or fields with no defined F1 in a resample are skipped for that resample.
    """
    per_doc: dict[str, dict[str, Counts]] = defaultdict(lambda: defaultdict(Counts))
    for r in results:
        if wants(r, metric):
            per_doc[r.doc_id][r.field] += r.counts
    docs = sorted(per_doc)
    rng = random.Random(seed)  # noqa: S311 (resampling, not security)

    samples: dict[str, dict[str, list[float]]] = {
        "micro": defaultdict(list),
        "macro": defaultdict(list),
        "field": defaultdict(list),
    }
    for _ in range(iterations):
        totals: dict[str, Counts] = defaultdict(Counts)
        for doc in rng.choices(docs, k=len(docs)):
            for field, counts in per_doc[doc].items():
                totals[field] += counts
        for field, counts in totals.items():
            if (f1 := counts.f1) is not None:
                samples["field"][field].append(f1)
        for group, score in aggregate(dict(totals), group_of).items():
            if score.micro_f1 is not None:
                samples["micro"][group].append(score.micro_f1)
            if score.macro_f1 is not None:
                samples["macro"][group].append(score.macro_f1)

    return {
        kind: {
            key: Interval(_percentile(sorted(v), 0.025), _percentile(sorted(v), 0.975))
            for key, v in by_key.items()
        }
        for kind, by_key in samples.items()
    }


@dataclass(frozen=True)
class Delta:
    """Micro-F1 difference ``b - a`` on the same contracts, with a 95% CI."""

    diff: float
    low: float
    high: float

    @property
    def significant(self) -> bool:
        return self.low > 0 or self.high < 0


def paired_delta(
    a: Iterable[FieldResult],
    b: Iterable[FieldResult],
    group_of: Callable[[str], str | None],
    metric: Metric | None = None,
    iterations: int = 2000,
    seed: int = DEFAULT_SEED,
) -> dict[str, Delta]:
    """Paired bootstrap: resample contracts once, score *both* systems on that sample.

    Pairing cancels contract difficulty: a hard sample lowers both scores together, so
    the CI reflects the systems' difference, not the sample's. Only contracts scored by
    both systems are used.
    """

    def by_doc(results: Iterable[FieldResult]) -> dict[str, dict[str, Counts]]:
        out: dict[str, dict[str, Counts]] = defaultdict(lambda: defaultdict(Counts))
        for r in results:
            if wants(r, metric):
                out[r.doc_id][r.field] += r.counts
        return out

    da, db = by_doc(a), by_doc(b)
    docs = sorted(set(da) & set(db))

    def micro(per_doc: dict[str, dict[str, Counts]], sample: list[str]) -> dict[str, float]:
        totals: dict[str, Counts] = defaultdict(Counts)
        for doc in sample:
            for field, counts in per_doc[doc].items():
                totals[field] += counts
        return {
            g: s.micro_f1
            for g, s in aggregate(dict(totals), group_of).items()
            if s.micro_f1 is not None
        }

    point_a, point_b = micro(da, docs), micro(db, docs)
    rng = random.Random(seed)  # noqa: S311 (resampling, not security)
    diffs: dict[str, list[float]] = defaultdict(list)
    for _ in range(iterations):
        sample = rng.choices(docs, k=len(docs))
        sa, sb = micro(da, sample), micro(db, sample)
        for g in sa.keys() & sb.keys():
            diffs[g].append(sb[g] - sa[g])
    return {
        g: Delta(
            point_b[g] - point_a[g],
            _percentile(sorted(diffs[g]), 0.025),
            _percentile(sorted(diffs[g]), 0.975),
        )
        for g in point_a.keys() & point_b.keys()
        if diffs[g]
    }
