"""The two record stores the agent eval runs against (SPEC §12.2.6).

- **normal**: what the production pipeline extracted for the dev set (prompt v4, full
  context, validation + re-ask; run ``NORMAL_RUN``). No new extraction is paid for.
- **oracle**: the gold labels, as records. An agent that fails here failed on its
  own (tool design, descriptions, reasoning), not because a record was wrong.

Both use the same record ids (``dev-00``…), so one task set runs against either, and
both are compacted so search and analytics work exactly as in the service.
"""

import datetime as dt
import json
from pathlib import Path

from dip.analytics.lake import compact
from dip.eval.runs import load_gold
from dip.schema.domain import ContractFields, ContractRecord, Provenance
from dip.service.blobs import LocalBlobStore
from dip.service.processing import record_key

NORMAL_RUN = "20261020-231956-llm-gpt-5.6-luna-single+validate-warn-reask-dev"
CREATED = dt.datetime(2026, 10, 21, tzinfo=dt.UTC)


def record_ids(doc_ids: list[str]) -> dict[str, str]:
    return {doc_id: f"dev-{i:02d}" for i, doc_id in enumerate(sorted(doc_ids))}


def build(data_dir: Path, out_dir: Path) -> dict[str, str]:
    """Write both stores; returns doc_id -> record_id."""
    gold = load_gold(data_dir, "dev")
    ids = record_ids(list(gold))
    predictions = data_dir / "runs" / NORMAL_RUN / "predictions"
    for variant in ("normal", "oracle"):
        blobs = LocalBlobStore(out_dir / variant)
        for doc_id, record in gold.items():
            if variant == "oracle":
                fields, model = record.fields, "gold"
            else:
                raw = json.loads((predictions / f"{doc_id}.json").read_text())
                fields, model = ContractFields.model_validate(raw["fields"]), "gpt-5.6-luna"
            contract = ContractRecord(
                record_id=ids[doc_id],
                document_sha256=record.text_sha256,
                created_at=CREATED,
                provenance=Provenance(
                    pipeline_version=f"agent-eval-{variant}",
                    route="text",
                    model=model,
                    prompt_version="v4" if variant == "normal" else "gold",
                ),
                fields=fields,
            )
            key = record_key(contract.record_id, CREATED.isoformat())
            blobs.put(key, contract.model_dump_json().encode(), "application/json")
        compact(blobs, force=True)
    (out_dir / "record_ids.json").write_text(json.dumps(ids, indent=2))
    return ids
