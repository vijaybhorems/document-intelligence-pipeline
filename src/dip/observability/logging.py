"""Structured JSON logs (SPEC §11): one line per event, with job_id and stage bound in.

Cloud Logging parses JSON lines on stdout automatically (``severity`` and ``message``).
Never log document text or keys.
"""

import logging
import sys
from typing import TextIO

import structlog


def _cloud_logging_fields(_: object, method: str, event: dict[str, object]) -> dict[str, object]:
    event["severity"] = method.upper()
    event["message"] = event.pop("event", "")
    return event


def configure_logging(level: str = "INFO", json: bool = True, stream: TextIO | None = None) -> None:
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.format_exc_info,
    ]
    if json:
        processors += [_cloud_logging_fields, structlog.processors.JSONRenderer()]
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
        # stdout by default (Cloud Run reads it); stderr for the MCP stdio transport, whose
        # stdout is the protocol channel.
        logger_factory=structlog.PrintLoggerFactory(stream or sys.stdout),
        cache_logger_on_first_use=True,
    )
