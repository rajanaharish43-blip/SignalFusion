from datetime import timedelta
import uuid
import models

def calculate_correlation_score(alert: models.Alert, incident: models.Incident) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    
    # Check against all alerts in the incident
    incident_alerts = incident.alerts
    
    # Simple strategy: Compare new alert with the most recent alert in the incident or aggregate characteristics
    
    if incident.source_ip and alert.source_ip and incident.source_ip == alert.source_ip:
        score += 30
        reasons.append("Same source IP")
        
    if incident.target_ip and alert.destination_ip and incident.target_ip == alert.destination_ip:
        score += 20
        reasons.append("Same destination target")
        
    # Check if usernames match any in the incident
    usernames = set(a.username for a in incident_alerts if a.username)
    if alert.username and alert.username in usernames:
        score += 15
        reasons.append("Same username")
        
    # Time proximity (within 15 minutes of the last seen alert)
    if incident.last_seen and alert.timestamp:
        time_diff = abs((alert.timestamp - incident.last_seen).total_seconds())
        if time_diff <= 900: # 15 minutes
            score += 20
            reasons.append("Close timestamp (within 15 mins)")
            
    # Same attack category
    stages = set(a.attack_stage for a in incident_alerts if a.attack_stage)
    if alert.attack_stage and alert.attack_stage in stages:
        score += 15
        reasons.append("Related attack stage")

    return score, reasons

def process_alert(db, alert: models.Alert):
    # Find recent OPEN incidents (e.g. last 1 hour)
    from datetime import datetime
    time_threshold = datetime.utcnow() - timedelta(hours=1)
    recent_incidents = db.query(models.Incident).filter(
        models.Incident.status == "OPEN",
        models.Incident.last_seen >= time_threshold
    ).all()
    
    best_score = -1
    best_incident = None
    best_reasons = []
    
    for inc in recent_incidents:
        score, reasons = calculate_correlation_score(alert, inc)
        if score > best_score:
            best_score = score
            best_incident = inc
            best_reasons = reasons
            
    if best_score >= 50 and best_incident:
        # Fuse alert into existing incident
        alert.incident_id = best_incident.id
        
        # Update incident metadata
        if alert.timestamp > best_incident.last_seen:
            best_incident.last_seen = alert.timestamp
        if alert.timestamp < best_incident.first_seen:
            best_incident.first_seen = alert.timestamp
            
        return best_incident, best_score, best_reasons
    else:
        # Create new incident
        return None, 0, []
