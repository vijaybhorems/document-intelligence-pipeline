"""Structured JSON logs (SPEC §11): one line per event, with job_id and stage bound in.

Cloud Logging parses JSON lines on stdout automatically (``severity`` and ``message``).
Never log document text or keys.
"""

import logging
import sys

import structlog


def _cloud_logging_fields(_: object, method: str, event: dict[str, object]) -> dict[str, object]:
    event["severity"] = method.upper()
    event["message"] = event.pop("event", "")
    return event


def configure_logging(level: str = "INFO", json: bool = True) -> None:
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
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )
