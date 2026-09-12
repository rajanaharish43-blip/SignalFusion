from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import database
import models
import schemas
import data_generator
import normalizer
import fusion
import incident_engine
from typing import List
import uuid
import datetime
import asyncio

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/simulate/{scenario}")
async def simulate_attack(scenario: str, db: Session = Depends(database.get_db)):
    raw_events = data_generator.generate_scenario(scenario)
    
    created_alerts = []
    updated_incidents = set()
    
    for event in raw_events:
        alert_data = normalizer.normalize_event(event)
        db_alert = models.Alert(**alert_data.dict(exclude={"raw_data"}), raw_data=alert_data.raw_data)
        
        # Process fusion
        incident, score, reasons = fusion.process_alert(db, db_alert)
        
        if incident:
            db_alert.incident_id = incident.id
            db.add(db_alert)
            db.commit() # Need to commit to update the relationship
            db.refresh(db_alert)
            updated_incidents.add(incident)
            
            # Update explanation
            if score >= 70:
                incident.confidence = max(incident.confidence or 0, float(score))
                explanation = "Fused because: " + ", ".join(reasons)
                incident.explanation = explanation
        else:
            db.add(db_alert)
            db.commit()
            db.refresh(db_alert)
            
            # Create new incident
            new_incident = models.Incident(
                incident_id=f"INC-{uuid.uuid4().hex[:6].upper()}",
                title=f"Suspicious Activity: {db_alert.event_type}",
                severity="LOW",
                confidence=float(100),
                first_seen=db_alert.timestamp,
                last_seen=db_alert.timestamp,
                source_ip=db_alert.source_ip,
                target_ip=db_alert.destination_ip,
                explanation="Initial alert"
            )
            db.add(new_incident)
            db.commit()
            db.refresh(new_incident)
            
            db_alert.incident_id = new_incident.id
            db.commit()
            updated_incidents.add(new_incident)
    
    # Recalculate priority and MITRE for updated incidents
    for inc in updated_incidents:
        db.refresh(inc)
        inc.severity = incident_engine.calculate_incident_priority(inc.alerts)
        inc.mitre_techniques = incident_engine.map_mitre_techniques(inc.alerts)
        
        # Update title based on severity or alerts
        if inc.severity in ["CRITICAL", "HIGH"] and len(inc.alerts) > 1:
            if any(a.event_type == "process_execution" for a in inc.alerts):
                inc.title = "Possible Server Compromise"
            else:
                inc.title = "Suspicious Authentication Sequence"

        db.commit()

    await manager.broadcast("UPDATE")
    return {"message": f"Simulated {len(raw_events)} events"}

@router.post("/alerts/wazuh")
async def ingest_wazuh_alert(payload: dict, db: Session = Depends(database.get_db)):
    # Standardize to common alert format
    alert_data = normalizer.normalize_event(payload)
    db_alert = models.Alert(**alert_data.dict(exclude={"raw_data"}), raw_data=alert_data.raw_data)
    
    # Process fusion
    incident, score, reasons = fusion.process_alert(db, db_alert)
    
    if incident:
        db_alert.incident_id = incident.id
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        # Update incident metadata
        if score >= 70:
            incident.confidence = max(incident.confidence or 0, float(score))
            incident.explanation = "Fused because: " + ", ".join(reasons)
            
        incident.severity = incident_engine.calculate_incident_priority(incident.alerts)
        incident.mitre_techniques = incident_engine.map_mitre_techniques(incident.alerts)
        db.commit()
        
    else:
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        
        # Create new incident
        new_incident = models.Incident(
            incident_id=f"INC-{uuid.uuid4().hex[:6].upper()}",
            title=f"Wazuh Alert: {db_alert.event_type}",
            severity=incident_engine.calculate_incident_priority([db_alert]),
            confidence=float(100),
            first_seen=db_alert.timestamp,
            last_seen=db_alert.timestamp,
            source_ip=db_alert.source_ip,
            target_ip=db_alert.destination_ip,
            explanation="Initial Wazuh alert",
            mitre_techniques=incident_engine.map_mitre_techniques([db_alert])
        )
        db.add(new_incident)
        db.commit()
        db.refresh(new_incident)
        
        db_alert.incident_id = new_incident.id
        db.commit()
        
    await manager.broadcast("UPDATE")
    return {"message": "Wazuh alert processed"}

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(database.get_db)):
    alerts = db.query(models.Alert).count()
    incidents = db.query(models.Incident).filter(models.Incident.status == "OPEN").count()
    critical = db.query(models.Incident).filter(
        models.Incident.status == "OPEN", 
        models.Incident.severity == "CRITICAL"
    ).count()
    resolved = db.query(models.Incident).filter(models.Incident.status == "RESOLVED").count()
    
    return {
        "alerts": alerts,
        "incidents": incidents,
        "critical": critical,
        "resolved": resolved
    }

@router.get("/incidents")
def get_incidents(db: Session = Depends(database.get_db)):
    incidents = db.query(models.Incident).order_by(models.Incident.last_seen.desc()).all()
    result = []
    for inc in incidents:
        result.append({
            "incident_id": inc.incident_id,
            "title": inc.title,
            "risk_level": inc.severity,
            "risk_score": int(inc.confidence),
            "created_at": inc.first_seen.isoformat(),
            "explanation": inc.explanation
        })
    return result

@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(database.get_db)):
    inc = db.query(models.Incident).filter(models.Incident.incident_id == incident_id).first()
    if not inc:
        return {"error": "Not found"}
        
    alerts = []
    for a in sorted(inc.alerts, key=lambda x: x.timestamp):
        alerts.append({
            "event_id": str(a.id),
            "timestamp": a.timestamp.isoformat(),
            "description": a.description,
            "event_type": a.event_type,
            "severity": "high" if a.severity >= 7 else ("medium" if a.severity >= 3 else "low"),
            "user": a.username,
            "device": a.destination_ip,
            "source_ip": a.source_ip
        })
        
    return {
        "incident_id": inc.incident_id,
        "title": inc.title,
        "risk_level": inc.severity,
        "risk_score": int(inc.confidence),
        "created_at": inc.first_seen.isoformat(),
        "source": inc.source_ip,
        "target": inc.target_ip,
        "events": alerts,
        "mitre_tactics": inc.mitre_techniques,
        "explanation": inc.explanation
    }

@router.get("/alerts")
def get_alerts(db: Session = Depends(database.get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.timestamp.desc()).limit(100).all()
    return alerts
