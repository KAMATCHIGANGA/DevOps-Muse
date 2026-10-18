
import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import FollowUpRequest, IncidentMessage
from app.database import get_db
from app.models import Incident, TraceRequest
from app.services.ai_analyzer import analyze_incident
from app.services.trace_analyzer import find_trace_logs, analyze_services
from app.services.threshold import (
    calculate_error_rate,
    find_slow_requests,
    classify_severity,
)
from app.models import RealUserIncidentRequest
from app.services.rds_connection import get_registered_username


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/investigate", tags=["Investigation"])



@router.post("/{incident_id}/trace")
def investigate_trace(
    incident_id: str,
    request: TraceRequest,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    log_lines = [
        record.log_line
        for record in sorted(
            incident.logs,
            key=lambda item: item.line_number
        )
    ]

    matching_result = find_trace_logs(
        log_lines,
        request_id=request.request_id,
    )

    matching_logs = matching_result["logs"]

    if not matching_logs:
        raise HTTPException(
            status_code=404,
            detail=f"No logs found for request ID: {request.request_id}"
        )

    error_analysis = calculate_error_rate(log_lines)
    slow_analysis = find_slow_requests(log_lines)
    service_analysis = analyze_services(matching_logs)

    severity = classify_severity(
        error_rate=error_analysis["error_rate"],
        slow_request_count=slow_analysis["slow_request_count"],
    )

    evidence = f"""
Incident ID: {incident_id}
Request ID: {request.request_id}
Incident severity: {severity}

Matching logs:
{chr(10).join(matching_logs)}

Overall error-rate analysis:
{error_analysis}

Slow-request analysis:
{slow_analysis}

Service-level analysis:
{service_analysis}

Investigate repeated HTTP 502 responses across endpoints.
Explain what the evidence supports, distinguish likely causes
from confirmed causes, and recommend actionable checks.
"""

    logger.info(
        "Starting investigation for incident_id=%s request_id=%s",
        incident_id,
        request.request_id,
    )

    start_time = time.perf_counter()

    try:
        ai_report = analyze_incident(evidence)
    except Exception:
        logger.exception(
            "AI investigation failed for incident_id=%s",
            incident_id,
        )
        raise HTTPException(
            status_code=503,
            detail="AI investigation is temporarily unavailable. Please retry."
        )

    investigation_time = round(time.perf_counter() - start_time, 2)

    incident.severity = severity
    incident.ai_report = ai_report
    incident.analysis_json = json.dumps({
        "error_analysis": error_analysis,
        "response_time_analysis": slow_analysis,
        "service_analysis": service_analysis,
        "request_id": request.request_id,
        "investigation_time_seconds": investigation_time,
    })

    db.commit()

    logger.info(
        "Investigation completed for incident_id=%s in %.2f seconds",
        incident_id,
        investigation_time,
    )

    return {
        "incident_id": incident_id,
        "request_id": request.request_id,
        "total_matching_logs": len(matching_logs),
        "matching_logs": matching_logs,
        "error_analysis": error_analysis,
        "response_time_analysis": slow_analysis,
        "service_analysis": service_analysis,
        "severity": severity,
        "ai_investigation": ai_report,
        "investigation_time_seconds": investigation_time,
    }


@router.post("/real-user-incident")
def investigate_real_user_incident(
    request: RealUserIncidentRequest,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, request.incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    log_lines = [
        record.log_line
        for record in sorted(
            incident.logs,
            key=lambda item: item.line_number,
        )
    ]

    entered_username = None

    for line in log_lines:
        try:
            parsed = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            continue

        records = parsed if isinstance(parsed, list) else [parsed]

        for record in records:
            if not isinstance(record, dict):
                continue

            message = record.get("@message", {})
            if isinstance(message, dict):
                if message.get("message") == "Invalid credentials":
                    entered_username = message.get("request_name")
                    break

        if entered_username:
            break

    if not entered_username:
        raise HTTPException(
            status_code=404,
            detail="Login failure or entered username not found in incident logs",
        )

    registered_username = get_registered_username(request.email)

    if not registered_username:
        finding = "The supplied email was not found in the user database."
        suggested_action = "Verify the registered email address."
        username_match = False
    else:
        username_match = (
            entered_username.casefold()
            == registered_username.casefold()
        )

        if username_match:
            finding = "The entered username matches the registered username."
            suggested_action = (
                "Investigate password validity and other authentication conditions."
            )
        else:
            finding = "The entered username does not match the registered username."
            suggested_action = (
                f"Ask the user to sign in using the registered username: "
                f"{registered_username}."
            )

    return {
        "incident_id": request.incident_id,
        "category": request.category,
        "email": request.email,
        "entered_username": entered_username,
        "registered_username": registered_username,
        "username_match": username_match,
        "finding": finding,
        "suggested_action": suggested_action,
    }
