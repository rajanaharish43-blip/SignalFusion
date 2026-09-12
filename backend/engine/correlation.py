import uuid
from typing import List
from datetime import datetime
from models.alert import NormalizedEvent
from models.incident import Incident
from engine.risk import calculate_incident_score
from engine.mitre import map_to_mitre

def generate_ai_explanation(events: List[NormalizedEvent], risk_level: str) -> str:
    types = [e.event_type.replace('_', ' ').lower() for e in events]
    summary = ", ".join(types[:-1]) + (" and " if len(types) > 1 else "") + types[-1] if types else "unknown events"
    
    if risk_level == "CRITICAL":
        return f"This incident is CRITICAL because it involves a sequence of {summary}. These signals are highly correlated and strongly indicate a possible account compromise followed by execution and command & control."
    elif risk_level == "HIGH":
        return f"This incident is HIGH risk. We detected {summary} originating from the same entity."
    else:
        return f"This is a {risk_level} priority incident. It consists of {summary} which are likely benign or false positives, but warrant a quick review."

def correlate_events(events: List[NormalizedEvent]) -> List[Incident]:
    # For a lightweight hackathon version, we assume events passed in together are a "batch"
    # to be analyzed. We will group them by user or device if they share them.
    # In a real system, this would run continuously over a sliding time window.
    
    if not events:
        return []
        
    users = set(e.user for e in events if e.user)
    primary_user = list(users)[0] if users else "unknown"
    
    devices = set(e.device for e in events if e.device)
    primary_device = list(devices)[0] if devices else "unknown"
    
    score, level = calculate_incident_score(events)
    tactics = map_to_mitre(events)
    
    # Create an explanation
    explanation = generate_ai_explanation(events, level)
    
    incident = Incident(
        incident_id=f"INC-{uuid.uuid4().hex[:6].upper()}",
        title=f"Suspicious Activity: {primary_user}",
        created_at=datetime.now().isoformat(),
        status="open",
        risk_score=score,
        risk_level=level,
        events=events,
        primary_user=primary_user,
        primary_device=primary_device,
        mitre_tactics=tactics,
        explanation=explanation
    )
    
    # We just return one incident for the batch simulation
    return [incident]
