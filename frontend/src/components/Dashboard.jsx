import React, { useEffect, useState } from 'react';
import { fetchStats, fetchIncidents, simulateAttack } from '../api';
import { AlertCircle, AlertTriangle, ShieldCheck, Activity, Zap } from 'lucide-react';

export default function Dashboard({ onSelectIncident }) {
  const [stats, setStats] = useState({ alerts: 0, incidents: 0, critical: 0, resolved: 0 });
  const [incidents, setIncidents] = useState([]);

  const loadData = async () => {
    const s = await fetchStats();
    setStats(s);
    const i = await fetchIncidents();
    setIncidents(i);
  };

  useEffect(() => {
    loadData();
    
    // Connect to WebSocket using current host to work in Codespaces
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${wsProtocol}//${window.location.host}/ws/dashboard`);
    
    ws.onmessage = (event) => {
      if (event.data === 'UPDATE') {
        loadData();
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleSimulate = async (scenario) => {
    await simulateAttack(scenario);
    await loadData();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">SOC Dashboard</h2>
        <div className="flex gap-2">
          <button 
            onClick={() => handleSimulate('account_compromise')}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded flex items-center gap-2 text-sm"
          >
            <Zap className="w-4 h-4" /> Simulate APT Attack
          </button>
          <button 
            onClick={() => handleSimulate('false_positive')}
            className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded flex items-center gap-2 text-sm"
          >
            <Zap className="w-4 h-4" /> Simulate False Positive
          </button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex flex-col items-center">
          <Activity className="text-blue-400 mb-2 w-8 h-8" />
          <div className="text-3xl font-bold">{stats.alerts}</div>
          <div className="text-slate-400 text-sm uppercase tracking-wide">Raw Alerts</div>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex flex-col items-center">
          <AlertTriangle className="text-yellow-400 mb-2 w-8 h-8" />
          <div className="text-3xl font-bold">{stats.incidents}</div>
          <div className="text-slate-400 text-sm uppercase tracking-wide">Correlated Incidents</div>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg border border-red-900/50 flex flex-col items-center">
          <AlertCircle className="text-red-500 mb-2 w-8 h-8" />
          <div className="text-3xl font-bold text-red-500">{stats.critical}</div>
          <div className="text-red-400/80 text-sm uppercase tracking-wide">Critical</div>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex flex-col items-center">
          <ShieldCheck className="text-green-400 mb-2 w-8 h-8" />
          <div className="text-3xl font-bold">{stats.resolved}</div>
          <div className="text-slate-400 text-sm uppercase tracking-wide">Resolved</div>
        </div>
      </div>

      {/* Incidents List */}
      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h3 className="text-lg font-semibold">Active Incidents</h3>
        </div>
        <div className="divide-y divide-slate-700">
          {incidents.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No active incidents. Run a simulation.</div>
          ) : (
            incidents.map(inc => (
              <div 
                key={inc.incident_id} 
                onClick={() => onSelectIncident(inc.incident_id)}
                className="p-4 hover:bg-slate-700/50 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div className="flex items-center gap-4">
                  {inc.risk_level === 'CRITICAL' && <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />}
                  {inc.risk_level === 'HIGH' && <div className="w-3 h-3 rounded-full bg-orange-500" />}
                  {inc.risk_level === 'MEDIUM' && <div className="w-3 h-3 rounded-full bg-yellow-500" />}
                  {inc.risk_level === 'LOW' && <div className="w-3 h-3 rounded-full bg-blue-500" />}
                  
                  <div>
                    <div className="font-semibold text-lg">{inc.title}</div>
                    <div className="text-sm text-slate-400">
                      ID: {inc.incident_id} • Score: {inc.risk_score} • {new Date(inc.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                    inc.risk_level === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 
                    inc.risk_level === 'HIGH' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/50' :
                    'bg-slate-700 text-slate-300'
                  }`}>
                    {inc.risk_level}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
