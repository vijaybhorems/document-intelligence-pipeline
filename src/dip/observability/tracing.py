"""OpenTelemetry tracing for LLM calls (SPEC §11).

Off unless ``DIP_OTEL_ENDPOINT`` is set. Locally that's Phoenix
(``http://localhost:6006/v1/traces``, see docker/compose.yaml). Deployed, it's Arize
(``https://otlp.arize.com/v1/traces``) with ``DIP_OTEL_HEADERS`` from Secret Manager.
OpenInference instruments the OpenAI SDK, so every API call becomes a span with its
prompt, response, token counts and latency. The extractor adds one parent span per
contract.

Spans include prompt text, which here means contract text. That's fine for a
local Phoenix; set ``DIP_TRACE_CONTENT=false`` before exporting real customer
documents anywhere else.
"""

import os
from typing import TYPE_CHECKING

from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter

if TYPE_CHECKING:
    from dip.config import Settings

_provider: TracerProvider | None = None


def parse_headers(raw: str) -> dict[str, str]:
    """``"a=1,b=x=y"`` -> ``{"a": "1", "b": "x=y"}``. Splits on the first ``=`` only:
    Arize space IDs are base64 and can end in ``=``."""
    pairs = (item.split("=", 1) for item in raw.split(",") if item.strip())
    return {key.strip(): value.strip() for key, value in pairs}


def start_tracing(settings: "Settings") -> bool:
    """Configure tracing from settings. True if spans will be exported."""
    headers = (
        parse_headers(settings.otel_headers.get_secret_value()) if settings.otel_headers else None
    )
    return (
        configure_tracing(settings.otel_endpoint, settings.trace_content, headers=headers)
        is not None
    )


def configure_tracing(
    endpoint: str | None,
    trace_content: bool = True,
    exporter: SpanExporter | None = None,
    headers: dict[str, str] | None = None,
    project: str = "document-intelligence-pipeline",
) -> TracerProvider | None:
    """Install a tracer provider and instrument the OpenAI SDK. No-op without an endpoint."""
    global _provider
    if endpoint is None and exporter is None:
        return None
    if not trace_content:
        os.environ["OPENINFERENCE_HIDE_INPUTS"] = "true"
        os.environ["OPENINFERENCE_HIDE_OUTPUTS"] = "true"
    provider = TracerProvider(
        resource=Resource.create({"service.name": "dip", "openinference.project.name": project})
    )
    provider.add_span_processor(
        BatchSpanProcessor(exporter or OTLPSpanExporter(endpoint=endpoint, headers=headers))
    )
    trace.set_tracer_provider(provider)
    OpenAIInstrumentor().instrument(tracer_provider=provider)
    _provider = provider
    return provider


def shutdown_tracing() -> None:
    """Flush pending spans. Call before the process exits."""
    global _provider
    if _provider is not None:
        _provider.force_flush()
        OpenAIInstrumentor().uninstrument()
        _provider.shutdown()
        _provider = None
