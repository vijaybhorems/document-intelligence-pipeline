"""OpenTelemetry tracing for LLM calls (SPEC §11).

Off unless ``DIP_OTEL_ENDPOINT`` is set. Locally that's Phoenix
(``http://localhost:6006/v1/traces``, see docker/compose.yaml); in Phase 8 the same
code exports to Arize. OpenInference instruments the OpenAI SDK, so every API
call becomes a span with its prompt, response, token counts and latency. The
extractor adds one parent span per contract.

Spans include prompt text, which here means contract text. That's fine for a
local Phoenix; set ``DIP_TRACE_CONTENT=false`` before exporting real customer
documents anywhere else.
"""

import os

from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter

_provider: TracerProvider | None = None


def configure_tracing(
    endpoint: str | None,
    trace_content: bool = True,
    exporter: SpanExporter | None = None,
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
    provider.add_span_processor(BatchSpanProcessor(exporter or OTLPSpanExporter(endpoint=endpoint)))
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
