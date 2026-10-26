"""A fixed agent loop over the MCP tools (SPEC §12.2.6): one model, only these tools.

The agent sees what a real MCP client would show a model: the server's instructions,
each tool's name, description and input schema, and each result's text content. It
must finish by calling ``final_answer``. Everything else is measured: turns, tool
calls, tool errors, tokens and cost. Spend goes to the run's ``usage.jsonl`` call by
call, so the budget guard counts it even if the run dies.
"""

import json
import time
from pathlib import Path
from typing import Any

import anyio
from mcp import Client
from mcp.server.mcpserver import MCPServer
from mcp_types import TextContent
from openai import AsyncOpenAI
from pydantic import BaseModel

from dip.agent_eval.tasks import Answer, Task
from dip.eval.runs import USAGE_LEDGER
from dip.extract.pricing import cost_usd
from dip.extract.system import Usage

SYSTEM = """You answer questions about a collection of commercial contracts using only the
tools provided. Look things up; never guess. When you have the answer, call
final_answer exactly once, filling only the fields the question asks for, and add
citations: for each contract in your answer, the record_id and a short verbatim quote
(copied from a tool result) that supports it."""

FINAL_ANSWER = {
    "type": "function",
    "name": "final_answer",
    "description": "Submit your answer. Call exactly once, at the end.",
    "parameters": {
        "type": "object",
        "properties": {
            "record_ids": {"type": "array", "items": {"type": "string"}},
            "date": {"type": "string", "description": "YYYY-MM-DD"},
            "boolean": {"type": "boolean"},
            "quote": {"type": "string", "description": "Verbatim text from a tool result."},
            "citations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"record_id": {"type": "string"}, "quote": {"type": "string"}},
                    "required": ["record_id", "quote"],
                },
            },
        },
        "required": ["citations"],
    },
}
MAX_TURNS = 12


class TaskRun(BaseModel):
    task_id: str
    answer: Answer | None
    turns: int
    tool_calls: int
    tool_errors: int
    tools_used: list[str]
    input_tokens: int
    cached_tokens: int
    output_tokens: int
    cost_usd: float
    seconds: float
    stop: str  # answered | no_answer | max_turns | error


async def _tools(client: Client) -> list[dict[str, Any]]:
    listed = (await client.list_tools()).tools
    return [
        {
            "type": "function",
            "name": t.name,
            "description": t.description or "",
            "parameters": t.input_schema,
            "strict": False,
        }
        for t in listed
    ] + [FINAL_ANSWER]


async def run_task(
    task: Task,
    server: MCPServer,
    instructions: str,
    openai: AsyncOpenAI,
    model: str,
    ledger: Path,
) -> TaskRun:
    started = time.perf_counter()
    totals = {"input": 0, "cached": 0, "output": 0, "cost": 0.0}
    calls = errors = turns = 0
    used: list[str] = []
    answer: Answer | None = None
    stop = "max_turns"
    messages: list[Any] = [
        {"role": "system", "content": f"{SYSTEM}\n\nServer instructions:\n{instructions}"},
        {"role": "user", "content": task.question},
    ]
    async with Client(server) as client:
        tools = await _tools(client)
        while turns < MAX_TURNS and answer is None:
            turns += 1
            response = await openai.responses.create(
                model=model,
                input=messages,
                tools=tools,  # type: ignore[arg-type]
                reasoning={"effort": "low"},
                include=["reasoning.encrypted_content"],  # stateless: pass reasoning back
                store=False,
            )
            u = response.usage
            if u is not None:
                cached = getattr(u.input_tokens_details, "cached_tokens", 0) or 0
                cost = cost_usd(model, u.input_tokens, cached, u.output_tokens)
                totals["input"] += u.input_tokens
                totals["cached"] += cached
                totals["output"] += u.output_tokens
                totals["cost"] += cost
                usage = Usage(
                    calls=1,
                    input_tokens=u.input_tokens,
                    cached_tokens=cached,
                    output_tokens=u.output_tokens,
                    cost_usd=cost,
                )
                with ledger.open("a") as f:
                    f.write(usage.model_dump_json() + "\n")
            messages += [
                item.model_dump(mode="json", exclude_none=True) for item in response.output
            ]
            function_calls = [o for o in response.output if o.type == "function_call"]
            if not function_calls:
                stop = "no_answer"
                messages.append(
                    {"role": "user", "content": "Call final_answer with your answer now."}
                )
                continue
            for call in function_calls:
                if call.name == "final_answer":
                    try:
                        answer = Answer.model_validate_json(call.arguments)
                        stop = "answered"
                    except ValueError:
                        output = "final_answer arguments were invalid; try again."
                        errors += 1
                    else:
                        output = "recorded"
                else:
                    calls += 1
                    used.append(call.name)
                    try:
                        result = await client.call_tool(call.name, json.loads(call.arguments))
                        output = "\n".join(
                            c.text for c in result.content if isinstance(c, TextContent)
                        )
                        errors += bool(result.is_error)
                    except Exception as exc:  # protocol-level failure: tell the model
                        errors += 1
                        output = f"error: {type(exc).__name__}: {exc}"[:500]
                messages.append(
                    {"type": "function_call_output", "call_id": call.call_id, "output": output}
                )
    return TaskRun(
        task_id=task.task_id,
        answer=answer,
        turns=turns,
        tool_calls=calls,
        tool_errors=errors,
        tools_used=used,
        input_tokens=totals["input"],
        cached_tokens=totals["cached"],
        output_tokens=totals["output"],
        cost_usd=round(totals["cost"], 6),
        seconds=round(time.perf_counter() - started, 1),
        stop=stop,
    )


async def run_all(
    tasks: list[Task],
    server: MCPServer,
    instructions: str,
    model: str,
    run_dir: Path,
    repeats: int,
    concurrency: int = 6,
    api_key: str | None = None,
) -> list[tuple[int, TaskRun]]:
    run_dir.mkdir(parents=True, exist_ok=True)
    ledger = run_dir / USAGE_LEDGER
    openai = AsyncOpenAI(api_key=api_key, timeout=120)
    limiter = anyio.Semaphore(concurrency)
    results: list[tuple[int, TaskRun]] = []

    async def one(rep: int, task: Task) -> None:
        async with limiter:
            try:
                run = await run_task(task, server, instructions, openai, model, ledger)
            except Exception as exc:  # one broken task shouldn't lose the others
                run = TaskRun(
                    task_id=task.task_id, answer=None, turns=0, tool_calls=0, tool_errors=1,
                    tools_used=[], input_tokens=0, cached_tokens=0, output_tokens=0,
                    cost_usd=0.0, seconds=0.0, stop=f"error: {type(exc).__name__}",
                )  # fmt: skip
            results.append((rep, run))
            with (run_dir / "task_runs.jsonl").open("a") as f:
                f.write(json.dumps({"repeat": rep, **run.model_dump(mode="json")}) + "\n")

    async with anyio.create_task_group() as group:
        for rep in range(repeats):
            for task in tasks:
                group.start_soon(one, rep, task)
    return results
