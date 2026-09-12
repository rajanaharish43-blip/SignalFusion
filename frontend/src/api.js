const API_BASE = 'http://localhost:8000';

export async function simulateAttack(scenario) {
    const res = await fetch(`${API_BASE}/simulate/${scenario}`, {
        method: 'POST'
    });
    return res.json();
}

export async function fetchStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return res.json();
}

export async function fetchIncidents() {
    const res = await fetch(`${API_BASE}/incidents`);
    return res.json();
}

export async function fetchIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}`);
    return res.json();
}

export async function fetchAlerts() {
    const res = await fetch(`${API_BASE}/alerts`);
    return res.json();
}
