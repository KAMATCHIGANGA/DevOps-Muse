
import json

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident, IncidentLog
from app.services.threshold import calculate_error_rate, find_slow_requests

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/upload")
async def upload_log(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.endswith((".log", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only .log and .txt files are supported"
        )

    max_file_size = 5 * 1024 * 1024
    content = await file.read(max_file_size + 1)

    if len(content) > max_file_size:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the 5 MB limit"
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    log_text = content.decode("utf-8", errors="replace")
    log_lines = log_text.splitlines()

    analysis = calculate_error_rate(log_lines)
    slow_analysis = find_slow_requests(log_lines)

    incident = Incident(
        filename=file.filename,
        severity="CRITICAL" if analysis.get("error_rate", 0) >= 20
        else "WARNING" if analysis.get("alert") or slow_analysis.get("alert")
        else "HEALTHY",
        analysis_json=json.dumps({
            "error_analysis": analysis,
            "response_time_analysis": slow_analysis
        })
    )

    try:
        db.add(incident)
        db.flush()

        db.add_all([
            IncidentLog(
                incident_id=incident.incident_id,
                line_number=index,
                log_line=line
            )
            for index, line in enumerate(log_lines, start=1)
        ])

        db.commit()
        db.refresh(incident)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save incident to database"
        )

    return {
        "incident_id": incident.incident_id,
        "filename": incident.filename,
        "total_lines": len(log_lines),
        "severity": incident.severity,
        "analysis": analysis,
        "response_time_analysis": slow_analysis
    }


@router.delete("/{incident_id}/clear")
def clear_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    db.delete(incident)
    db.commit()

    return {
        "message": "Incident and its associated data deleted",
        "incident_id": incident_id
    }


@router.get("/history")
def get_incident_history(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .all()
    )

    return [
        {
            "incident_id": incident.incident_id,
            "filename": incident.filename,
            "created_at": incident.created_at,
            "severity": incident.severity,
            "has_ai_report": bool(incident.ai_report),
        }
        for incident in incidents
    ]


@router.get("/{incident_id}")
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return {
        "incident_id": incident.incident_id,
        "filename": incident.filename,
        "created_at": incident.created_at,
        "severity": incident.severity,
        "logs": [
            {
                "line_number": log.line_number,
                "log_line": log.log_line
            }
            for log in sorted(incident.logs, key=lambda item: item.line_number)
        ],
        "analysis": json.loads(incident.analysis_json) if incident.analysis_json else {},
        "ai_report": incident.ai_report
    }
