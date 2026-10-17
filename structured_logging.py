import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from opentelemetry import trace

LOG_FILE = Path.home() / "starcourt" / "telemetry" / "logs.jsonl"


class JsonFileHandler(logging.Handler):
    def emit(self, record):
        try:
            span_context = trace.get_current_span().get_span_context()

            log_entry = {
                "timestamp": datetime.fromtimestamp(
                    record.created, timezone.utc
                ).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "request_name": getattr(record, "request_name", None),
                "submitted_username": getattr(record, "submitted_username", None),
                "nginx_request_id": getattr(record, "nginx_request_id", None),
                "trace_id": (
                    format(span_context.trace_id, "032x")
                    if span_context.is_valid
                    else None
                ),
                "span_id": (
                    format(span_context.span_id, "016x")
                    if span_context.is_valid
                    else None
                ),
            }

            if record.exc_info:
                log_entry["exception"] = self.formatException(
                    record.exc_info
                )

            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(json.dumps(log_entry) + "\n")

        except Exception:
            self.handleError(record)


def configure_logging():
    logger = logging.getLogger("starcourt")
    logger.setLevel(logging.INFO)

    if not any(
        isinstance(handler, JsonFileHandler)
        for handler in logger.handlers
    ):
        logger.addHandler(JsonFileHandler())

    return logger
