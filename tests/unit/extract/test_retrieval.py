"""Retrieval (D3) with deterministic mock embeddings: no network."""

from types import SimpleNamespace
from typing import Any

from llama_index.core import MockEmbedding

from dip.extract.extractor import OpenAIExtractor, Strategy
from dip.extract.retrieval import Retriever, field_query
from dip.schema.registry import FIELDS, FIELDS_BY_NAME
from tests.unit.extract.test_extractor import ANSWERS, FakeResponses

SECTION = "Section {n}. The parties agree to the terms set out in this section, number {n}.\n\n"
TEXT = "".join(SECTION.format(n=i) for i in range(1, 400))


def _retriever(top_k: int = 2) -> Retriever:
    r = Retriever(MockEmbedding(embed_dim=8), top_k=top_k, chunk_tokens=128)
    r.prepare_queries(list(FIELDS), "v4", None)
    return r


def test_excerpts_are_verbatim_and_shorter() -> None:
    ex = _retriever().excerpts(TEXT, list(FIELDS), "v4")

    assert ex.chunks_kept < ex.chunks_total
    for part in ex.text.split("\n[...]\n"):
        assert part in TEXT
    assert len(ex.text) < len(TEXT)
    assert ex.usage.cost_usd > 0


def test_short_contract_comes_back_whole() -> None:
    short = "This Agreement is governed by the laws of Texas.\n\nLicensee may not assign it."

    ex = _retriever(top_k=5).excerpts(short, list(FIELDS), "v4")

    assert ex.text == short.strip() or ex.text == short


def test_field_query_uses_variants_from_v2() -> None:
    spec = FIELDS_BY_NAME["competitive_restriction_exception"]

    assert len(field_query(spec, "v2")) > len(field_query(spec, "v1"))


def test_query_embeddings_are_computed_once_per_run() -> None:
    seen: list[float] = []
    r = Retriever(MockEmbedding(embed_dim=8))
    r.prepare_queries(list(FIELDS), "v4", lambda u: seen.append(u.cost_usd))
    r.prepare_queries(list(FIELDS), "v4", lambda u: seen.append(u.cost_usd))

    assert len(seen) == 1


def test_extractor_sends_excerpts_and_records_embedding_spend() -> None:
    responses = FakeResponses(ANSWERS)
    client: Any = SimpleNamespace(responses=responses)
    extractor = OpenAIExtractor(
        "gpt-5.6-luna",
        Strategy.SINGLE,
        client=client,
        prompt_version="v4",
        retriever=Retriever(MockEmbedding(embed_dim=8), top_k=2, chunk_tokens=128),
    )
    spend: list[float] = []

    out = extractor.predict_all({"d1": TEXT}, on_usage=lambda u: spend.append(u.cost_usd))["d1"]

    (call,) = responses.calls
    assert "<contract_excerpts>" in call["input"][1]["content"]
    assert extractor.name.endswith("-v4-retrieved")
    assert extractor.config()["context"] == "retrieved"
    assert len(spend) == 3  # query embeddings, contract embeddings, the LLM call
    assert out.usage.cost_usd > 0
    assert out.usage.embedding_tokens > 0
    assert out.usage.input_tokens == 1000  # only the LLM call; embeddings counted separately
