import json    
import os
from pathlib import Path
from threading import Lock
import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from flask import request


TELEMETRY_DIR = Path.home() / "starcourt" / "telemetry"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

TRACE_FILE = TELEMETRY_DIR / "traces.jsonl"


class JsonlSpanExporter(SpanExporter):
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = Lock()

    def export(self, spans):
        try:
            with self.lock:
                with self.file_path.open("a", encoding="utf-8") as file:
                    for span in spans:
                        record = {
    "trace_id": format(span.context.trace_id, "032x"),
    "span_id": format(span.context.span_id, "016x"),
    "parent_span_id": (
        format(span.parent.span_id, "016x")
        if span.parent else None
    ),
    "name": span.name,
    "service_name": span.resource.attributes.get("service.name"),
    "start_time_unix_nano": span.start_time,
    "end_time_unix_nano": span.end_time,
    "duration_ms": (
        span.end_time - span.start_time
    ) / 1_000_000,
    "status": span.status.status_code.name,
    "attributes": dict(span.attributes),
    "events": [
        {
            "name": event.name,
            "attributes": dict(event.attributes),
            "timestamp": event.timestamp,
        }
        for event in span.events
    ],
}
                        file.write(json.dumps(record, default=str) + "\n")
            return SpanExportResult.SUCCESS
        except Exception:
            return SpanExportResult.FAILURE

    def shutdown(self):
        pass


provider = TracerProvider(
    resource=Resource.create({"service.name": "starcourt"})
)
provider.add_span_processor(
    BatchSpanProcessor(JsonlSpanExporter(TRACE_FILE))
)
trace.set_tracer_provider(provider)


def instrument_app(app):
    FlaskInstrumentor().instrument_app(app)

    @app.after_request
    def add_request_id_to_trace(response):
        span = trace.get_current_span()

        if span and span.is_recording():
            request_id = request.headers.get("X-Request-ID")
            if request_id:
                span.set_attribute("nginx.request_id", request_id)

        return response

    @app.after_request
    def log_request_response(response):
        logging.getLogger("starcourt").info(
            "Request completed",
            extra={
                "request_name": request.headers.get("X-Request-ID"),
                "http_status_code": response.status_code,
                "http_method": request.method,
                "http_path": request.path,
            },
        )
        return response

