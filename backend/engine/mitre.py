from typing import List
from models.alert import NormalizedEvent

MITRE_MAPPING = {
    "POWERSHELL_EXECUTION": "T1059.001 - PowerShell",
    "UNUSUAL_LOGIN": "T1078 - Valid Accounts",
    "FAILED_LOGIN": "T1110 - Brute Force",
    "MALICIOUS_IP_CONNECTION": "T1071 - Application Layer Protocol",
    "DATA_EXFILTRATION": "T1041 - Exfiltration Over C2 Channel"
}

def map_to_mitre(events: List[NormalizedEvent]) -> List[str]:
    tactics = set()
    for event in events:
        tactic = MITRE_MAPPING.get(event.event_type)
        if tactic:
            tactics.add(tactic)
    return list(tactics)
