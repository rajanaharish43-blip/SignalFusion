from typing import List
from models.alert import NormalizedEvent

# Base scores for different event types
BASE_SCORES = {
    "FAILED_LOGIN": 10,
    "SUCCESSFUL_LOGIN": 0,
    "UNUSUAL_LOGIN": 25,
    "POWERSHELL_EXECUTION": 30,
    "PRIVILEGE_ESCALATION": 40,
    "MALICIOUS_IP_CONNECTION": 50,
    "DATA_EXFILTRATION": 60
}

def calculate_incident_score(events: List[NormalizedEvent]) -> tuple[int, str]:
    total_score = sum(BASE_SCORES.get(event.event_type, 5) for event in events)
    
    # Contextual weighting (mock example)
    users_involved = set(e.user for e in events if e.user)
    if "admin" in [u.lower() for u in users_involved]:
        total_score += 20
        
    if total_score <= 30:
        level = "LOW"
    elif total_score <= 60:
        level = "MEDIUM"
    elif total_score <= 80:
        level = "HIGH"
    else:
        level = "CRITICAL"
        
    return min(total_score, 100), level
