"""The lake's SQL F1 must equal the Python scorer's on a real eval run. Skipped without runs."""

import shutil
from pathlib import Path

import pytest

from dip.analytics.lake import push_evals
from dip.analytics.queries import Lake
from dip.eval.runs import load_results
from dip.eval.scorer import aggregate, per_field
from dip.service.blobs import LocalBlobStore

RUN = Path("data/runs/20261021-034310-llm-gpt-5.6-sol-single-v4-pypdf-clean-experiment")

pytestmark = [pytest.mark.cuad, pytest.mark.skipif(not RUN.exists(), reason="eval run not present")]


def test_sql_headline_f1_equals_the_scorer(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    shutil.copytree(RUN, runs / RUN.name)
    blobs = LocalBlobStore(tmp_path / "store")
    push_evals(runs, blobs)

    (row,) = (
        Lake(str((tmp_path / "store" / "lake").resolve()), blobs)
        .run("eval_by_route_model", {"split": "experiment"})
        .rows
    )
    expected = aggregate(per_field(load_results(RUN), None), lambda _: "all")["all"].micro_f1
    assert expected is not None
    assert row["micro_f1"] == round(100 * expected, 1)
