from pydantic import BaseModel
from typing import List, Optional
from .alert import NormalizedEvent

class Incident(BaseModel):
    incident_id: str
    title: str
    created_at: str
    status: str = "open"  # open, resolved, escalated
    risk_score: int
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    events: List[NormalizedEvent]
    primary_user: Optional[str] = None
    primary_device: Optional[str] = None
    mitre_tactics: List[str] = []
    explanation: Optional[str] = None
