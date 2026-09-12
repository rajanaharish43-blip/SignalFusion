# Wazuh Integration Setup

SignalFusion integrates with Wazuh directly using Wazuh's native **Custom Integrations** capability. By configuring an integration in Wazuh, every time Wazuh triggers a security alert, it will instantly push the alert payload to SignalFusion's webhook endpoint for normalization and fusion.

## Prerequisites

1. SignalFusion backend must be running and accessible over the network from the Wazuh Manager.
2. Wazuh Manager must be version 4.x or higher.

## Configuration Steps

### 1. Edit the Wazuh Manager Configuration
On your Wazuh Manager server, open the main configuration file, typically located at `/var/ossec/etc/ossec.conf`.

### 2. Add the SignalFusion Integration
Scroll to the `<ossec_config>` section and add the following `<integration>` block. Be sure to replace `http://<SIGNALFUSION_IP>:8000/alerts/wazuh` with the actual IP address or hostname where your SignalFusion backend is running.

```xml
  <integration>
    <name>custom-webhook</name>
    <hook_url>http://<SIGNALFUSION_IP>:8000/alerts/wazuh</hook_url>
    <level>5</level>
    <alert_format>json</alert_format>
  </integration>
```

**Configuration Details:**
- `<name>`: Setting this to `custom-webhook` tells Wazuh to just POST the raw JSON.
- `<hook_url>`: The SignalFusion collector endpoint.
- `<level>`: (Optional) The minimum severity level (1-15) of alerts to send to SignalFusion. We recommend setting this to 5 or higher to avoid fusing low-level noise.
- `<alert_format>`: Must be `json`.

### 3. Restart the Wazuh Manager
To apply the changes, restart the Wazuh Manager service:

```bash
systemctl restart wazuh-manager
```

## How to Test
You can generate a test alert on an endpoint running the Wazuh Agent (for example, by attempting several failed SSH logins).

In the SignalFusion React Dashboard, you will automatically see the alert ingested, correlated, and if it matches an ongoing incident, it will be fused!

## Advanced Filtering (Optional)
If you only want to send specific rule IDs or groups to SignalFusion, you can use `<rule_id>` or `<group>` tags in the integration block:

```xml
  <integration>
    <name>custom-webhook</name>
    <hook_url>http://<SIGNALFUSION_IP>:8000/alerts/wazuh</hook_url>
    <group>authentication_failed,syscheck</group>
    <alert_format>json</alert_format>
  </integration>
```
