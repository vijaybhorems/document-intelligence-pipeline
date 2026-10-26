"""The agent task set (SPEC §12.2.6): questions over the dev contracts, answers from gold.

Generated, not hand-written, so every answer is checkable and the set is reproducible:

- **set**: "Which contracts governed by X law contain clause Y?" and "Which T
  contracts have no clause Y?" Scored by set F1 over record ids.
- **date**: "When does contract R expire?" Exact match on the ISO date.
- **boolean**: "Does contract R renew automatically?" (renewal term present.)
- **quote**: "Quote the Y clause of contract R." Correct if the quote is in that
  contract's text and overlaps the gold span for Y.

Every answer also carries citations (record id + quote); citation accuracy is the
share of them found verbatim (or nearly) in the cited contract.
"""

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from dip.analytics.contract_types import contract_type
from dip.eval.runs import load_gold
from dip.schema.domain import Evidence, GoldRecord, field_of, is_present
from dip.schema.registry import FIELDS, FieldType
from dip.validate.grounding import SourceText

Kind = Literal["set", "date", "boolean", "quote"]
CLAUSE_LABEL = {f.name: f.cuad_category for f in FIELDS if f.field_type is FieldType.CLAUSE}


class Task(BaseModel):
    task_id: str
    kind: Kind
    question: str
    record_ids: list[str] = []  # set: the gold answer
    date: str | None = None
    boolean: bool | None = None
    record_id: str | None = None  # the contract a date/boolean/quote task is about
    field: str | None = None


class Answer(BaseModel):
    """What the agent submits through its final_answer tool."""

    record_ids: list[str] | None = None
    date: str | None = None
    boolean: bool | None = None
    quote: str | None = None
    citations: list[dict[str, str]] = []


def _name(record: GoldRecord) -> str:
    return " ".join((record.fields.document_name.value or record.title).split())


def _a(word: str) -> str:
    return f"an {word}" if word[0].lower() in "aeiou" else f"a {word}"


def build_tasks(data_dir: Path, ids: dict[str, str]) -> list[Task]:
    gold = load_gold(data_dir, "dev")
    by_rid = {ids[d]: r for d, r in gold.items()}
    rids = sorted(by_rid)
    tasks: list[Task] = []

    def present(rid: str, field: str) -> bool:
        return is_present(field_of(by_rid[rid].fields, field))

    # set: law + clause, with 2-6 matching contracts (answerable, not trivial)
    laws: dict[str, set[str]] = {}
    for rid in rids:
        for law in by_rid[rid].fields.governing_law.values:
            laws.setdefault(law, set()).add(rid)
    pairs = []
    for law, members in sorted(laws.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        for clause in CLAUSE_LABEL:
            hits = sorted(r for r in members if present(r, clause))
            if 2 <= len(hits) <= 6:
                pairs.append((law, clause, hits))
    used: set[str] = set()
    per_law: dict[str, int] = {}
    for law, clause, hits in pairs:
        if clause in used or per_law.get(law, 0) >= 2:  # variety: clauses and laws
            continue
        if len([t for t in tasks if t.kind == "set"]) >= 6:
            break
        used.add(clause)
        per_law[law] = per_law.get(law, 0) + 1
        tasks.append(
            Task(
                task_id=f"set-{len(tasks):02d}",
                kind="set",
                question=f"Which contracts governed by {law} law contain "
                f"{_a(CLAUSE_LABEL[clause])} clause? Answer with their record_ids.",
                record_ids=hits,
            )
        )
    # set: type + absent clause
    types: dict[str, list[str]] = {}
    for rid in rids:
        types.setdefault(contract_type(by_rid[rid].fields.document_name.value), []).append(rid)
    for ctype, members in sorted(types.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if ctype == "Unknown" or len([t for t in tasks if t.kind == "set"]) >= 8:
            continue
        for clause in (
            "anti_assignment",
            "governing_law_clause",
            "audit_rights",
            "cap_on_liability",
        ):
            if clause not in CLAUSE_LABEL:
                continue
            hits = sorted(r for r in members if not present(r, clause))
            if 1 <= len(hits) <= 5 and len(hits) < len(members):
                tasks.append(
                    Task(
                        task_id=f"set-{len(tasks):02d}",
                        kind="set",
                        question=f"Which {ctype} agreements have NO {CLAUSE_LABEL[clause]} "
                        "clause? Answer with their record_ids.",
                        record_ids=hits,
                    )
                )
                break

    # date: complete expiration dates
    for rid in rids:
        dates = [d for d in by_rid[rid].fields.expiration_date.values if d.is_complete]
        if dates and len([t for t in tasks if t.kind == "date"]) < 6:
            tasks.append(
                Task(
                    task_id=f"date-{len(tasks):02d}",
                    kind="date",
                    question=f"When does contract {rid} ({_name(by_rid[rid])}) expire? "
                    "Answer with the date (YYYY-MM-DD).",
                    date=str(dates[0].to_date()),
                    record_id=rid,
                    field="expiration_date",
                )
            )
    # boolean: auto-renewal, balanced yes/no
    yes = [r for r in rids if present(r, "renewal_term")][:3]
    no = [r for r in rids if not present(r, "renewal_term")][:2]
    for rid in yes + no:
        tasks.append(
            Task(
                task_id=f"bool-{len(tasks):02d}",
                kind="boolean",
                # CUAD's Renewal Term covers optional extensions too, so don't ask about
                # *automatic* renewal: D8 v1 of this question did, and its gold was wrong.
                question=f"Does contract {rid} ({_name(by_rid[rid])}) provide for renewing or "
                "extending its term (automatically or by option)? Answer true or false.",
                boolean=rid in yes,
                record_id=rid,
                field="renewal_term",
            )
        )
    # quote: present clauses with a gold span
    seen: set[str] = set()
    for clause in ("cap_on_liability", "non_compete", "exclusivity", "termination_for_convenience",
                   "license_grant", "audit_rights"):  # fmt: skip
        if clause not in CLAUSE_LABEL:
            continue
        for rid in rids:
            value = field_of(by_rid[rid].fields, clause)
            if rid not in seen and value.evidence:
                seen.add(rid)
                tasks.append(
                    Task(
                        task_id=f"quote-{len(tasks):02d}",
                        kind="quote",
                        question=f"Quote the {CLAUSE_LABEL[clause]} clause of contract {rid} "
                        f"({_name(by_rid[rid])}).",
                        record_id=rid,
                        field=clause,
                    )
                )
                break
    return tasks


# ---------------------------------------------------------------- scoring


class Score(BaseModel):
    task_id: str
    kind: Kind
    correct: bool
    f1: float | None = None
    citations: int = 0
    citations_grounded: int = 0


_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def scorer(data_dir: Path, ids: dict[str, str]) -> Callable[[Task, Answer | None], Score]:
    gold = load_gold(data_dir, "dev")
    by_rid = {ids[d]: r for d, r in gold.items()}
    txt_dir = data_dir / "raw" / "CUAD_v1" / "full_contract_txt"
    texts: dict[str, SourceText] = {}

    def source(rid: str) -> SourceText | None:
        if rid not in by_rid:
            return None
        if rid not in texts:
            texts[rid] = SourceText((txt_dir / by_rid[rid].txt_path).read_text("utf-8"))
        return texts[rid]

    def grounded(rid: str, quote: str) -> bool:
        text = source(rid)
        return bool(text and quote.strip() and text.ground(Evidence(quote=quote)).grounded)

    def score(task: Task, answer: Answer | None) -> Score:
        if answer is None:
            return Score(task_id=task.task_id, kind=task.kind, correct=False, f1=0.0)
        cites = [c for c in answer.citations if c.get("quote")]
        ok_cites = sum(grounded(c.get("record_id", ""), c["quote"]) for c in cites)
        base = {"task_id": task.task_id, "kind": task.kind, "citations": len(cites),
                "citations_grounded": ok_cites}  # fmt: skip
        if task.kind == "set":
            got, want = set(answer.record_ids or []), set(task.record_ids)
            tp = len(got & want)
            f1 = 2 * tp / (len(got) + len(want)) if got or want else 1.0
            return Score(**base, correct=got == want, f1=f1)
        if task.kind == "date":
            return Score(**base, correct=(answer.date or "").strip()[:10] == task.date)
        if task.kind == "boolean":
            return Score(**base, correct=answer.boolean is task.boolean)
        # quote: in the right contract, and overlapping the gold span for the clause
        quote = (answer.quote or "").strip()
        if task.record_id is None or task.field is None:
            raise ValueError(f"quote task {task.task_id} needs record_id and field")
        spans = [e.quote for e in field_of(by_rid[task.record_id].fields, task.field).evidence]
        words = _words(quote)
        overlap = max((len(words & _words(s)) / len(words) for s in spans if words), default=0.0)
        return Score(**base, correct=grounded(task.record_id, quote) and overlap >= 0.5)

    return score


def save(tasks: list[Task], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(t.model_dump_json() for t in tasks) + "\n")


def load(path: Path) -> list[Task]:
    return [Task.model_validate(json.loads(line)) for line in path.read_text().splitlines() if line]
