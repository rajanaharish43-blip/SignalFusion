import React, { useEffect, useState } from 'react';
import { fetchIncident } from '../api';
import { ArrowLeft, ShieldAlert, Cpu, Activity, Shield, MapPin, Globe } from 'lucide-react';

export default function IncidentView({ incidentId, onBack }) {
  const [incident, setIncident] = useState(null);

  useEffect(() => {
    fetchIncident(incidentId).then(setIncident);
  }, [incidentId]);

  if (!incident) return <div className="p-8 text-center text-slate-400">Loading incident...</div>;

  return (
    <div className="space-y-6 animate-in fade-in">
      <button onClick={onBack} className="flex items-center gap-2 text-blue-400 hover:text-blue-300">
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-3">
            {incident.title}
            <span className={`px-3 py-1 rounded text-sm font-bold uppercase ${
              incident.risk_level === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/50' : 'bg-orange-500/20 text-orange-400'
            }`}>
              {incident.risk_level} RISK ({incident.risk_score})
            </span>
          </h2>
          <div className="mt-2 text-slate-400 flex gap-6">
            <span>ID: {incident.incident_id}</span>
            <span>Created: {new Date(incident.created_at).toLocaleString()}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded text-sm">Investigate</button>
          <button className="bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded text-sm">Isolate Host</button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column: Story & Entities */}
        <div className="col-span-2 space-y-6">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-400" /> Attack Story (Correlation)
            </h3>
            <div className="space-y-4">
              {incident.events.map((ev, i) => (
                <div key={ev.event_id} className="relative pl-6 pb-4 border-l-2 border-slate-700 last:border-0 last:pb-0">
                  <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full ${
                    ev.severity === 'critical' ? 'bg-red-500' : 
                    ev.severity === 'high' ? 'bg-orange-500' : 'bg-slate-500'
                  }`} />
                  <div className="bg-slate-900/50 p-4 rounded border border-slate-700/50">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <div className="font-bold text-lg">{ev.event_type.replace(/_/g, ' ')}</div>
                        <div className="text-sm text-slate-400 mt-1">{ev.description}</div>
                      </div>
                      <div className="text-xs text-slate-400 whitespace-nowrap ml-4">{new Date(ev.timestamp).toLocaleTimeString()}</div>
                    </div>
                    <div className="text-sm text-slate-300">
                      {ev.user && <span className="mr-4">User: <strong className="text-white">{ev.user}</strong></span>}
                      {ev.device && <span className="mr-4">Host: <strong className="text-white">{ev.device}</strong></span>}
                      {ev.source_ip && <span>IP: <strong className="text-white">{ev.source_ip}</strong></span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-purple-400" /> AI Analysis
            </h3>
            <p className="text-slate-300 leading-relaxed italic bg-slate-900/50 p-4 rounded border border-slate-700/50">
              "{incident.explanation}"
            </p>
          </div>
        </div>

        {/* Right Column: Context & Intel */}
        <div className="col-span-1 space-y-6">
          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-red-400" /> MITRE ATT&CK
            </h3>
            <div className="space-y-2">
              {incident.mitre_tactics.length === 0 ? (
                <div className="text-slate-500 text-sm">No techniques mapped.</div>
              ) : (
                incident.mitre_tactics.map(t => (
                  <div key={t} className="bg-slate-900 p-2 text-sm rounded border border-slate-700 text-slate-300">
                    {t}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5 text-green-400" /> Threat Intel (Mock)
            </h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span className="text-slate-400">External IP</span>
                <span className="font-mono text-red-400">185.15.22.4</span>
              </div>
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span className="text-slate-400">Reputation</span>
                <span className="text-red-400 font-bold">Malicious (C2)</span>
              </div>
              <div className="flex justify-between border-b border-slate-700 pb-2">
                <span className="text-slate-400">Location</span>
                <span>St. Petersburg, RU</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
