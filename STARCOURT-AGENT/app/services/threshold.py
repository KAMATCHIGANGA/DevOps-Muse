



#✅ implement SRE rule: calculate the HTTP error rate and alert if it exceeds 5%.

import re


def calculate_error_rate(log_lines: list[str]) -> dict:
    total_requests = 0
    failed_requests = 0

    for line in log_lines:
        match = re.search(r"(?:^|\s)status=(\d{3})(?=\s|$)", line)

        if not match:
            continue

        status_code = int(match.group(1))
        total_requests += 1

        # Count every HTTP 5xx status as a failure.
        if 500 <= status_code <= 599:
            failed_requests += 1

    error_rate = (
        round((failed_requests / total_requests) * 100, 2)
        if total_requests
        else 0.0
    )

    threshold_exceeded = error_rate >= 0.1

    return {
        "total_requests": total_requests,
        "failed_requests": failed_requests,
        "error_rate": error_rate,
        "alert": threshold_exceeded,
        "message": (
            "Error rate exceeds 5% threshold"
            if threshold_exceeded
            else "Error rate is within threshold"
        ),
    }


#✅second SRE rule: flag requests whose response time exceeds 2 seconds.

def find_slow_requests(log_lines: list[str]) -> dict:
    slow_requests = []

    for line in log_lines:
        if "rt=" not in line:
            continue

        try:
            response_time = float(
                line.split("rt=")[1].split()[0].rstrip("s")
            )
        except (ValueError, IndexError):
            continue

        if response_time > 2:
            slow_requests.append({
                "log": line,
                "response_time_seconds": response_time
            })

    return {
        "threshold_seconds": 2,
        "slow_request_count": len(slow_requests),
        "alert": len(slow_requests) > 0,
        "slow_requests": slow_requests
    }

def classify_severity(error_rate: float, slow_request_count: int) -> str:
    if error_rate >= 20:
        return "CRITICAL"
    elif error_rate >= 5 or slow_request_count > 0:
        return "WARNING"
    else:
        return "HEALTHY"



