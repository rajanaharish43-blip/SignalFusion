import urllib.request
import json
import time
import random

# The SignalFusion webhook endpoint
WEBHOOK_URL = "http://localhost:8000/alerts/wazuh"

# A sequence of Wazuh alerts representing a brute force attack followed by a successful login
wazuh_alerts = [
    {
        "timestamp": "2024-03-20T10:15:00.000+0000",
        "rule": {
            "level": 5,
            "description": "sshd: Attempt to login using a non-existent user",
            "id": "5710",
            "mitre": {"tactic": ["Credential Access"], "technique": ["Brute Force"]}
        },
        "agent": {"ip": "192.168.1.10", "name": "server-01"},
        "data": {"srcip": "203.0.113.42", "dstuser": "admin"}
    },
    {
        "timestamp": "2024-03-20T10:15:03.000+0000",
        "rule": {
            "level": 5,
            "description": "sshd: Attempt to login using a non-existent user",
            "id": "5710",
            "mitre": {"tactic": ["Credential Access"], "technique": ["Brute Force"]}
        },
        "agent": {"ip": "192.168.1.10", "name": "server-01"},
        "data": {"srcip": "203.0.113.42", "dstuser": "admin"}
    },
    {
        "timestamp": "2024-03-20T10:15:15.000+0000",
        "rule": {
            "level": 3,
            "description": "sshd: authentication success.",
            "id": "5715",
            "mitre": {"tactic": ["Initial Access"], "technique": ["Valid Accounts"]}
        },
        "agent": {"ip": "192.168.1.10", "name": "server-01"},
        "data": {"srcip": "203.0.113.42", "dstuser": "admin"}
    }
]

def send_alert(alert):
    print(f"[*] Sending Wazuh Alert: {alert['rule']['description']}")
    data = json.dumps(alert).encode('utf-8')
    req = urllib.request.Request(WEBHOOK_URL, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        response = urllib.request.urlopen(req)
        print(f"[+] Response: {response.read().decode('utf-8')}\n")
    except Exception as e:
        print(f"[-] Error: {e}\n")

if __name__ == "__main__":
    print("Starting Wazuh Webhook Simulator...")
    print("This script pushes real Wazuh JSON payloads to the SignalFusion collector.\n")
    
    for alert in wazuh_alerts:
        send_alert(alert)
        time.sleep(1.5) # Simulate slight delay between events
        
    print("Done! Check your SignalFusion dashboard to see the fused incident.")
