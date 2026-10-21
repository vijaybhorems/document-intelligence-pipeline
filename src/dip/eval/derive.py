"""Derived runs: re-process a saved run's predictions without re-extracting (D6, D7).

``dip validate <run_id> --policy drop`` grounds and checks the base run's
predictions and writes a new run. It costs nothing unless ``--reask`` is given,
in which case contracts with validation errors get one follow-up LLM call for
just the failing fields, and that spend goes into the derived run's ledger.
"""

import datetime as dt
from pathlib import Path

from dip.eval.runs import (
    USAGE_LEDGER,
    Prediction,
    RunMeta,
    _quantile,
    git_state,
    load_meta,
    load_predictions,
    split_texts,
)
from dip.extract.convert import to_domain
from dip.extract.extractor import OpenAIExtractor
from dip.extract.system import Usage
from dip.validate.reask import merge, problems_for
from dip.validate.validator import Policy, validate


def validate_run(
    base_dir: Path,
    data_dir: Path,
    runs_dir: Path,
    policy: Policy,
    reasker: OpenAIExtractor | None = None,
    max_cost_usd: float | None = None,
    enforce_rules: bool = False,
) -> Path:
    base = load_meta(base_dir)
    predictions = load_predictions(base_dir)
    texts = split_texts(data_dir, base.split)
    now = dt.datetime.now(dt.UTC)
    suffix = (
        f"validate-{policy.value}"
        + ("-enforce" if enforce_rules else "")
        + ("-reask" if reasker else "")
    )
    run_id = f"{now:%Y%m%d-%H%M%S}-{base.system}+{suffix}-{base.split}"
    run_dir = runs_dir / run_id
    (run_dir / "predictions").mkdir(parents=True)
    ledger = run_dir / USAGE_LEDGER
    ledger.touch()  # derived runs always have a ledger, so the base run's cost isn't counted twice

    def record(usage: Usage) -> None:
        with ledger.open("a", encoding="utf-8") as f:
            f.write(usage.model_dump_json() + "\n")

    reask_usage: dict[str, Usage] = {}
    reask_issues: dict[str, list[str]] = {}
    if reasker is not None:
        first = {d: validate(p.fields, texts[d], policy) for d, p in predictions.items()}
        problems = {
            d: problems_for(predictions[d].fields, predictions[d].issues, first[d].issues)
            for d in predictions
        }
        answers = reasker.reask(texts, problems, max_cost_usd, record)
        for doc_id, (llm_fields, usage, issues) in answers.items():
            fresh, convert_issues = to_domain(llm_fields)
            asked = set(problems[doc_id])
            predictions[doc_id] = predictions[doc_id].model_copy(
                update={"fields": merge(predictions[doc_id].fields, fresh, asked)}
            )
            reask_usage[doc_id] = usage
            reask_issues[doc_id] = issues + convert_issues

    total = Usage()
    for doc_id, prediction in predictions.items():
        result = validate(prediction.fields, texts[doc_id], policy, enforce_rules=enforce_rules)
        usage = reask_usage.get(doc_id, Usage())
        total += usage
        # Extraction issues that a re-ask fixed are gone; keep only those still relevant.
        issues = reask_issues.get(doc_id, prediction.issues) if reasker else prediction.issues
        (run_dir / "predictions" / f"{doc_id}.json").write_text(
            Prediction(
                doc_id=doc_id,
                fields=result.fields,
                usage=prediction.usage + usage,
                issues=issues,
                validation_issues=result.issues,
            ).model_dump_json(indent=2),
            "utf-8",
        )

    sha, dirty = git_state()
    latencies = [p.usage.latency_s for p in predictions.values()]
    meta = RunMeta(
        run_id=run_id,
        created_at=now,
        system=f"{base.system}+{suffix}",
        split=base.split,
        n_docs=base.n_docs,
        n_predicted=len(predictions),
        git_sha=sha,
        git_dirty=dirty,
        config={
            **base.config,
            "validation_policy": policy.value,
            "reask": reasker is not None,
            "enforce_rules": enforce_rules,
            "base_cost_usd": base.usage.cost_usd,
        },
        usage=total,
        latency_p50_s=_quantile(latencies, 0.5),
        latency_p95_s=_quantile(latencies, 0.95),
        issues=sum(len(v) for v in reask_issues.values()),
        derived_from=base.run_id,
    )
    (run_dir / "run.json").write_text(meta.model_dump_json(indent=2), "utf-8")
    return run_dir
