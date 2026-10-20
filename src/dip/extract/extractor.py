"""Field extraction with OpenAI Structured Outputs (SPEC §6.1, §7).

One contract = one or more calls, depending on the strategy (decision D4):

- ``single``     one call for all 41 fields
- ``grouped``    one call per field group (6 calls)
- ``per_field``  one call per field (41 calls)

Every call sends ``[system] [contract] [field instructions]``. The first call
for a contract runs alone so the shared prefix lands in OpenAI's prompt cache;
the rest run concurrently and can read it back at a discount.
"""

import asyncio
import hashlib
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any, cast

import openai
from openai import AsyncOpenAI
from openai.types.shared_params import Reasoning
from pydantic import BaseModel

from dip.extract import prompts
from dip.extract.convert import to_domain
from dip.extract.pricing import PRICES_AS_OF, cost_usd, price_of
from dip.extract.system import SystemOutput, Usage
from dip.schema.llm import LLMField, output_model
from dip.schema.registry import FIELDS, FieldGroup, FieldSpec

MAX_OUTPUT_TOKENS_BASE = 4_000
MAX_OUTPUT_TOKENS_PER_FIELD = 800
MAX_OUTPUT_TOKENS_CAP = 32_000


class Strategy(StrEnum):
    SINGLE = "single"
    GROUPED = "grouped"
    PER_FIELD = "per_field"


def call_plan(strategy: Strategy) -> list[tuple[str, list[FieldSpec]]]:
    """(call name, fields) for each call one contract needs."""
    match strategy:
        case Strategy.SINGLE:
            return [("all", list(FIELDS))]
        case Strategy.GROUPED:
            return [(g.value, [f for f in FIELDS if f.group is g]) for g in FieldGroup]
        case Strategy.PER_FIELD:
            return [(f.name, [f]) for f in FIELDS]


class _Budget:
    """Shared spend counter: stop starting new contracts once the cap is reached.

    Every paid call is also reported to ``on_usage`` as it happens, so a run that
    crashes halfway still has its spend on record.
    """

    def __init__(self, cap_usd: float | None, on_usage: Callable[[Usage], None] | None) -> None:
        self.cap = cap_usd
        self.spent = 0.0
        self.on_usage = on_usage

    def record(self, usage: Usage) -> None:
        self.spent += usage.cost_usd
        if self.on_usage:
            self.on_usage(usage)

    @property
    def exhausted(self) -> bool:
        return self.cap is not None and self.spent >= self.cap


class OpenAIExtractor:
    def __init__(
        self,
        model: str,
        strategy: Strategy = Strategy.GROUPED,
        reasoning_effort: str = "low",
        prompt_version: str = prompts.CURRENT_VERSION,
        shared_schema: bool = True,
        max_concurrency: int = 8,
        timeout_s: float = 180.0,
        api_key: str | None = None,
        client: AsyncOpenAI | None = None,
    ) -> None:
        price_of(model)  # fail fast on a model we can't cost
        self.model = model
        self.strategy = strategy
        self.reasoning_effort = reasoning_effort
        self.prompt_version = prompt_version
        # One schema for every call lets OpenAI cache [schema + system + contract].
        self.shared_schema = shared_schema and strategy is not Strategy.SINGLE
        self.max_concurrency = max_concurrency
        self.timeout_s = timeout_s
        self._api_key = api_key
        self._client = client
        shared = output_model("AllFields", list(FIELDS), nullable=True)
        self._plan = [
            (name, specs, shared if self.shared_schema else output_model(f"Fields_{name}", specs))
            for name, specs in call_plan(strategy)
        ]

    @property
    def name(self) -> str:
        suffix = "" if self.shared_schema or self.strategy is Strategy.SINGLE else "-own_schema"
        return f"llm-{self.model}-{self.strategy.value}{suffix}"

    def config(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "strategy": self.strategy.value,
            "calls_per_contract": len(self._plan),
            "reasoning_effort": self.reasoning_effort,
            "shared_schema": self.shared_schema,
            "prompt_version": self.prompt_version,
            "prices_as_of": PRICES_AS_OF,
        }

    # ── Public API ───────────────────────────────────────────────────────────

    def predict_all(
        self,
        texts: dict[str, str],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, SystemOutput]:
        return asyncio.run(self._predict_all(texts, max_cost_usd, on_usage))

    async def _predict_all(
        self,
        texts: dict[str, str],
        max_cost_usd: float | None,
        on_usage: Callable[[Usage], None] | None,
    ) -> dict[str, SystemOutput]:
        client = self._client or AsyncOpenAI(
            api_key=self._api_key, timeout=self.timeout_s, max_retries=4
        )
        calls = asyncio.Semaphore(self.max_concurrency)
        # Bound how many contracts are in flight, so the budget check stays meaningful.
        contracts = asyncio.Semaphore(max(1, self.max_concurrency // 2))
        budget = _Budget(max_cost_usd, on_usage)
        results: dict[str, SystemOutput] = {}

        async def one(doc_id: str, text: str) -> None:
            async with contracts:
                if budget.exhausted:
                    return
                results[doc_id] = await self._predict_one(client, calls, budget, text)

        await asyncio.gather(*(one(doc_id, text) for doc_id, text in sorted(texts.items())))
        return results

    # ── One contract ─────────────────────────────────────────────────────────

    async def _predict_one(
        self, client: AsyncOpenAI, calls: asyncio.Semaphore, budget: _Budget, text: str
    ) -> SystemOutput:
        started = time.perf_counter()
        cache_key = "dip-" + hashlib.sha256(text.encode()).hexdigest()[:24]
        first, *rest = self._plan
        outcomes = [await self._call(client, calls, budget, text, cache_key, *first)]
        outcomes += await asyncio.gather(
            *(self._call(client, calls, budget, text, cache_key, *call) for call in rest)
        )
        outputs: dict[str, LLMField] = {}
        usage = Usage()
        issues: list[str] = []
        for fields_out, call_usage, call_issues in outcomes:
            outputs.update(fields_out)
            usage += call_usage
            issues += call_issues
        fields, convert_issues = to_domain(outputs)
        usage = usage.model_copy(update={"latency_s": time.perf_counter() - started})
        return SystemOutput(fields=fields, usage=usage, issues=issues + convert_issues)

    async def _call(
        self,
        client: AsyncOpenAI,
        calls: asyncio.Semaphore,
        budget: _Budget,
        text: str,
        cache_key: str,
        name: str,
        specs: list[FieldSpec],
        model_cls: type[BaseModel],
    ) -> tuple[dict[str, LLMField], Usage, list[str]]:
        max_tokens = min(
            MAX_OUTPUT_TOKENS_BASE + MAX_OUTPUT_TOKENS_PER_FIELD * len(specs),
            MAX_OUTPUT_TOKENS_CAP,
        )
        usage = Usage()
        for attempt in range(2):  # one retry with more room if the output was truncated
            async with calls:
                try:
                    response = await client.responses.parse(
                        model=self.model,
                        input=[
                            {
                                "role": "system",
                                "content": prompts.system_prompt(self.prompt_version),
                            },
                            {"role": "user", "content": prompts.contract_message(text)},
                            {
                                "role": "user",
                                "content": prompts.fields_prompt(
                                    specs, self.prompt_version, self.shared_schema
                                ),
                            },
                        ],
                        text_format=model_cls,
                        reasoning=cast("Reasoning", {"effort": self.reasoning_effort}),
                        max_output_tokens=max_tokens,
                        prompt_cache_key=cache_key,
                        store=False,
                    )
                except openai.APIError as exc:
                    return {}, usage, [f"{name}: API error {type(exc).__name__}: {exc}"[:300]]
                except Exception as exc:  # one bad response must not sink a paid run
                    return {}, usage, [f"{name}: {type(exc).__name__}: {exc}"[:300]]
            call_usage = self._usage(response)
            usage += call_usage
            budget.record(call_usage)

            if response.status == "incomplete":
                if attempt == 0 and max_tokens < MAX_OUTPUT_TOKENS_CAP:
                    max_tokens = min(max_tokens * 2, MAX_OUTPUT_TOKENS_CAP)
                    continue
                return {}, usage, [f"{name}: output truncated at {max_tokens} tokens"]
            parsed = response.output_parsed
            if parsed is None:
                reason = getattr(response.incomplete_details, "reason", None) or "refusal or empty"
                return {}, usage, [f"{name}: no parsed output ({reason})"]
            fields: dict[str, LLMField] = {}
            missing = []
            for spec in specs:
                value = getattr(parsed, spec.name)
                if value is None:  # shared schema: the model nulled a field it was asked for
                    missing.append(spec.name)
                else:
                    fields[spec.name] = value
            return (
                fields,
                usage,
                [f"{name}: returned null for {', '.join(missing)}"] if missing else [],
            )
        return {}, usage, [f"{name}: output truncated after retry"]

    def _usage(self, response: Any) -> Usage:
        u = response.usage
        if u is None:
            return Usage(calls=1)
        cached = getattr(u.input_tokens_details, "cached_tokens", 0) or 0
        reasoning = getattr(u.output_tokens_details, "reasoning_tokens", 0) or 0
        return Usage(
            calls=1,
            input_tokens=u.input_tokens,
            cached_tokens=cached,
            output_tokens=u.output_tokens,
            reasoning_tokens=reasoning,
            cost_usd=cost_usd(self.model, u.input_tokens, cached, u.output_tokens),
        )
