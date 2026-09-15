import uuid
from datetime import datetime, timedelta
import random

# Scenario 1: Account Compromise
def generate_account_compromise(start_time: datetime):
    events = []
    user = "alice"
    device = "PC-104"
    malicious_ip = "185.15.22.4"
    
    # Failed login
    events.append({
        "source_type": "AuthLog",
        "data": {
            "time": (start_time).isoformat(),
            "username": user,
            "workstation": device,
            "action": "LOGIN_FAILED",
            "ip": "10.10.2.15"
        }
    })
    
    # Successful login from unusual location
    events.append({
        "source_type": "CloudAuth",
        "data": {
            "eventTime": (start_time + timedelta(minutes=2)).isoformat(),
            "userId": user,
            "location": "Russia",
            "ipAddress": malicious_ip,
            "status": "SUCCESS"
        }
    })
    
    # PowerShell execution
    events.append({
        "source_type": "EndpointLog",
        "data": {
            "ts": (start_time + timedelta(minutes=5)).isoformat(),
            "user": user,
            "host": device,
            "process": "powershell.exe",
            "args": "-ExecutionPolicy Bypass -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AEYAcgBvAG0AQgBhAHMAZQA2ADQAUwB0AHIAaQBuAGcAKAAiAEgA..."
        }
    })
    
    # Malicious IP Connection
    events.append({
        "source_type": "FirewallLog",
        "data": {
            "timestamp": (start_time + timedelta(minutes=7)).isoformat(),
            "src_ip": "10.10.2.15",
            "dst_ip": malicious_ip,
            "action": "ALLOW",
            "port": 443
        }
    })
    
    return events

# Scenario 2: False Positive
def generate_false_positive(start_time: datetime):
    events = []
    user = "bob"
    device = "PC-201"
    
    events.append({
        "source_type": "AuthLog",
        "data": {
            "time": (start_time).isoformat(),
            "username": user,
            "workstation": device,
            "action": "LOGIN_FAILED",
            "ip": "10.10.5.22"
        }
    })
    
    events.append({
        "source_type": "AuthLog",
        "data": {
            "time": (start_time + timedelta(seconds=15)).isoformat(),
            "username": user,
            "workstation": device,
            "action": "LOGIN_SUCCESS",
            "ip": "10.10.5.22"
        }
    })
    return events

def generate_scenario(scenario_name: str):
    now = datetime.now()
    if scenario_name == "account_compromise":
        return generate_account_compromise(now)
    elif scenario_name == "false_positive":
        return generate_false_positive(now)
    # Could add more like 'malware', 'exfiltration' later
    return []
