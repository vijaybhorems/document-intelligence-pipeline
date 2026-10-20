"""``dip`` command-line entry point."""

from pathlib import Path
from typing import Annotated

import typer

from dip import __version__
from dip.config import get_settings

app = typer.Typer(help="Document intelligence pipeline.", no_args_is_help=True)


def _paths() -> dict[str, Path]:
    data = get_settings().data_dir
    return {
        "raw": data / "raw",
        "cuad": data / "raw" / "CUAD_v1",
        "gold": data / "gold",
        "profiles": data / "profiles",
        "splits": data / "splits.json",
    }


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def info() -> None:
    """Show the active configuration (secrets masked)."""
    settings = get_settings()
    for key, value in settings.model_dump().items():
        typer.echo(f"{key}: {value}")


# ── Phase 1: data ────────────────────────────────────────────────────────────


@app.command("download-cuad")
def download_cuad() -> None:
    """Download CUAD v1 from Zenodo (checksum-verified) and extract it."""
    from dip.ingest.cuad import fetch_cuad

    root = fetch_cuad(_paths()["raw"])
    typer.echo(f"CUAD ready at {root}")


@app.command("build-gold")
def build_gold() -> None:
    """Convert CUAD labels into gold records (data/gold/*.json + Parquet tables)."""
    from collections import Counter

    from dip.ingest.build_gold import gold_record, write_gold
    from dip.ingest.cuad import load_cuad_index

    paths = _paths()
    records = [gold_record(doc) for doc in load_cuad_index(paths["cuad"])]
    write_gold(records, paths["gold"])
    issues = Counter(i.kind for r in records for i in r.label_issues)
    typer.echo(f"Wrote {len(records)} gold records to {paths['gold']}")
    for kind, count in issues.most_common():
        typer.echo(f"  label issues · {kind}: {count}")


@app.command("make-splits")
def make_splits_cmd(
    seed: Annotated[int, typer.Option(help="Random seed.")] = 20261019,
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite the frozen splits file.")
    ] = False,
) -> None:
    """Create the frozen, stratified train/dev/test splits (data/splits.json)."""
    from dip.ingest.build_gold import gold_record, present_fields
    from dip.ingest.cuad import load_cuad_index
    from dip.ingest.splits import SplitInput, SplitsExistError, make_splits, write_splits

    paths = _paths()
    docs = [
        SplitInput(d.doc_id, d.contract_type, len(d.text), present_fields(gold_record(d)))
        for d in load_cuad_index(paths["cuad"])
    ]
    splits = make_splits(docs, seed=seed)
    try:
        write_splits(splits, paths["splits"], seed=seed, force=force)
    except SplitsExistError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo(", ".join(f"{name}={len(ids)}" for name, ids in splits.items()))


@app.command("profile-pdfs")
def profile_pdfs_cmd(
    workers: Annotated[int | None, typer.Option(help="Worker processes.")] = None,
) -> None:
    """Measure the text layer of every CUAD PDF (data/profiles/text_layer.parquet)."""
    from dip.ingest.cuad import load_cuad_index
    from dip.ingest.text_layer import profile_pdfs, write_profiles

    paths = _paths()
    docs = load_cuad_index(paths["cuad"])
    profiles = profile_pdfs({d.doc_id: d.pdf_path for d in docs}, workers=workers)
    target = paths["profiles"] / "text_layer.parquet"
    write_profiles(profiles, target)
    errors = sum(p.error is not None for p in profiles)
    typer.echo(f"Profiled {len(profiles)} PDFs ({errors} errors) -> {target}")


@app.command("cuad-report")
def cuad_report(
    out: Annotated[Path, typer.Option(help="Markdown file to write.")] = Path(
        "docs/notes/cuad-dataset-profile.md"
    ),
) -> None:
    """Write the CUAD dataset profile (prevalence, support, label issues) as Markdown."""
    from dip.analytics.cuad_report import render

    out.write_text(render(get_settings().data_dir), encoding="utf-8")
    typer.echo(f"Wrote {out}")


if __name__ == "__main__":
    app()
