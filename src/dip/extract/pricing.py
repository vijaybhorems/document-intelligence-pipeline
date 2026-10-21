"""Token prices, used for cost tracking and the budget guard (SPEC §19).

Source: https://developers.openai.com/api/docs/pricing (Standard tier), checked
2026-10-20. Prices change: re-check before trusting a cost report, and update
``PRICES_AS_OF`` when you do.
"""

from dataclasses import dataclass

PRICES_AS_OF = "2026-10-20"


@dataclass(frozen=True)
class Price:
    """USD per 1M tokens."""

    input: float
    cached_input: float
    output: float  # includes reasoning tokens


PRICES: dict[str, Price] = {
    "gpt-5.6-luna": Price(0.20, 0.02, 1.20),
    "gpt-5.6-terra": Price(2.00, 0.20, 12.00),
    "gpt-5.6-sol": Price(4.00, 0.40, 20.00),
    "gpt-5.5": Price(5.00, 0.50, 30.00),
    "gpt-5.4": Price(2.50, 0.25, 15.00),
    "gpt-5.4-mini": Price(0.75, 0.075, 4.50),
    "gpt-5.4-nano": Price(0.20, 0.02, 1.25),
    "gpt-5-mini": Price(0.25, 0.025, 2.00),
    "gpt-5-nano": Price(0.05, 0.005, 0.40),
    "gpt-4.1": Price(2.00, 0.50, 8.00),
    "gpt-4.1-mini": Price(0.40, 0.10, 1.60),
    "text-embedding-3-small": Price(0.02, 0.0, 0.0),
}


class UnknownModelPriceError(KeyError):
    pass


def price_of(model: str) -> Price:
    if model not in PRICES:
        raise UnknownModelPriceError(
            f"no price for {model!r}; add it to dip.extract.pricing.PRICES before running it"
        )
    return PRICES[model]


def cost_usd(model: str, input_tokens: int, cached_tokens: int, output_tokens: int) -> float:
    """``input_tokens`` includes the cached ones, as the API reports it."""
    p = price_of(model)
    uncached = input_tokens - cached_tokens
    return (uncached * p.input + cached_tokens * p.cached_input + output_tokens * p.output) / 1e6


# Cloud Run services, request-based billing, us-central1, from the Cloud Billing
# Catalog API (service 152E-C115-5142), 2026-10-20: $0.000024 per vCPU-second and
# $0.0000025 per GiB-second. The Docling worker is sized at 4 vCPU / 8 GiB (SPEC §6.5).
CLOUD_RUN_VCPU_SECOND = 0.000024
CLOUD_RUN_GIB_SECOND = 0.0000025
WORKER_VCPU = 4
WORKER_GIB = 8
WORKER_USD_PER_SECOND = WORKER_VCPU * CLOUD_RUN_VCPU_SECOND + WORKER_GIB * CLOUD_RUN_GIB_SECOND


def compute_usd(seconds: float) -> float:
    """Parsing time priced as Cloud Run worker time. Measured locally, so an estimate."""
    return seconds * WORKER_USD_PER_SECOND
