from pydantic import BaseModel
from typing import Optional, Dict, Any

class RawEvent(BaseModel):
    # This represents varying incoming data, typically would be unstructured or varied
    source_type: str
    data: Dict[str, Any]

class NormalizedEvent(BaseModel):
    event_id: str
    timestamp: str
    user: Optional[str] = None
    device: Optional[str] = None
    source_ip: Optional[str] = None
    event_type: str
    severity: str  # low, medium, high, critical
    metadata: Dict[str, Any] = {}
