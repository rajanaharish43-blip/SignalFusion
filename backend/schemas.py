from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class AlertBase(BaseModel):
    source: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    username: Optional[str] = None
    event_type: str
    severity: int
    timestamp: datetime
    description: Optional[str] = None
    attack_stage: Optional[str] = None
    raw_data: Optional[Any] = None

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    incident_id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True

class IncidentBase(BaseModel):
    incident_id: str
    title: str
    severity: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    status: str
    mitre_techniques: List[str] = []
    explanation: Optional[str] = None
    source_ip: Optional[str] = None
    target_ip: Optional[str] = None

class IncidentCreate(IncidentBase):
    pass

class Incident(IncidentBase):
    id: int
    alerts: List[Alert] = []

    class Config:
        orm_mode = True
        from_attributes = True

class DashboardStats(BaseModel):
    alerts: int
    incidents: int
    critical: int
    resolved: int
