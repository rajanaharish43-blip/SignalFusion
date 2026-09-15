def calculate_incident_priority(alerts: list) -> str:
    if not alerts:
        return "LOW"
    
    max_severity = max(a.severity for a in alerts)
    unique_stages = set(a.attack_stage for a in alerts if a.attack_stage)
    
    # Simple logic
    if max_severity >= 7 or len(unique_stages) >= 3:
        return "CRITICAL"
    elif max_severity >= 5 or len(unique_stages) == 2:
        return "HIGH"
    elif max_severity >= 3 or len(alerts) >= 5:
        return "MEDIUM"
    else:
        return "LOW"

def map_mitre_techniques(alerts: list) -> list:
    techniques = set()
    for a in alerts:
        if a.event_type == "login_failed":
            techniques.add("T1110 (Brute Force)")
        elif "cloud_auth" in a.event_type:
            techniques.add("T1078 (Valid Accounts)")
        elif a.event_type == "process_execution" and "powershell" in (a.description or "").lower():
            techniques.add("T1059.001 (PowerShell)")
        elif "network" in a.event_type:
            techniques.add("T1043 (Commonly Used Port)")
    return list(techniques)
