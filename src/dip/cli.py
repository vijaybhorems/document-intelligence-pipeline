"""``dip`` command-line entry point."""

from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from dip import __version__
from dip.config import get_settings

if TYPE_CHECKING:
    from dip.extract.extractor import OpenAIExtractor
    from dip.extract.retrieval import Retriever
    from dip.extract.system import System
    from dip.parse.base import Parser

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
        "scans": data / "scans",
        "parsed": data / "parsed",
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
PromptOpt = Annotated[
    str | None, typer.Option("--prompt-version", help="v1 | v2 | v3 | v4 (decision D5).")
]
RouteOpt = Annotated[
    str, typer.Option("--route", help="txt | pypdf | docling | multimodal (decision D1).")
]
VariantOpt = Annotated[str, typer.Option("--variant", help="clean | scanned (synthetic scans).")]
ContextOpt = Annotated[str, typer.Option("--context", help="full | retrieved (decision D3).")]
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
    system: str,
    model: str | None,
    strategy: str,
    effort: str | None,
    own_schema: bool = False,
    prompt_version: str | None = None,
    context: str = "full",
    route: str = "txt",
    variant: str = "clean",
    split: str = "dev",
) -> "System":
    from dip.eval.baselines import SYSTEMS
    from dip.extract import prompts
    from dip.extract.extractor import OpenAIExtractor, Strategy

    if prompt_version is not None and prompt_version not in prompts.FEATURES:
        raise typer.BadParameter(f"--prompt-version must be one of {list(prompts.FEATURES)}")
    if system in SYSTEMS:
        return SYSTEMS[system]
    if system != "llm":
        raise typer.BadParameter(f"unknown system {system!r}; choose from {[*SYSTEMS, 'llm']}")
    settings = get_settings()
    if settings.openai_api_key is None:
        raise typer.BadParameter("set DIP_OPENAI_API_KEY in .env first")
    if strategy not in Strategy.__members__.values():
        raise typer.BadParameter(f"--strategy must be one of {[s.value for s in Strategy]}")
    extractor = OpenAIExtractor(
        model=model or settings.extraction_model,
        strategy=Strategy(strategy),
        reasoning_effort=effort or settings.reasoning_effort,
        shared_schema=not own_schema,
        prompt_version=prompt_version or prompts.CURRENT_VERSION,
        retriever=_retriever(context, settings.openai_api_key.get_secret_value()),
        max_concurrency=settings.max_concurrency,
        timeout_s=settings.request_timeout_s,
        api_key=settings.openai_api_key.get_secret_value(),
    )
    return _route(extractor, route, variant, split)


def _pdf_paths(split: str, variant: str) -> dict[str, Path]:
    from dip.eval.runs import load_gold
    from dip.ingest.synth_scans import scan_path

    paths = _paths()
    gold = load_gold(get_settings().data_dir, split)
    if variant == "clean":
        return {d: paths["cuad"] / "full_contract_pdf" / r.pdf_path for d, r in gold.items()}
    scans = {d: scan_path(paths["scans"], d) for d in gold}
    missing = [d for d, p in scans.items() if not p.exists()]
    if missing:
        raise typer.BadParameter(
            f"{len(missing)} scans missing; run `dip make-scans --split {split}`"
        )
    return scans


def _route(extractor: "OpenAIExtractor", route: str, variant: str, split: str) -> "System":
    from dip.extract.routes import (
        ROUTES,
        VARIANTS,
        HybridRoute,
        MultimodalRoute,
        ParsedTextRoute,
    )

    if route not in ROUTES or variant not in VARIANTS:
        raise typer.BadParameter(f"--route one of {ROUTES}, --variant one of {VARIANTS}")
    if route == "txt":
        if variant != "clean":
            raise typer.BadParameter("--route txt is CUAD's text files; there is no scanned txt")
        return extractor
    pdfs = _pdf_paths(split, variant)
    if route == "multimodal":
        return MultimodalRoute(extractor, pdfs, variant)
    if route == "hybrid":
        return HybridRoute(extractor, pdfs, variant, _paths()["parsed"])
    return ParsedTextRoute(_parser(route), extractor, pdfs, variant, _paths()["parsed"])


def _parser(route: str) -> "Parser":
    if route == "docling":
        try:
            from dip.parse.docling_parser import DoclingParser

            return DoclingParser()
        except ImportError as exc:  # optional extra: production doesn't need it (ADR D1, I3)
            raise typer.BadParameter(
                "Docling isn't installed: run `uv sync --extra docling`"
            ) from exc
    from dip.parse.pypdf_parser import PypdfParser

    return PypdfParser()


def _retriever(context: str, api_key: str) -> "Retriever | None":
    if context not in ("full", "retrieved"):
        raise typer.BadParameter("--context must be full or retrieved")
    if context == "full":
        return None
    from dip.extract.retrieval import openai_retriever

    return openai_retriever(api_key)


def _start_tracing() -> None:
    from dip.observability.tracing import start_tracing

    settings = get_settings()
    if start_tracing(settings):
        typer.echo(f"tracing to {settings.otel_endpoint}")


def _budget_check(system: object, split: str, max_cost: float | None) -> float | None:
    """Print the estimate and remaining budget; refuse runs that can't fit. Returns the run cap."""
    from pypdf import PdfReader

    from dip.eval.runs import spent_usd, split_texts
    from dip.extract.estimate import estimate
    from dip.extract.extractor import OpenAIExtractor
    from dip.extract.routes import MultimodalRoute

    # Routes wrap an extractor; the budget check must see through them.
    extractor = (
        system if isinstance(system, OpenAIExtractor) else getattr(system, "extractor", None)
    )
    if not isinstance(extractor, OpenAIExtractor):
        return None
    remaining = get_settings().budget_usd - spent_usd(_paths()["runs"])
    cap = remaining if max_cost is None else min(remaining, max_cost)
    texts = split_texts(get_settings().data_dir, split)
    pages = (
        {d: len(PdfReader(p).pages) for d, p in system.pdfs.items()}
        if isinstance(system, MultimodalRoute)
        else None
    )
    est = estimate(extractor, texts, pages)
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
    prompt_version: PromptOpt = None,
    context: ContextOpt = "full",
    route: RouteOpt = "txt",
    variant: VariantOpt = "clean",
) -> None:
    """Estimate a run's tokens and cost without calling the API."""
    _budget_check(
        _make_system(
            system,
            model,
            strategy,
            effort,
            own_schema,
            prompt_version,
            context,
            route,
            variant,
            split,
        ),
        split,
        max_cost=None,
    )


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
    prompt_version: PromptOpt = None,
    context: ContextOpt = "full",
    route: RouteOpt = "txt",
    variant: VariantOpt = "clean",
    max_cost_usd: MaxCostOpt = None,
) -> None:
    """Run a system over a split and save its predictions as a new run."""
    from dip.eval.runs import load_meta
    from dip.eval.runs import predict as run_predict

    built = _make_system(
        system, model, strategy, effort, own_schema, prompt_version, context, route, variant, split
    )
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
    prompt_version: PromptOpt = None,
    context: ContextOpt = "full",
    route: RouteOpt = "txt",
    variant: VariantOpt = "clean",
    max_cost_usd: MaxCostOpt = None,
    compare: Annotated[str | None, typer.Option(help="run_id to compare against.")] = None,
    out: Annotated[Path | None, typer.Option(help="Also copy the report here.")] = None,
) -> None:
    """predict + score + report in one go."""
    from dip.eval.runs import predict as run_predict

    built = _make_system(
        system, model, strategy, effort, own_schema, prompt_version, context, route, variant, split
    )
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


# ── Phase 5: prompting and context ───────────────────────────────────────────


@app.command("build-field-notes")
def build_field_notes_cmd() -> None:
    """Rebuild prompt variants and examples from TRAIN gold (prompts/field_notes.json)."""
    from importlib.resources import files

    from dip.eval.runs import contract_text, load_gold
    from dip.extract import prompts
    from dip.extract.examples import build_field_notes, write_field_notes

    data = get_settings().data_dir
    train = load_gold(data, "train")  # never dev or test: that would leak labels into prompts
    notes = build_field_notes((r, contract_text(data, r)) for r in train.values())
    target = Path(str(files(prompts).joinpath(prompts.FIELD_NOTES_FILE)))
    write_field_notes(notes, target)
    typer.echo(
        f"Wrote {target} from {len(train)} train contracts: "
        f"{sum(bool(n.variants) for n in notes.values())} fields with variants, "
        f"{sum(bool(n.hard_negative) for n in notes.values())} with hard negatives"
    )


# ── Phase 6: parsers and routes ──────────────────────────────────────────────


@app.command("make-scans")
def make_scans_cmd(split: SplitOpt = "experiment") -> None:
    """Create synthetic image-only scans of a split's PDFs (data/scans/), seeded per contract."""
    from dip.ingest.synth_scans import write_scans

    written = write_scans(_pdf_paths(split, "clean"), _paths()["scans"])
    typer.echo(f"{len(written)} scans in {_paths()['scans']}")


@app.command()
def parse(
    route: Annotated[str, typer.Option("--parser", help="pypdf | docling")] = "docling",
    split: SplitOpt = "experiment",
    variant: VariantOpt = "clean",
) -> None:
    """Parse a split's PDFs into the cache ahead of extraction (free; Docling is slow)."""
    import time

    from dip.parse.cache import parse_cached

    parser = _parser(route)
    total = 0.0
    for i, (doc_id, path) in enumerate(sorted(_pdf_paths(split, variant).items()), start=1):
        started = time.perf_counter()
        parsed = parse_cached(parser, path.read_bytes(), f"{doc_id}.pdf", _paths()["parsed"])
        total += time.perf_counter() - started
        typer.echo(
            f"[{i}] {doc_id[:48]:48s} {len(parsed.pages):3d} pages {len(parsed.text):8,d} chars "
            f"{parsed.seconds:6.1f}s ocr={parsed.ocr_used}"
        )
    typer.echo(f"done in {total:.0f}s")


@app.command()
def pareto(
    split: SplitOpt = "experiment",
    out: Annotated[Path, typer.Option(help="PNG to write.")] = Path("docs/img/d1-d2-pareto.png"),
) -> None:
    """Cost-vs-F1 chart of every v4 route/model/variant run on a split (needs dev deps)."""
    from dip.eval.charts import collect_points, pareto_front, render

    points = collect_points(_paths()["runs"], split)
    render(points, out, f"Cost vs quality, {split} set: prompt v4, one call per contract")
    for p in sorted(points, key=lambda p: (p.variant, p.cost)):
        star = "*" if p in pareto_front([q for q in points if q.variant == p.variant]) else " "
        typer.echo(
            f"{star} {p.variant:7s} {p.route:10s} {p.model:14s} ${p.cost:.4f}  "
            f"F1 {100 * p.f1:5.1f} [{100 * p.low:.0f}-{100 * p.high:.0f}]  runs={p.runs}"
        )
    typer.echo(f"Wrote {out}  (* = on the Pareto frontier)")


# ── Phase 7: service ─────────────────────────────────────────────────────────


@app.command()
def submit(
    files: Annotated[list[Path], typer.Argument(help="PDF or .txt contracts to upload.")],
    api: Annotated[str, typer.Option(help="Service base URL.")] = "http://localhost:8080",
    api_key: Annotated[
        str | None,
        typer.Option(envvar="DIP_API_KEY", help="X-API-Key (default: DIP_API_KEY, env or .env)."),
    ] = None,
    force: Annotated[bool, typer.Option(help="Re-extract even if already done.")] = False,
    out: Annotated[Path | None, typer.Option(help="Directory to save each record as JSON.")] = None,
) -> None:
    """Upload contracts to a running service, wait, and summarise each record."""
    import time

    import httpx

    from dip.service.client import submit as submit_one

    if api_key is None:  # like Settings: the environment first, then .env
        from dotenv import dotenv_values

        api_key = dotenv_values(".env").get("DIP_API_KEY")
    headers = {"X-API-Key": api_key} if api_key else {}
    total = 0.0
    with httpx.Client(base_url=api, headers=headers, timeout=60) as client:
        for path in files:
            started = time.perf_counter()
            job, record = submit_one(client, path, force=force)
            p, f = record.provenance, record.fields
            total += p.cost_usd
            present = sum(c.present for _, c in f.clauses)
            typer.echo(
                f"{path.name[:50]:50s} {job['status']:19s} {time.perf_counter() - started:5.1f}s "
                f"route={p.route} grounding={p.grounding} pages={p.pages} ${p.cost_usd:.4f}"
            )
            typer.echo(
                f"  name={f.document_name.value!r} parties={[x.name for x in f.parties.parties]} "
                f"clauses={present} issues={[i.code for i in record.validation_issues]}"
            )
            if out:
                out.mkdir(parents=True, exist_ok=True)
                (out / f"{record.record_id}.json").write_text(record.model_dump_json(indent=2))
    typer.echo(f"total ${total:.4f}")


if __name__ == "__main__":
    app()
