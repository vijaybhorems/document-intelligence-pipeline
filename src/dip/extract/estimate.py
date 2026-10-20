"""Estimate a run's cost before paying for it (SPEC §19).

Input tokens are counted exactly with ``tiktoken``. Output tokens are an
assumption (``OUTPUT_TOKENS_*``), calibrated from real runs: compare the
estimate with ``usage`` in a run's ``run.json`` and update the constants.
"""

import json
from dataclasses import dataclass
from functools import cache

import tiktoken

from dip.extract import prompts
from dip.extract.extractor import OpenAIExtractor
from dip.extract.pricing import price_of
from dip.schema.llm import output_model
from dip.schema.registry import FIELDS

# Fitted to the Phase 3 D4 runs (gpt-5.6-luna, effort=low, experiment set): single
# ~2,000/call, grouped ~790, per_field ~435. See docs/notes/phase-3.md.
OUTPUT_TOKENS_PER_CALL = 250
OUTPUT_TOKENS_PER_FIELD = 45
OUTPUT_TOKENS_PER_NULL_FIELD = 4  # shared schema: `"field": null` for fields outside the call


@dataclass(frozen=True)
class Estimate:
    contracts: int
    calls: int
    input_tokens: int
    cacheable_tokens: int  # prefix tokens re-sent after each contract's first call
    output_tokens: int
    cost_no_cache_usd: float
    cost_with_cache_usd: float


@cache
def _encoder() -> tiktoken.Encoding:
    return tiktoken.get_encoding("o200k_base")


def _tokens(text: str) -> int:
    return len(_encoder().encode(text, disallowed_special=()))


def estimate(extractor: OpenAIExtractor, texts: dict[str, str]) -> Estimate:
    from dip.extract.extractor import call_plan

    price = price_of(extractor.model)
    plan = call_plan(extractor.strategy)
    system = _tokens(prompts.system_prompt(extractor.prompt_version))
    shared = extractor.shared_schema
    shared_schema_tokens = _tokens(
        json.dumps(output_model("x", list(FIELDS), nullable=True).model_json_schema())
    )
    per_call_extra = [
        _tokens(prompts.fields_prompt(specs, extractor.prompt_version, shared))
        + (shared_schema_tokens if shared else 0)
        for _, specs in plan
    ]
    # With a per-call schema the schema isn't part of the shared prefix; count it per call.
    per_call_schema = (
        [0] * len(plan)
        if shared
        else [_tokens(json.dumps(output_model("x", s).model_json_schema())) for _, s in plan]
    )
    output_per_contract = sum(
        OUTPUT_TOKENS_PER_CALL
        + OUTPUT_TOKENS_PER_FIELD * len(specs)
        + (OUTPUT_TOKENS_PER_NULL_FIELD * (len(FIELDS) - len(specs)) if shared else 0)
        for _, specs in plan
    )

    input_tokens = cacheable = 0
    for text in texts.values():
        prefix = system + _tokens(prompts.contract_message(text))
        input_tokens += sum(
            prefix + extra + schema
            for extra, schema in zip(per_call_extra, per_call_schema, strict=True)
        )
        if shared:  # a differing schema breaks the prefix, so nothing is cacheable
            cacheable += (prefix + shared_schema_tokens) * (len(plan) - 1)
    output_tokens = output_per_contract * len(texts)

    no_cache = (input_tokens * price.input + output_tokens * price.output) / 1e6
    with_cache = no_cache - cacheable * (price.input - price.cached_input) / 1e6
    return Estimate(
        contracts=len(texts),
        calls=len(plan) * len(texts),
        input_tokens=input_tokens,
        cacheable_tokens=cacheable,
        output_tokens=output_tokens,
        cost_no_cache_usd=no_cache,
        cost_with_cache_usd=with_cache,
    )
