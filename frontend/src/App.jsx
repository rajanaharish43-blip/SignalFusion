import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import IncidentView from './components/IncidentView';
import { Activity } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

  const navigateToIncident = (id) => {
    setSelectedIncidentId(id);
    setCurrentView('incident');
  };

  const navigateToDashboard = () => {
    setSelectedIncidentId(null);
    setCurrentView('dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-50 flex flex-col">
      <header className="bg-slate-800 border-b border-slate-700 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2 cursor-pointer" onClick={navigateToDashboard}>
          <Activity className="text-blue-500 w-6 h-6" />
          <h1 className="text-xl font-bold tracking-wider">SIGNALFUSION <span className="text-sm font-normal text-slate-400">SOC</span></h1>
        </div>
        <div className="text-sm text-slate-400">
          Analyst: Admin User
        </div>
      </header>
      
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
        {currentView === 'dashboard' && (
          <Dashboard onSelectIncident={navigateToIncident} />
        )}
        {currentView === 'incident' && (
          <IncidentView 
            incidentId={selectedIncidentId} 
            onBack={navigateToDashboard} 
          />
        )}
      </main>
    </div>
  );
}

export default App;
