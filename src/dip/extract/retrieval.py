"""Retrieval: send only the parts of a contract relevant to the fields (SPEC §7.4, decision D3).

Each contract is split into ~384-token chunks (LlamaIndex ``SentenceSplitter``)
and embedded. Each field has one query: its definition plus phrasing variants.
The top-k chunks per field are unioned and sent in document order. This cuts
input tokens; the risk is recall on rare clauses that sit in unexpected places,
which is what D3 measures.

Query embeddings are the same for every contract, so they're computed once.
Embedding spend is reported through ``on_usage`` like any other paid call.

Sentences are split with a regex rather than LlamaIndex's default NLTK punkt
tokenizer. Punkt loads data files bundled in the wheel, and NLTK's path security
refuses to open them when the installer hardlinked them (uv does by default on
Linux, so CI and Docker builds broke). The regex needs no data files.
"""

import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import tiktoken
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import QueryBundle, TextNode

from dip.extract import prompts
from dip.extract.pricing import cost_usd
from dip.extract.system import Usage
from dip.schema.registry import FieldSpec

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_TOKENS = 384
CHUNK_OVERLAP = 48
TOP_K = 3
_GAP = "\n[...]\n"
# Split after sentence-ending punctuation that's followed by whitespace. Lookarounds
# keep every character, so the pieces join back to the exact original text.
_SENTENCE_END = re.compile(r"(?<=[.;:!?])(?=\s)")


def split_sentences(text: str) -> list[str]:
    return [piece for piece in _SENTENCE_END.split(text) if piece]


@dataclass(frozen=True)
class Excerpts:
    text: str
    chunks_kept: int
    chunks_total: int
    usage: Usage


def field_query(spec: FieldSpec, version: str) -> str:
    notes = (
        prompts._field_notes().get(spec.name) if "variants" in prompts.FEATURES[version] else None
    )
    variants = " ".join(notes.variants) if notes else ""
    return f"{spec.name.replace('_', ' ')}: {spec.definition} {variants}".strip()


class Retriever:
    def __init__(
        self,
        embed_model: BaseEmbedding,
        top_k: int = TOP_K,
        chunk_tokens: int = CHUNK_TOKENS,
        embedding_model_name: str = EMBEDDING_MODEL,
    ) -> None:
        self.embed_model = embed_model
        self.top_k = top_k
        self.splitter = SentenceSplitter(
            chunk_size=chunk_tokens,
            chunk_overlap=CHUNK_OVERLAP,
            chunking_tokenizer_fn=split_sentences,
        )
        self.model_name = embedding_model_name
        self._encoder = tiktoken.get_encoding("o200k_base")
        self._queries: dict[str, list[float]] = {}

    def _cost(self, texts: Sequence[str]) -> Usage:
        tokens = sum(len(self._encoder.encode(t, disallowed_special=())) for t in texts)
        return Usage(
            calls=1, embedding_tokens=tokens, cost_usd=cost_usd(self.model_name, tokens, 0, 0)
        )

    def prepare_queries(
        self, specs: Sequence[FieldSpec], version: str, on_usage: Callable[[Usage], None] | None
    ) -> None:
        """Embed one query per field, once per run."""
        missing = [s for s in specs if s.name not in self._queries]
        if not missing:
            return
        texts = [field_query(s, version) for s in missing]
        vectors = self.embed_model.get_text_embedding_batch(texts)
        self._queries.update({s.name: v for s, v in zip(missing, vectors, strict=True)})
        if on_usage:
            on_usage(self._cost(texts))

    def excerpts(self, text: str, specs: Sequence[FieldSpec], version: str) -> Excerpts:
        nodes = [
            n
            for n in self.splitter.get_nodes_from_documents([Document(text=text)])
            if isinstance(n, TextNode)
        ]
        index = VectorStoreIndex(nodes, embed_model=self.embed_model, show_progress=False)
        retriever = index.as_retriever(similarity_top_k=self.top_k)
        keep: set[str] = set()
        for spec in specs:
            query = QueryBundle(field_query(spec, version), embedding=self._queries[spec.name])
            keep.update(hit.node.node_id for hit in retriever.retrieve(query))
        kept = [n for n in nodes if n.node_id in keep and n.start_char_idx is not None]
        return Excerpts(
            text=_GAP.join(text[a:b] for a, b in _merge_ranges(kept, text)),
            chunks_kept=len(kept),
            chunks_total=len(nodes),
            usage=self._cost([n.get_content() for n in nodes]),
        )


def _merge_ranges(nodes: Sequence[TextNode], text: str) -> list[tuple[int, int]]:
    """Kept chunks as character ranges, merged where they overlap or only whitespace is between."""
    ranges = sorted((n.start_char_idx or 0, n.end_char_idx or 0) for n in nodes)
    merged: list[tuple[int, int]] = []
    for start, end in ranges:
        if merged and (start <= merged[-1][1] or not text[merged[-1][1] : start].strip()):
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def openai_retriever(api_key: str) -> Retriever:
    from llama_index.embeddings.openai import OpenAIEmbedding

    return Retriever(OpenAIEmbedding(model=EMBEDDING_MODEL, api_key=api_key))
