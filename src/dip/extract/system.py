"""The interface every extraction system implements: baselines now, LLM pipelines from Phase 3."""

from collections.abc import Callable
from typing import Any, Protocol

from pydantic import BaseModel

from dip.schema.domain import ContractFields


class Usage(BaseModel):
    """Tokens, cost and time for one contract (or summed over a run)."""

    calls: int = 0
    input_tokens: int = 0  # includes cached
    cached_tokens: int = 0
    output_tokens: int = 0  # includes reasoning
    reasoning_tokens: int = 0
    embedding_tokens: int = 0  # retrieval (D3); never mixed into input_tokens
    cost_usd: float = 0.0
    latency_s: float = 0.0

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            calls=self.calls + other.calls,
            input_tokens=self.input_tokens + other.input_tokens,
            cached_tokens=self.cached_tokens + other.cached_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            reasoning_tokens=self.reasoning_tokens + other.reasoning_tokens,
            embedding_tokens=self.embedding_tokens + other.embedding_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            latency_s=self.latency_s + other.latency_s,
        )


class SystemOutput(BaseModel):
    fields: ContractFields
    usage: Usage = Usage()
    issues: list[str] = []


class System(Protocol):
    @property
    def name(self) -> str: ...

    def config(self) -> dict[str, Any]:
        """Everything needed to reproduce this system's predictions."""
        ...

    def predict_all(
        self,
        texts: dict[str, str],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, SystemOutput]:
        """Predict every contract; may return fewer once ``max_cost_usd`` has been spent.

        ``on_usage`` is called after every paid API call, for crash-safe spend tracking.
        """
        ...
