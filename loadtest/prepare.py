"""Pick the load-test contracts and estimate what they'll cost (SPEC §12.1, Phase 9).

    uv run python loadtest/prepare.py            # writes data/loadtest/manifest.json

TRAIN split only: test is scored once, in Phase 10, and dev/experiment drive decisions.
The sample is seeded, so the same 50 contracts are chosen every time. Ten of them are
also turned into synthetic scans, so both D1 routes are exercised.
"""

import json
import random
from pathlib import Path

import pypdfium2

from dip.config import get_settings
from dip.eval.runs import load_gold
from dip.ingest.synth_scans import scan_path, write_scans

N_DOCS, N_SCANS, SEED = 50, 10, 20261021
MAX_PAGES = 60  # keep the bill bounded; the NFR is stated for a 20-page contract
# Per page, from Phase 6 (experiment set, prompt v4, luna): ~$0.0075 / 18 pages clean,
# ~$0.015 / 18 pages scanned. Re-asks and output variance add ~20%.
USD_PER_PAGE = {"clean": 0.0075 / 18 * 1.2, "scanned": 0.015 / 18 * 1.2}


def main() -> None:
    data = get_settings().data_dir
    pdf_root = data / "raw" / "CUAD_v1" / "full_contract_pdf"
    gold = load_gold(data, "train")
    candidates = []
    for doc_id, record in sorted(gold.items()):
        path = pdf_root / record.pdf_path
        pages = len(pypdfium2.PdfDocument(path))
        if pages <= MAX_PAGES:
            candidates.append({"doc_id": doc_id, "path": str(path), "pages": pages})
    chosen = random.Random(SEED).sample(candidates, N_DOCS)  # noqa: S311 - a seeded sample, not crypto
    scans = {c["doc_id"]: Path(c["path"]) for c in chosen[:N_SCANS]}
    write_scans(scans, data / "scans")
    for i, doc in enumerate(chosen):
        doc["variant"] = "scanned" if i < N_SCANS else "clean"
        if doc["variant"] == "scanned":
            doc["path"] = str(scan_path(data / "scans", doc["doc_id"]))
        doc["estimate_usd"] = round(doc["pages"] * USD_PER_PAGE[doc["variant"]], 5)

    out = data / "loadtest" / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(chosen, indent=2))
    pages = sorted(d["pages"] for d in chosen)
    print(
        f"{len(chosen)} contracts ({N_SCANS} scanned), {sum(pages)} pages "
        f"(median {pages[len(pages) // 2]}, max {pages[-1]}); "
        f"estimated ${sum(d['estimate_usd'] for d in chosen):.2f} -> {out}"
    )


if __name__ == "__main__":
    main()
