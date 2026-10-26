"""D8 analysis: per-variant metrics, paired bootstrap over tasks, normal-vs-oracle attribution."""

import json
import random
from pathlib import Path
from statistics import mean

from dip.agent_eval.report import attribution, load_runs, summarize
from dip.agent_eval.tasks import Score, Task, scorer

N_BOOT = 2000


def _per_task(scores: list[Score], key: str) -> dict[str, float]:
    by: dict[str, list[float]] = {}
    for s in scores:
        if key == "correct":
            by.setdefault(s.task_id, []).append(float(s.correct))
        elif s.citations:  # citation accuracy only where the agent cited
            by.setdefault(s.task_id, []).append(s.citations_grounded / s.citations)
    return {t: mean(v) for t, v in by.items()}


def paired_bootstrap(
    a: dict[str, float], b: dict[str, float], seed: int = 0
) -> tuple[float, float, float]:
    """Mean of (b - a) over shared tasks, with a 95% bootstrap CI (tasks resampled)."""
    tasks = sorted(set(a) & set(b))
    diffs = [b[t] - a[t] for t in tasks]
    rng = random.Random(seed)  # noqa: S311 - seeded resampling, not crypto
    boots = sorted(mean(rng.choices(diffs, k=len(diffs))) for _ in range(N_BOOT))
    return mean(diffs), boots[int(0.025 * N_BOOT)], boots[int(0.975 * N_BOOT)]


def analyse(runs_dir: Path, data_dir: Path, tasks: list[Task], ids: dict[str, str]) -> dict:
    score = scorer(data_dir, ids)
    by_id = {t.task_id: t for t in tasks}
    variants: dict[str, dict] = {}
    for run_dir in sorted(runs_dir.glob("*-agent-*-dev")):
        summary_path = run_dir / "summary.json"
        if not summary_path.exists():
            continue
        cfg = json.loads(summary_path.read_text())["config"]
        if cfg["repeats"] < 3:
            continue  # the pilot
        name = f"{cfg['store']}/{cfg['descriptions']}/{cfg['granularity']}"
        runs = load_runs(run_dir)
        scores = [score(by_id[r.task_id], r.answer) for _, r in runs]
        variants[name] = {
            "summary": summarize(tasks, runs, score),
            "correct": _per_task(scores, "correct"),
            "cited": _per_task(scores, "cited"),
            "run_dir": run_dir.name,
        }
    comparisons = {}
    for label, a, b in [
        ("v2 vs v1 descriptions (normal, coarse)", "normal/v1/coarse", "normal/v2/coarse"),
        ("v2 vs v1 descriptions (oracle, coarse)", "oracle/v1/coarse", "oracle/v2/coarse"),
        ("fine vs coarse tools (normal, v2)", "normal/v2/coarse", "normal/v2/fine"),
        ("fine vs coarse tools (oracle, v2)", "oracle/v2/coarse", "oracle/v2/fine"),
        ("oracle vs normal records (v2, coarse)", "normal/v2/coarse", "oracle/v2/coarse"),
    ]:
        if a in variants and b in variants:
            comparisons[label] = {
                metric: [
                    round(x, 3) for x in paired_bootstrap(variants[a][metric], variants[b][metric])
                ]
                for metric in ("correct", "cited")
            }
    attr = attribution(
        variants["normal/v2/coarse"]["summary"], variants["oracle/v2/coarse"]["summary"]
    )
    return {"variants": variants, "comparisons": comparisons, "attribution": attr}
