
import uuid

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import model_validator
from app.database import Base


# API request model

class RealUserIncidentRequest(BaseModel):
    category: str = Field(
        default="login_issue",
        pattern="^login_issue$"
    )
    email: str = Field(
        min_length=1,
        max_length=254
    )
    incident_id: str = Field(
        min_length=1,
        max_length=36
    )

class TraceRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=100)


# Stores each uploaded incident
class Incident(Base):
    __tablename__ = "incidents"

    incident_id = Column(
        String(36), primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String(20), nullable=True)
    analysis_json = Column(Text, nullable=True)
    ai_report = Column(Text, nullable=True)

    logs = relationship(
        "IncidentLog", back_populates="incident",
        cascade="all, delete-orphan"
    )
    messages = relationship(
        "IncidentMessage", back_populates="incident",
        cascade="all, delete-orphan"
    )


# Stores individual log lines
class IncidentLog(Base):
    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        String(36), ForeignKey("incidents.incident_id"),
        nullable=False, index=True
    )
    line_number = Column(Integer, nullable=False)
    log_line = Column(Text, nullable=False)

    incident = relationship("Incident", back_populates="logs")


# Stores interactive investigation conversations
class IncidentMessage(Base):
    __tablename__ = "incident_messages"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(
        String(36), ForeignKey("incidents.incident_id"),
        nullable=False, index=True
    )
    role = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="messages")


class FollowUpRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
