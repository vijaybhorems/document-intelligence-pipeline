import random
from collections import Counter

import pytest

from dip.ingest.splits import (
    EXPERIMENT_SIZE,
    SMOKE_SIZE,
    SplitInput,
    SplitsExistError,
    _stratified_sample,
    make_splits,
    write_splits,
)


def _corpus() -> list[SplitInput]:
    """140 docs over 5 contract types; 'rare_clause' appears in 10 of them, spread unevenly."""
    sizes = {"License": 60, "Supply": 40, "Franchise": 25, "IP": 12, "Rare": 3}
    docs = []
    for contract_type, n in sizes.items():
        for i in range(n):
            labels = {"common_clause"} if i % 2 else set()
            if contract_type == "License" and i < 10:
                labels.add("rare_clause")  # all rare positives in one type, adjacent ids
            docs.append(
                SplitInput(
                    doc_id=f"{contract_type}-{i:03d}",
                    contract_type=contract_type,
                    text_chars=1000 + 37 * i,
                    present_fields=frozenset(labels),
                )
            )
    return docs


def _count(ids: list[str], corpus: list[SplitInput], label: str) -> int:
    by_id = {d.doc_id: d for d in corpus}
    return sum(label in by_id[i].labels for i in ids)


def test_sample_has_exact_size() -> None:
    sample, rest = _stratified_sample(_corpus(), 28, random.Random(0))

    assert (len(sample), len(rest)) == (28, 112)


def test_sample_rejects_impossible_size() -> None:
    with pytest.raises(ValueError, match="cannot take"):
        _stratified_sample(_corpus(), 141, random.Random(0))


def test_splits_are_deterministic_for_a_seed() -> None:
    assert make_splits(_corpus(), seed=7) == make_splits(_corpus(), seed=7)
    assert make_splits(_corpus(), seed=7) != make_splits(_corpus(), seed=8)


def test_test_dev_train_partition_the_corpus() -> None:
    splits = make_splits(_corpus())
    test, dev, train = set(splits["test"]), set(splits["dev"]), set(splits["train"])

    assert not test & dev
    assert not test & train
    assert not dev & train
    assert test | dev | train == {d.doc_id for d in _corpus()}
    assert len(test) == 28  # 20% of 140


def test_experiment_and_smoke_are_nested_in_dev() -> None:
    splits = make_splits(_corpus())

    assert len(splits["experiment"]) == EXPERIMENT_SIZE
    assert set(splits["experiment"]) <= set(splits["dev"])
    assert len(splits["smoke"]) == SMOKE_SIZE
    assert set(splits["smoke"]) <= set(splits["experiment"])


@pytest.mark.parametrize("seed", range(5))
def test_rare_labels_are_proportional_in_test(seed: int) -> None:
    corpus = _corpus()
    test = make_splits(corpus, seed=seed)["test"]

    assert _count(test, corpus, "rare_clause") == 2  # 10 positives x 20%
    assert abs(_count(test, corpus, "common_clause") - 14) <= 1  # 69 positives x 20%


@pytest.mark.parametrize("seed", range(5))
def test_contract_types_stay_roughly_proportional(seed: int) -> None:
    corpus = _corpus()
    types = {d.doc_id: d.contract_type for d in corpus}
    in_test = Counter(types[i] for i in make_splits(corpus, seed=seed)["test"])

    expected = {"License": 12, "Supply": 8, "Franchise": 5, "IP": 2.4, "Rare": 0.6}
    for contract_type, count in expected.items():
        assert abs(in_test[contract_type] - count) <= 1


def test_smoke_prefers_distinct_contract_types() -> None:
    corpus = _corpus()
    types = {d.doc_id: d.contract_type for d in corpus}
    smoke = make_splits(corpus)["smoke"]

    assert len(smoke) == SMOKE_SIZE
    assert len({types[i] for i in smoke}) == len(
        {types[i] for i in make_splits(corpus)["experiment"]}
    )


def test_write_splits_refuses_to_overwrite(tmp_path) -> None:
    path = tmp_path / "splits.json"
    write_splits({"test": ["a"]}, path, seed=1)

    with pytest.raises(SplitsExistError):
        write_splits({"test": ["b"]}, path, seed=1)
    write_splits({"test": ["b"]}, path, seed=1, force=True)
