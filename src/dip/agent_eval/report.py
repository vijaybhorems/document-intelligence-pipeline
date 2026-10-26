"""Score agent runs and compare variants (D8), including normal vs oracle (SPEC §12.2.6)."""

import json
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from statistics import mean
from typing import Any

from dip.agent_eval.agent import TaskRun
from dip.agent_eval.tasks import Score, Task


def load_runs(run_dir: Path) -> list[tuple[int, TaskRun]]:
    lines = (run_dir / "task_runs.jsonl").read_text().splitlines()
    out = []
    for line in lines:
        row = json.loads(line)
        out.append((row.pop("repeat"), TaskRun.model_validate(row)))
    return out


def summarize(
    tasks: list[Task], runs: list[tuple[int, TaskRun]], score: Callable[[Task, Any], Score]
) -> dict:
    by_id = {t.task_id: t for t in tasks}
    scores: list[tuple[TaskRun, Score]] = [(r, score(by_id[r.task_id], r.answer)) for _, r in runs]
    kinds: dict[str, list[bool]] = defaultdict(list)
    for _, s in scores:
        kinds[s.kind].append(s.correct)
    cites = sum(s.citations for _, s in scores)
    return {
        "runs": len(scores),
        "accuracy": round(mean(s.correct for _, s in scores), 3),
        "by_kind": {k: round(mean(v), 3) for k, v in sorted(kinds.items())},
        "set_f1": round(mean(s.f1 or 0 for _, s in scores if s.kind == "set"), 3),
        "citation_accuracy": round(sum(s.citations_grounded for _, s in scores) / cites, 3)
        if cites
        else None,
        "answered": round(mean(r.stop == "answered" for r, _ in scores), 3),
        "tool_calls_per_task": round(mean(r.tool_calls for r, _ in scores), 2),
        "tool_errors_per_task": round(mean(r.tool_errors for r, _ in scores), 2),
        "input_tokens_per_task": round(mean(r.input_tokens for r, _ in scores)),
        "cost_per_task_usd": round(mean(r.cost_usd for r, _ in scores), 5),
        "total_cost_usd": round(sum(r.cost_usd for r, _ in scores), 4),
        "per_task": {
            t: round(mean(s.correct for r, s in scores if r.task_id == t), 2) for t in sorted(by_id)
        },
    }


def attribution(normal: dict, oracle: dict) -> dict[str, list[str]]:
    """Which tasks fail because the record was wrong, and which because the agent was."""
    out: dict[str, list[str]] = {"extraction": [], "agent": [], "both_right": []}
    for task, ok_normal in normal["per_task"].items():
        ok_oracle = oracle["per_task"].get(task, 0.0)
        if ok_oracle >= 0.5 > ok_normal:
            out["extraction"].append(task)  # right with gold records, wrong with ours
        elif ok_oracle < 0.5:
            out["agent"].append(task)  # wrong even with perfect records
        else:
            out["both_right"].append(task)
    return out
