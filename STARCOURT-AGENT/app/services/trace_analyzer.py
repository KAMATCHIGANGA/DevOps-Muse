
import re
import json
from collections import defaultdict


def extract_request_id(log_line: str) -> str | None:
    try:
        record = json.loads(log_line)
    except (json.JSONDecodeError, TypeError):
        record = None

    # Handle structured JSON log records
    if isinstance(record, dict):
        message = record.get("@message", "")

        # Nginx @message is a key-value string
        if isinstance(message, str):
            match = re.search(
                r'\brequest_id=([a-fA-F0-9]+)\b',
                message
            )
            if match:
                return match.group(1)

        # App logs may contain the linked Nginx request ID
        elif isinstance(message, dict):
            request_id = message.get("nginx_request_id")
            if request_id:
                return request_id

    # Handle raw key-value logs
    match = re.search(
        r'\brequest_id=([a-fA-F0-9]+)\b',
        log_line
    )

    return match.group(1) if match else None


def find_trace_logs(
    log_lines: list[str],
    trace_id: str | None = None,
    request_id: str | None = None,
) -> dict:
    matching_logs = []
    entered_username = None
    matched_request_ids = set()

    for line in log_lines:
        try:
            parsed = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            parsed = None

        # Uploaded file may be one complete JSON array in a single DB row.
        if isinstance(parsed, list):
            records = parsed
        elif isinstance(parsed, dict):
            records = [parsed]
        else:
            records = [None]

        for record in records:
            if isinstance(record, dict):
                message = record.get("@message", {})
                if isinstance(message, str):
                    log_request_match = re.search(
                        r'\brequest_id=([a-fA-F0-9]+)\b',
                        message
                    )
                    log_request_id = (
                        log_request_match.group(1)
                        if log_request_match else None
                    )
                    log_trace_id = None
                elif isinstance(message, dict):
                    log_request_id = message.get("nginx_request_id")
                    log_trace_id = message.get("trace_id")
                else:
                    log_request_id = None
                    log_trace_id = None
            else:
                message = {}
                log_request_id = extract_request_id(line)
                log_trace_id = None

            if log_request_id:
                matched_request_ids.add(log_request_id)

            if (
                (request_id and log_request_id == request_id)
                or (trace_id and log_trace_id == trace_id)
            ):
                matching_logs.append(json.dumps(record))

                if isinstance(message, dict) and message.get("request_name"):
                    entered_username = message["request_name"]

    return {
        "trace_id": trace_id,
        "request_id": request_id,
        "total_matching_logs": len(matching_logs),
        "logs": matching_logs,
        "entered_username": entered_username,
        "matched_request_ids": sorted(matched_request_ids),
    }


def analyze_services(log_lines: list[str]) -> dict:
    services = {}

    for line in log_lines:
        service_match = re.search(
            r"(?:^|\s)service=([^\s]+)", line
        )

        if not service_match:
            continue

        service = service_match.group(1)

        if service not in services:
            services[service] = {
                "total_events": 0,
                "failed_events": 0,
                "slow_events": 0,
                "error_rate_percent": 0.0,
                "errors": [],
            }

        stats = services[service]
        stats["total_events"] += 1

        status_match = re.search(
            r"(?:^|\s)status=(\d{3})(?=\s|$)", line
        )

        is_http_failure = (
            status_match is not None
            and 500 <= int(status_match.group(1)) <= 599
        )

        error_match = re.search(
            r"(?:^|\s)error=([^\s]+)", line
        )

        if is_http_failure or error_match:
            stats["failed_events"] += 1
            stats["errors"].append(
                error_match.group(1)
                if error_match
                else f"HTTP {status_match.group(1)}"
            )

        latency_match = re.search(
            r"(?:^|\s)rt=(\d+(?:\.\d+)?)(s?)(?=\s|$)", line
        )

        if latency_match and float(latency_match.group(1)) > 2:
            stats["slow_events"] += 1

    for stats in services.values():
        if stats["total_events"]:
            stats["error_rate_percent"] = round(
                stats["failed_events"]
                / stats["total_events"] * 100,
                2,
            )

    return services