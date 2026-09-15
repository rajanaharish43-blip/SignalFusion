from datetime import datetime
from dateutil import parser
from backend.models import schemas

def normalize_event(event: dict) -> schemas.AlertCreate:
    source = event.get("source_type", "unknown")
    data = event.get("data", {})
    
    # Extract timestamp
    raw_time = data.get("time") or data.get("eventTime") or data.get("ts") or data.get("timestamp")
    if raw_time:
        try:
            timestamp = parser.parse(raw_time)
        except Exception:
            timestamp = datetime.utcnow()
    else:
        timestamp = datetime.utcnow()

    # Defaults
    source_ip = None
    destination_ip = None
    username = None
    event_type = "unknown_event"
    severity = 1
    description = ""
    attack_stage = "Unknown"

    if source == "AuthLog":
        source_ip = data.get("ip")
        destination_ip = data.get("workstation")
        username = data.get("username")
        action = data.get("action", "")
        event_type = action.lower()
        if "FAILED" in action:
            severity = 3
            description = f"Failed login for {username}"
            attack_stage = "Initial Access"
        else:
            severity = 1
            description = f"Successful login for {username}"
            
    elif source == "CloudAuth":
        source_ip = data.get("ipAddress")
        username = data.get("userId")
        status = data.get("status", "")
        event_type = f"cloud_auth_{status.lower()}"
        if status == "SUCCESS":
            severity = 5
            description = f"Cloud auth success from {data.get('location')}"
            attack_stage = "Privilege Escalation" # Context dependent
            
    elif source == "EndpointLog":
        username = data.get("user")
        destination_ip = data.get("host")
        process = data.get("process", "")
        event_type = "process_execution"
        if "powershell" in process.lower():
            severity = 7
            description = "Suspicious PowerShell execution"
            attack_stage = "Execution"
            
    elif source == "FirewallLog":
        source_ip = data.get("src_ip")
        destination_ip = data.get("dst_ip")
        action = data.get("action", "")
        port = data.get("port")
        event_type = f"network_{action.lower()}"
        severity = 2
        description = f"Network connection {action} on port {port}"
        attack_stage = "Command and Control" if port in [443, 80] else "Discovery"
        
    elif source == "wazuh" or "rule" in event: # Handle direct Wazuh webhook
        source = "Wazuh"
        rule = event.get("rule", {})
        agent = event.get("agent", {})
        
        # Wazuh timestamp might be at root
        raw_time = event.get("timestamp") or raw_time
        if raw_time:
            try:
                timestamp = parser.parse(raw_time)
            except Exception:
                timestamp = datetime.utcnow()
                
        severity = rule.get("level", 3)
        description = rule.get("description", "Wazuh Alert")
        event_type = f"wazuh_rule_{rule.get('id', 'unknown')}"
        
        # Wazuh provides data in various fields depending on decoder
        data_field = event.get("data", {})
        if isinstance(data_field, dict):
            source_ip = data_field.get("srcip")
            destination_ip = data_field.get("dstip") or agent.get("ip")
            username = data_field.get("srcuser") or data_field.get("dstuser")
        
        # Determine Attack Stage from MITRE tactics if available
        mitre_data = rule.get("mitre", {})
        if isinstance(mitre_data, dict) and "tactic" in mitre_data:
            tactics = mitre_data.get("tactic", [])
            if tactics:
                attack_stage = tactics[0]

    return schemas.AlertCreate(
        source=source,
        source_ip=source_ip,
        destination_ip=destination_ip,
        username=username,
        event_type=event_type,
        severity=severity,
        timestamp=timestamp,
        description=description,
        attack_stage=attack_stage,
        raw_data=event
    )
