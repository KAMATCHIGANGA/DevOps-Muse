
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
