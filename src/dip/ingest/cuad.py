"""Download and unpack CUAD v1 from its official Zenodo record.

The archive is untrusted input: its checksum is verified against the value
pinned here, and extraction refuses any member that would land outside the
target directory ("zip slip").
"""

import csv
import hashlib
import json
import re
import shutil
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path

import httpx

CUAD_URL = "https://zenodo.org/api/records/4595826/files/CUAD_v1.zip/content"
CUAD_MD5 = "c38f490a984420b8a62600db401fafd5"  # published on the Zenodo record
CUAD_ZIP_NAME = "CUAD_v1.zip"


class ChecksumError(RuntimeError):
    pass


class UnsafeArchiveError(RuntimeError):
    pass


def md5_of(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)  # Zenodo publishes MD5 only
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(
    url: str, dest: Path, expected_md5: str, *, client: httpx.Client | None = None
) -> Path:
    """Stream ``url`` to ``dest`` and verify it. Skips the download if a valid file exists."""
    if dest.exists() and md5_of(dest) == expected_md5:
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".part")
    client = client or httpx.Client(follow_redirects=True, timeout=60.0)
    with (
        client,
        client.stream("GET", url) as response,
        partial.open("wb") as f,
    ):
        response.raise_for_status()
        for chunk in response.iter_bytes(1 << 20):
            f.write(chunk)

    actual = md5_of(partial)
    if actual != expected_md5:
        partial.unlink()
        raise ChecksumError(f"{url}: expected md5 {expected_md5}, got {actual}")
    partial.replace(dest)
    return dest


def safe_extract(archive: Path, target: Path) -> None:
    """Extract ``archive`` into ``target``, rejecting absolute paths and ``..`` escapes."""
    root = target.resolve()
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            out = (root / member.filename).resolve()
            if not out.is_relative_to(root):
                raise UnsafeArchiveError(f"refusing to extract {member.filename!r}")
        zf.extractall(root)


def fetch_cuad(raw_dir: Path) -> Path:
    """Ensure CUAD is downloaded and extracted under ``raw_dir``. Returns the dataset root."""
    archive = download(CUAD_URL, raw_dir / CUAD_ZIP_NAME, CUAD_MD5)
    extracted = raw_dir / "CUAD_v1"
    if not extracted.exists():
        staging = raw_dir / "_extracting"
        shutil.rmtree(staging, ignore_errors=True)
        safe_extract(archive, staging)
        # The archive contains a single top-level CUAD_v1/ folder.
        (staging / "CUAD_v1").replace(extracted)
        shutil.rmtree(staging)
    return extracted


# ── Index: one entry per contract, across all four CUAD sources ─────────────

# PDF folder name -> contract type. Folders mix singular/plural and "_" for spaces.
CONTRACT_TYPES: dict[str, str] = {
    "Affiliate Agreement": "Affiliate",
    "Affiliate_Agreements": "Affiliate",
    "Agency Agreements": "Agency",
    "Co_Branding": "Co-Branding",
    "Collaboration": "Collaboration",
    "Consulting Agreements": "Consulting",
    "Development": "Development",
    "Distributor": "Distributor",
    "Endorsement": "Endorsement",
    "Endorsement Agreement": "Endorsement",
    "Franchise": "Franchise",
    "Hosting": "Hosting",
    "IP": "IP",
    "Joint Venture": "Joint Venture",
    "Joint Venture _ Filing": "Joint Venture / Filing",
    "License_Agreements": "License",
    "Maintenance": "Maintenance",
    "Manufacturing": "Manufacturing",
    "Marketing": "Marketing",
    "Non_Compete_Non_Solicit": "Non-Compete / Non-Solicit",
    "Outsourcing": "Outsourcing",
    "Promotion": "Promotion",
    "Reseller": "Reseller",
    "Service": "Service",
    "Sponsorship": "Sponsorship",
    "Strategic Alliance": "Strategic Alliance",
    "Supply": "Supply",
    "Transportation": "Transportation",
}


class CuadIndexError(RuntimeError):
    pass


def match_key(name: str) -> str:
    """Spelling-insensitive key: CUAD's sources disagree on '&' vs '_', accents, spaces."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", folded.lower())


def make_doc_id(title: str) -> str:
    """Filesystem- and URL-safe ID derived from the contract title."""
    folded = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9.-]", "_", folded)).strip("_.")


@dataclass(frozen=True)
class CuadDocument:
    doc_id: str
    title: str  # as in CUAD_v1.json; matches the .txt file stem
    contract_type: str
    text: str  # JSON context: the text all gold offsets point into
    txt_path: Path
    pdf_path: Path
    csv_row: dict[str, str]
    qas: dict[str, list[dict[str, int | str]]]  # cuad_category -> SQuAD answers


def _unique_lookup(paths: list[Path], key: str) -> Path:
    exact = [p for p in paths if match_key(p.stem) == key]
    if len(exact) == 1:
        return exact[0]
    # e.g. "..._Development Agreement_Option Agreement.pdf" for a "..._Development Agreement" row
    prefixed = [p for p in paths if match_key(p.stem).startswith(key)]
    if len(prefixed) == 1:
        return prefixed[0]
    raise CuadIndexError(f"expected one file for key {key!r}, found {len(exact) or len(prefixed)}")


def load_cuad_index(root: Path) -> list[CuadDocument]:
    """Join CUAD_v1.json, master_clauses.csv, the .txt and the .pdf for every contract."""
    squad = json.loads((root / "CUAD_v1.json").read_text(encoding="utf-8"))
    with (root / "master_clauses.csv").open(encoding="utf-8", newline="") as f:
        rows = {match_key(Path(r["Filename"]).stem): r for r in csv.DictReader(f)}
    txts = sorted((root / "full_contract_txt").glob("*.txt"))
    pdfs = sorted(p for p in (root / "full_contract_pdf").rglob("*") if p.is_file())

    documents = []
    for entry in squad["data"]:
        title = entry["title"]
        key = match_key(title)
        (paragraph,) = entry["paragraphs"]  # CUAD stores each contract as one paragraph
        pdf_path = _unique_lookup(pdfs, key)
        qas = {qa["id"].split("__", 1)[1]: qa["answers"] for qa in paragraph["qas"]}
        if key not in rows:
            raise CuadIndexError(f"no master_clauses.csv row for {title!r}")
        documents.append(
            CuadDocument(
                doc_id=make_doc_id(title),
                title=title,
                contract_type=CONTRACT_TYPES[pdf_path.parent.name],
                text=paragraph["context"],
                txt_path=_unique_lookup(txts, key),
                pdf_path=pdf_path,
                csv_row=rows[key],
                qas=qas,
            )
        )
    ids = [d.doc_id for d in documents]
    if len(set(ids)) != len(ids):
        raise CuadIndexError("doc_id collision; make_doc_id needs to be more specific")
    return sorted(documents, key=lambda d: d.doc_id)
