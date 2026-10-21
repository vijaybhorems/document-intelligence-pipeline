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
from typing import TYPE_CHECKING, Any, cast

import openai
from openai import AsyncOpenAI
from openai.types.responses import ResponseInputParam
from openai.types.shared_params import Reasoning
from opentelemetry import trace
from pydantic import BaseModel

from dip.extract import prompts
from dip.extract.convert import to_domain
from dip.extract.pricing import PRICES_AS_OF, cost_usd, price_of
from dip.extract.system import SystemOutput, Usage
from dip.schema.llm import LLMField, output_model
from dip.schema.registry import FIELDS, FieldGroup, FieldSpec

if TYPE_CHECKING:
    # LlamaIndex costs ~40% of the service's import time (Cloud Run cold start) and only
    # the retrieval experiment (D3) uses it, so it is imported where it's built.
    from dip.extract.retrieval import Retriever

MAX_OUTPUT_TOKENS_BASE = 4_000
_tracer = trace.get_tracer("dip.extract")
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
        retriever: "Retriever | None" = None,
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
        self.retriever = retriever  # None = send the full contract (decision D3)
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
        version = "" if self.prompt_version == "v1" else f"-{self.prompt_version}"
        context = "-retrieved" if self.retriever else ""
        return f"llm-{self.model}-{self.strategy.value}{suffix}{version}{context}"

    def config(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "strategy": self.strategy.value,
            "calls_per_contract": len(self._plan),
            "reasoning_effort": self.reasoning_effort,
            "shared_schema": self.shared_schema,
            "context": "retrieved" if self.retriever else "full",
            **({"retrieval_top_k": self.retriever.top_k} if self.retriever else {}),
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
        inputs: dict[str, tuple[str, bytes | None]] = {d: (text, None) for d, text in texts.items()}
        return asyncio.run(self._predict_all(inputs, max_cost_usd, on_usage))

    def predict_pdfs(
        self,
        pdfs: dict[str, bytes],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, SystemOutput]:
        """Multimodal route (D1): the model reads each PDF directly, no parser in between."""
        if self.retriever is not None:
            raise ValueError("retrieval needs text; it can't be combined with PDF input")
        inputs: dict[str, tuple[str, bytes | None]] = {d: ("", pdf) for d, pdf in pdfs.items()}
        return asyncio.run(self._predict_all(inputs, max_cost_usd, on_usage))

    async def _predict_all(
        self,
        inputs: dict[str, tuple[str, bytes | None]],
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
        if self.retriever is not None:
            all_specs = [s for _, specs, _ in self._plan for s in specs]
            await asyncio.to_thread(
                self.retriever.prepare_queries, all_specs, self.prompt_version, budget.record
            )

        async def one(doc_id: str, text: str, pdf: bytes | None) -> None:
            async with contracts:
                if budget.exhausted:
                    return
                results[doc_id] = await self._predict_one(client, calls, budget, text, pdf)

        await asyncio.gather(*(one(d, text, pdf) for d, (text, pdf) in sorted(inputs.items())))
        return results

    # ── One contract ─────────────────────────────────────────────────────────

    async def _predict_one(
        self,
        client: AsyncOpenAI,
        calls: asyncio.Semaphore,
        budget: _Budget,
        text: str,
        pdf: bytes | None = None,
    ) -> SystemOutput:
        with _tracer.start_as_current_span("extract.contract") as span:
            span.set_attributes(
                {
                    "dip.model": self.model,
                    "dip.strategy": self.strategy.value,
                    "dip.chars": len(text),
                    "dip.pdf_bytes": len(pdf or b""),
                }
            )
            output = await self._predict_one_untraced(client, calls, budget, text, pdf)
            span.set_attributes(
                {
                    "dip.cost_usd": output.usage.cost_usd,
                    "dip.calls": output.usage.calls,
                    "dip.issues": len(output.issues),
                }
            )
            return output

    async def _predict_one_untraced(
        self,
        client: AsyncOpenAI,
        calls: asyncio.Semaphore,
        budget: _Budget,
        text: str,
        pdf: bytes | None = None,
    ) -> SystemOutput:
        started = time.perf_counter()
        cache_key = "dip-" + hashlib.sha256(pdf or text.encode()).hexdigest()[:24]
        excerpts = None
        retrieval_usage = Usage()
        if self.retriever is not None:
            specs = [s for _, call_specs, _ in self._plan for s in call_specs]
            found = await asyncio.to_thread(
                self.retriever.excerpts, text, specs, self.prompt_version
            )
            budget.record(found.usage)
            retrieval_usage = found.usage
            excerpts = found.text
            trace.get_current_span().set_attributes(
                {
                    "dip.chunks_kept": found.chunks_kept,
                    "dip.chunks_total": found.chunks_total,
                    "dip.excerpt_chars": len(found.text),
                }
            )
        first, *rest = self._plan
        outcomes = [
            await self._call(
                client, calls, budget, text, cache_key, *first, excerpts=excerpts, pdf=pdf
            )
        ]
        outcomes += await asyncio.gather(
            *(
                self._call(
                    client, calls, budget, text, cache_key, *call, excerpts=excerpts, pdf=pdf
                )
                for call in rest
            )
        )
        outputs: dict[str, LLMField] = {}
        usage = retrieval_usage
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
        feedback: str | None = None,
        shared_schema: bool | None = None,
        excerpts: str | None = None,
        pdf: bytes | None = None,
    ) -> tuple[dict[str, LLMField], Usage, list[str]]:
        shared = self.shared_schema if shared_schema is None else shared_schema
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
                        input=self._messages(text, specs, shared, feedback, excerpts, pdf),
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

    # ── Re-ask (D6) ──────────────────────────────────────────────────────────

    def reask(
        self,
        texts: dict[str, str],
        problems: dict[str, dict[str, list[str]]],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, tuple[dict[str, LLMField], Usage, list[str]]]:
        """One follow-up call per contract for just the fields that failed validation.

        ``problems`` maps doc_id -> field name -> what was wrong. The model gets the
        same system prompt and contract, the field list, and the feedback.
        Returns doc_id -> (fresh LLM output for those fields, usage, issues).
        """
        return asyncio.run(self._reask_all(texts, problems, max_cost_usd, on_usage))

    async def _reask_all(
        self,
        texts: dict[str, str],
        problems: dict[str, dict[str, list[str]]],
        max_cost_usd: float | None,
        on_usage: Callable[[Usage], None] | None,
    ) -> dict[str, tuple[dict[str, LLMField], Usage, list[str]]]:
        client = self._client or AsyncOpenAI(
            api_key=self._api_key, timeout=self.timeout_s, max_retries=4
        )
        calls = asyncio.Semaphore(self.max_concurrency)
        budget = _Budget(max_cost_usd, on_usage)
        shared = output_model("AllFields", list(FIELDS), nullable=True)
        results: dict[str, tuple[dict[str, LLMField], Usage, list[str]]] = {}

        async def one(doc_id: str, by_field: dict[str, list[str]]) -> None:
            if budget.exhausted:
                return
            specs = [s for s in FIELDS if s.name in by_field]
            feedback = prompts.reask_feedback(by_field)
            cache_key = "dip-" + hashlib.sha256(texts[doc_id].encode()).hexdigest()[:24]
            results[doc_id] = await self._call(
                client,
                calls,
                budget,
                texts[doc_id],
                cache_key,
                "reask",
                specs,
                shared,
                feedback=feedback,
                shared_schema=True,
            )

        await asyncio.gather(*(one(d, p) for d, p in sorted(problems.items()) if p))
        return results

    def _messages(
        self,
        text: str,
        specs: list[FieldSpec],
        shared: bool,
        feedback: str | None,
        excerpts: str | None,
        pdf: bytes | None,
    ) -> "ResponseInputParam":
        """[system] [contract: text, excerpts or PDF] [field instructions] [re-ask feedback]."""
        v = self.prompt_version
        context: list[Any] = (
            [{"role": "user", "content": prompts.pdf_content(pdf)}]
            if pdf is not None
            else [
                {"role": "user", "content": m} for m in prompts.context_messages(text, v, excerpts)
            ]
        )
        messages: list[Any] = [
            {"role": "system", "content": prompts.system_prompt(v)},
            *context,
            {"role": "user", "content": prompts.fields_prompt(specs, v, shared)},
            *([{"role": "user", "content": feedback}] if feedback else []),
        ]
        return cast("ResponseInputParam", messages)

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
