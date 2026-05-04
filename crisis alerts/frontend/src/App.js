import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import ControlPanel from './components/ControlPanel';
import AgentGrid from './components/AgentGrid';
import ResourceChart from './components/ResourceChart';
import StatusPanel from './components/StatusPanel';

function App() {
  const [simulationData, setSimulationData] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('Connected to server');
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'initial_state':
        case 'simulation_update':
          setSimulationData(message.data);
          break;
        case 'simulation_reset':
          setSimulationData(message.data);
          setHistoryData(null);
          break;
        case 'disaster_triggered':
          console.log('Disaster triggered:', message.data);
          break;
        default:
          console.log('Unknown message type:', message.type);
      }
    };
    
    ws.onclose = () => {
      console.log('Disconnected from server');
      setIsConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    // Fetch initial data
    fetchInitialData();
    
    return () => {
      ws.close();
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setSimulationData(data);
      
      const historyResponse = await fetch('/api/history');
      const history = await historyResponse.json();
      setHistoryData(history);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const startSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/start', { method: 'POST' });
      const result = await response.json();
      setIsRunning(true);
      console.log(result.message);
    } catch (error) {
      console.error('Error starting simulation:', error);
    }
  };

  const stopSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/stop', { method: 'POST' });
      const result = await response.json();
      setIsRunning(false);
      console.log(result.message);
    } catch (error) {
      console.error('Error stopping simulation:', error);
    }
  };

  const resetSimulation = async () => {
    try {
      const response = await fetch('/api/simulation/reset', { method: 'POST' });
      const result = await response.json();
      setIsRunning(false);
      console.log(result.message);
    } catch (error) {
      console.error('Error resetting simulation:', error);
    }
  };

  const triggerDisaster = async (disasterType, impact) => {
    try {
      const response = await fetch('/api/disaster/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ type: disasterType, impact }),
      });
      const result = await response.json();
      console.log(result.message);
    } catch (error) {
      console.error('Error triggering disaster:', error);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Crisis Resource Allocation System</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>
      </header>
      
      <main className="main-content">
        <div className="control-section">
          <ControlPanel
            isRunning={isRunning}
            onStart={startSimulation}
            onStop={stopSimulation}
            onReset={resetSimulation}
            onTriggerDisaster={triggerDisaster}
          />
        </div>
        
        {simulationData && (
          <>
            <div className="status-section">
              <StatusPanel data={simulationData} />
            </div>
            
            <div className="chart-section">
              <ResourceChart data={simulationData} />
            </div>
            
            <div className="agents-section">
              <AgentGrid agents={simulationData.agents} />
            </div>
          </>
        )}
        
        {!simulationData && (
          <div className="loading">
            <p>Loading simulation data...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
