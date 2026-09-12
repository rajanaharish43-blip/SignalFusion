import uuid
from typing import List, Dict, Any
from models.alert import RawEvent, NormalizedEvent

def normalize_event(raw: RawEvent) -> NormalizedEvent:
    event_id = str(uuid.uuid4())
    data = raw.data
    source = raw.source_type
    
    # Defaults
    timestamp = ""
    user = None
    device = None
    source_ip = None
    event_type = "UNKNOWN"
    severity = "low"
    
    if source == "AuthLog":
        timestamp = data.get("time")
        user = data.get("username")
        device = data.get("workstation")
        source_ip = data.get("ip")
        
        if data.get("action") == "LOGIN_FAILED":
            event_type = "FAILED_LOGIN"
            severity = "low"
        elif data.get("action") == "LOGIN_SUCCESS":
            event_type = "SUCCESSFUL_LOGIN"
            severity = "low"
            
    elif source == "CloudAuth":
        timestamp = data.get("eventTime")
        user = data.get("userId")
        source_ip = data.get("ipAddress")
        
        if data.get("status") == "SUCCESS":
            event_type = "UNUSUAL_LOGIN"
            severity = "medium"
            
    elif source == "EndpointLog":
        timestamp = data.get("ts")
        user = data.get("user")
        device = data.get("host")
        
        if data.get("process") == "powershell.exe":
            event_type = "POWERSHELL_EXECUTION"
            severity = "high"
            
    elif source == "FirewallLog":
        timestamp = data.get("timestamp")
        source_ip = data.get("src_ip")
        
        if data.get("dst_ip") == "185.15.22.4": # Mock malicious IP check
            event_type = "MALICIOUS_IP_CONNECTION"
            severity = "critical"
            
    return NormalizedEvent(
        event_id=event_id,
        timestamp=timestamp or "unknown",
        user=user,
        device=device,
        source_ip=source_ip,
        event_type=event_type,
        severity=severity,
        metadata=data
    )

def normalize_events(raw_events: List[RawEvent]) -> List[NormalizedEvent]:
    return [normalize_event(r) for r in raw_events]
