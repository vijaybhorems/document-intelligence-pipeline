"""The title → contract-type rule against CUAD's folder labels. Skipped without gold."""

import json
from pathlib import Path

import duckdb
import pytest

from dip.analytics.contract_types import contract_type

GOLD = Path("data/gold")
SAME = {"Joint Venture", "Joint Venture / Filing"}  # CUAD files joint-filing agreements under both

pytestmark = [
    pytest.mark.cuad,
    pytest.mark.skipif(not (GOLD / "documents.parquet").exists(), reason="gold not built"),
]


def test_title_rule_matches_cuad_labels() -> None:
    rows = duckdb.sql(
        f"""SELECT d.contract_type, g.value_json
            FROM '{GOLD}/documents.parquet' d JOIN '{GOLD}/gold_fields.parquet' g USING (doc_id)
            WHERE g.field = 'document_name'"""
    ).fetchall()
    hits = 0
    for gold, value_json in rows:
        predicted = contract_type(json.loads(value_json).get("value"))
        hits += predicted == gold or {predicted, gold} <= SAME
    # 95.1% when written (2026-10-21); misses are mostly titles with no type ("First Amendment").
    assert hits / len(rows) >= 0.94, f"{hits}/{len(rows)}"
