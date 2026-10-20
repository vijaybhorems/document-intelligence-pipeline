"""``dip`` command-line entry point."""

from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from dip import __version__
from dip.config import get_settings

if TYPE_CHECKING:
    from dip.extract.system import System

app = typer.Typer(help="Document intelligence pipeline.", no_args_is_help=True)


def _paths() -> dict[str, Path]:
    data = get_settings().data_dir
    return {
        "raw": data / "raw",
        "cuad": data / "raw" / "CUAD_v1",
        "gold": data / "gold",
        "profiles": data / "profiles",
        "splits": data / "splits.json",
        "runs": data / "runs",
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


# ── Phase 2: evaluation ──────────────────────────────────────────────────────

SPLITS = ("smoke", "experiment", "dev", "test", "train")


def _check_split(split: str) -> str:
    if split not in SPLITS:
        raise typer.BadParameter(f"choose one of {', '.join(SPLITS)}")
    if split == "test":
        typer.echo("Scoring on TEST. Do this only at milestones (SPEC §2.3).", err=True)
    return split


def _run_dir(run_id: str) -> Path:
    run_dir = _paths()["runs"] / run_id
    if not (run_dir / "run.json").exists():
        raise typer.BadParameter(f"no run {run_id!r} in {_paths()['runs']}")
    return run_dir


SystemOpt = Annotated[str, typer.Option("--system", help="all_absent | keyword | llm")]
ModelOpt = Annotated[str | None, typer.Option(help="LLM model (default: DIP_EXTRACTION_MODEL).")]
StrategyOpt = Annotated[str, typer.Option(help="LLM call strategy: single | grouped | per_field")]
EffortOpt = Annotated[
    str | None, typer.Option(help="Reasoning effort (default: DIP_REASONING_EFFORT).")
]
SplitOpt = Annotated[str, typer.Option(callback=_check_split)]
OwnSchemaOpt = Annotated[
    bool,
    typer.Option(
        "--own-schema", help="Give each call its own schema (defeats prompt caching; for D4)."
    ),
]
MaxCostOpt = Annotated[
    float | None, typer.Option(help="Stop this run once it has spent this much (USD).")
]


def _make_system(
    system: str, model: str | None, strategy: str, effort: str | None, own_schema: bool = False
) -> "System":
    from dip.eval.baselines import SYSTEMS
    from dip.extract.extractor import OpenAIExtractor, Strategy

    if system in SYSTEMS:
        return SYSTEMS[system]
    if system != "llm":
        raise typer.BadParameter(f"unknown system {system!r}; choose from {[*SYSTEMS, 'llm']}")
    settings = get_settings()
    if settings.openai_api_key is None:
        raise typer.BadParameter("set DIP_OPENAI_API_KEY in .env first")
    if strategy not in Strategy.__members__.values():
        raise typer.BadParameter(f"--strategy must be one of {[s.value for s in Strategy]}")
    return OpenAIExtractor(
        model=model or settings.extraction_model,
        strategy=Strategy(strategy),
        reasoning_effort=effort or settings.reasoning_effort,
        shared_schema=not own_schema,
        max_concurrency=settings.max_concurrency,
        timeout_s=settings.request_timeout_s,
        api_key=settings.openai_api_key.get_secret_value(),
    )


def _start_tracing() -> None:
    from dip.observability.tracing import configure_tracing

    settings = get_settings()
    if configure_tracing(settings.otel_endpoint, settings.trace_content):
        typer.echo(f"tracing to {settings.otel_endpoint}")


def _budget_check(system: object, split: str, max_cost: float | None) -> float | None:
    """Print the estimate and remaining budget; refuse runs that can't fit. Returns the run cap."""
    from dip.eval.runs import spent_usd, split_texts
    from dip.extract.estimate import estimate
    from dip.extract.extractor import OpenAIExtractor

    if not isinstance(system, OpenAIExtractor):
        return None
    remaining = get_settings().budget_usd - spent_usd(_paths()["runs"])
    cap = remaining if max_cost is None else min(remaining, max_cost)
    est = estimate(system, split_texts(get_settings().data_dir, split))
    typer.echo(
        f"estimate: {est.contracts} contracts, {est.calls} calls, "
        f"{est.input_tokens:,} input + ~{est.output_tokens:,} output tokens, "
        f"${est.cost_with_cache_usd:.2f} with caching (${est.cost_no_cache_usd:.2f} without). "
        f"Budget left: ${remaining:.2f}; this run stops at ${cap:.2f}."
    )
    if est.cost_with_cache_usd > cap:
        typer.echo("Estimate exceeds the cap. Raise --max-cost-usd or DIP_BUDGET_USD.", err=True)
        raise typer.Exit(1)
    return cap


@app.command()
def estimate(
    system: SystemOpt = "llm",
    split: SplitOpt = "dev",
    model: ModelOpt = None,
    strategy: StrategyOpt = "grouped",
    effort: EffortOpt = None,
    own_schema: OwnSchemaOpt = False,
) -> None:
    """Estimate a run's tokens and cost without calling the API."""
    _budget_check(_make_system(system, model, strategy, effort, own_schema), split, max_cost=None)


@app.command()
def spend() -> None:
    """Total recorded spend across all runs, against DIP_BUDGET_USD."""
    from dip.eval.runs import run_spend_usd, spent_usd

    runs = _paths()["runs"]
    for run_dir in sorted(runs.glob("*")):
        if run_dir.is_dir() and (cost := run_spend_usd(run_dir)):
            note = "" if (run_dir / "run.json").exists() else "  (incomplete: no run.json)"
            typer.echo(f"  ${cost:7.4f}  {run_dir.name}{note}")
    typer.echo(f"spent ${spent_usd(runs):.4f} of ${get_settings().budget_usd:.2f}")


@app.command()
def predict(
    system: SystemOpt,
    split: SplitOpt = "dev",
    model: ModelOpt = None,
    strategy: StrategyOpt = "grouped",
    effort: EffortOpt = None,
    own_schema: OwnSchemaOpt = False,
    max_cost_usd: MaxCostOpt = None,
) -> None:
    """Run a system over a split and save its predictions as a new run."""
    from dip.eval.runs import load_meta
    from dip.eval.runs import predict as run_predict

    built = _make_system(system, model, strategy, effort, own_schema)
    cap = _budget_check(built, split, max_cost_usd)
    from dip.observability.tracing import shutdown_tracing

    _start_tracing()
    try:
        run_dir = run_predict(built, split, get_settings().data_dir, _paths()["runs"], cap)
    finally:
        shutdown_tracing()
    meta = load_meta(run_dir)
    typer.echo(
        f"run: {run_dir.name}  ({meta.n_predicted}/{meta.n_docs} contracts, "
        f"${meta.usage.cost_usd:.4f}, {meta.usage.cached_tokens:,}/{meta.usage.input_tokens:,} "
        f"input tokens cached, p50 {meta.latency_p50_s:.1f}s, {meta.issues} issues)"
    )
    if not meta.complete:
        typer.echo(
            "INCOMPLETE: stopped at the cost cap; missing contracts score as empty.", err=True
        )


@app.command()
def score(run_id: str) -> None:
    """Score a run's predictions against gold (writes field_results.parquet)."""
    from dip.eval.runs import dump_summary, score_run

    results = score_run(_run_dir(run_id), get_settings().data_dir)
    typer.echo(f"headline micro F1 by field type:\n{dump_summary(results)}")


@app.command()
def report(
    run_id: str,
    compare: Annotated[str | None, typer.Option(help="Another run_id to compare against.")] = None,
    out: Annotated[Path | None, typer.Option(help="Also copy the report here.")] = None,
) -> None:
    """Render a run's Markdown report (data/runs/<run_id>/report.md)."""
    from dip.eval.report import render
    from dip.eval.runs import load_meta, load_results

    run_dir = _run_dir(run_id)
    baseline = None
    if compare:
        other = _run_dir(compare)
        baseline = (load_meta(other), load_results(other))
    from dip.eval.validation_metrics import ValidationMetrics

    validation_file = run_dir / "validation.json"
    validation = (
        ValidationMetrics.model_validate_json(validation_file.read_text("utf-8"))
        if validation_file.exists()
        else None
    )
    text = render(load_meta(run_dir), load_results(run_dir), baseline, validation)
    (run_dir / "report.md").write_text(text, encoding="utf-8")
    if out:
        out.write_text(text, encoding="utf-8")
    typer.echo(f"Wrote {run_dir / 'report.md'}" + (f" and {out}" if out else ""))


@app.command("eval")
def eval_cmd(
    system: SystemOpt,
    split: SplitOpt = "dev",
    model: ModelOpt = None,
    strategy: StrategyOpt = "grouped",
    effort: EffortOpt = None,
    own_schema: OwnSchemaOpt = False,
    max_cost_usd: MaxCostOpt = None,
    compare: Annotated[str | None, typer.Option(help="run_id to compare against.")] = None,
    out: Annotated[Path | None, typer.Option(help="Also copy the report here.")] = None,
) -> None:
    """predict + score + report in one go."""
    from dip.eval.runs import predict as run_predict

    built = _make_system(system, model, strategy, effort, own_schema)
    cap = _budget_check(built, split, max_cost_usd)
    from dip.observability.tracing import shutdown_tracing

    _start_tracing()
    try:
        run_dir = run_predict(built, split, get_settings().data_dir, _paths()["runs"], cap)
    finally:
        shutdown_tracing()
    typer.echo(f"run: {run_dir.name}")
    score(run_dir.name)
    report(run_dir.name, compare=compare, out=out)


# ── Phase 4: validation ──────────────────────────────────────────────────────


@app.command()
def validate(
    run_id: str,
    policy: Annotated[str, typer.Option(help="warn | drop (decision D7)")] = "drop",
    reask: Annotated[
        bool, typer.Option("--reask", help="Re-ask the model for fields that fail (D6).")
    ] = False,
    enforce_rules: Annotated[
        bool,
        typer.Option("--enforce-rules", help="Drop dependent clauses whose parent is missing."),
    ] = False,
    max_cost_usd: MaxCostOpt = None,
    compare: Annotated[str | None, typer.Option(help="run_id to compare against.")] = None,
    out: Annotated[Path | None, typer.Option(help="Also copy the report here.")] = None,
) -> None:
    """Ground, check and re-score a saved run, without re-extracting (free unless --reask)."""
    from dip.eval.derive import validate_run
    from dip.eval.runs import load_meta, spent_usd
    from dip.extract.extractor import OpenAIExtractor, Strategy
    from dip.validate.validator import Policy

    base_dir = _run_dir(run_id)
    reasker = None
    cap = None
    if reask:
        settings = get_settings()
        if settings.openai_api_key is None:
            raise typer.BadParameter("set DIP_OPENAI_API_KEY in .env first")
        base_config = load_meta(base_dir).config
        reasker = OpenAIExtractor(
            model=base_config.get("model", settings.extraction_model),
            strategy=Strategy.SINGLE,
            reasoning_effort=base_config.get("reasoning_effort", settings.reasoning_effort),
            max_concurrency=settings.max_concurrency,
            timeout_s=settings.request_timeout_s,
            api_key=settings.openai_api_key.get_secret_value(),
        )
        remaining = settings.budget_usd - spent_usd(_paths()["runs"])
        cap = remaining if max_cost_usd is None else min(remaining, max_cost_usd)
        typer.echo(f"re-asking failing fields; budget left ${remaining:.2f}, stops at ${cap:.2f}")
    run_dir = validate_run(
        base_dir,
        get_settings().data_dir,
        _paths()["runs"],
        Policy(policy),
        reasker,
        cap,
        enforce_rules,
    )
    meta = load_meta(run_dir)
    typer.echo(f"run: {run_dir.name}  (re-ask cost ${meta.usage.cost_usd:.4f})")
    score(run_dir.name)
    report(run_dir.name, compare=compare or run_id, out=out)


if __name__ == "__main__":
    app()
