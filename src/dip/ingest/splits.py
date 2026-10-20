"""Seeded, multi-label stratified splits (SPEC §2.3).

    test        ~20%   frozen; milestone scoring only
    dev         80     prompt iteration and error analysis
    experiment  30     subset of dev, fixed for parser/model/prompt bake-offs
    smoke       5      subset of experiment, short contracts, for CI
    train       rest   few-shot examples and phrasing variants only

Stratification balances contract type *and* the presence of every field at
once (iterative stratification, Sechidis et al., ECML 2011). Stratifying on
contract type alone left the 30-contract experiment set with zero examples
of several rare clauses.

The algorithm is deterministic for a given seed and input, so anyone can
regenerate ``data/splits.json`` and get the same file. The committed file is
the source of truth: ``write_splits`` refuses to overwrite it.
"""

import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

SPLITS_VERSION = 1
DEFAULT_SEED = 20261019
TEST_FRACTION = 0.2
DEV_SIZE = 80
EXPERIMENT_SIZE = 30
SMOKE_SIZE = 5


@dataclass(frozen=True)
class SplitInput:
    doc_id: str
    contract_type: str
    text_chars: int
    present_fields: frozenset[str] = frozenset()

    @property
    def labels(self) -> frozenset[str]:
        return self.present_fields | {f"type:{self.contract_type}"}


class SplitsExistError(RuntimeError):
    pass


def _stratified_sample(
    docs: list[SplitInput], size: int, rng: random.Random
) -> tuple[list[SplitInput], list[SplitInput]]:
    """Return (sample, rest) with every label as close to proportional as possible.

    Iterative stratification: repeatedly take the label with the fewest
    unassigned documents, and give each of those documents to whichever side
    still wants that label most. Rare labels are placed first, while there is
    still room to place them well. Sizes are exact.
    """
    if not 0 <= size <= len(docs):
        raise ValueError(f"cannot take {size} from {len(docs)}")
    pending = sorted(docs, key=lambda d: d.doc_id)
    rng.shuffle(pending)
    capacity = [size, len(docs) - size]  # [sample, rest]
    share = [size / len(docs), 1 - size / len(docs)]
    totals = Counter(label for d in docs for label in d.labels)
    wanted = [{label: n * share[side] for label, n in totals.items()} for side in (0, 1)]
    sides: tuple[list[SplitInput], list[SplitInput]] = ([], [])

    while pending:
        remaining = Counter(label for d in pending for label in d.labels)
        label = min(remaining, key=lambda lb: (remaining[lb], lb)) if remaining else None
        batch = [d for d in pending if label is None or label in d.labels]
        for doc in batch:
            open_sides = [side for side in (0, 1) if capacity[side] > 0]
            side = max(
                open_sides,
                key=lambda s: (wanted[s][label] if label else 0.0, capacity[s], -s),
            )
            sides[side].append(doc)
            capacity[side] -= 1
            for doc_label in doc.labels:
                wanted[side][doc_label] -= 1
        taken = {d.doc_id for d in batch}
        pending = [d for d in pending if d.doc_id not in taken]
    return sides


def _smoke(experiment: list[SplitInput]) -> list[SplitInput]:
    """Shortest contract of each type, shortest types first: cheap and varied for CI.

    Tops up with the next-shortest contracts if there are fewer types than slots.
    """
    by_length = sorted(experiment, key=lambda d: (d.text_chars, d.doc_id))
    shortest: dict[str, SplitInput] = {}
    for doc in by_length:
        shortest.setdefault(doc.contract_type, doc)
    picked = sorted(shortest.values(), key=lambda d: (d.text_chars, d.doc_id))[:SMOKE_SIZE]
    picked += [d for d in by_length if d not in picked][: SMOKE_SIZE - len(picked)]
    return picked


def make_splits(docs: list[SplitInput], seed: int = DEFAULT_SEED) -> dict[str, list[str]]:
    rng = random.Random(seed)  # noqa: S311 (reproducible sampling, not security)
    test, rest = _stratified_sample(docs, round(len(docs) * TEST_FRACTION), rng)
    dev, train = _stratified_sample(rest, DEV_SIZE, rng)
    experiment, _ = _stratified_sample(dev, EXPERIMENT_SIZE, rng)
    smoke = _smoke(experiment)
    return {
        name: sorted(d.doc_id for d in split)
        for name, split in {
            "test": test,
            "dev": dev,
            "train": train,
            "experiment": experiment,
            "smoke": smoke,
        }.items()
    }


def write_splits(
    splits: dict[str, list[str]], path: Path, seed: int, *, force: bool = False
) -> None:
    if path.exists() and not force:
        raise SplitsExistError(
            f"{path} already exists. The test split is frozen (SPEC §2.3); "
            "use --force (force=True) only if you mean to invalidate every previous result."
        )
    payload = {
        "version": SPLITS_VERSION,
        "seed": seed,
        "method": "iterative stratification: contract type + field presence (dip.ingest.splits)",
        "counts": {name: len(ids) for name, ids in splits.items()},
        "splits": splits,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_splits(path: Path) -> dict[str, list[str]]:
    return json.loads(path.read_text(encoding="utf-8"))["splits"]
