import React, { useState } from 'react';
import './ControlPanel.css';

const ControlPanel = ({ isRunning, onStart, onStop, onReset, onTriggerDisaster }) => {
  const [selectedDisaster, setSelectedDisaster] = useState('earthquake');
  const [disasterImpact, setDisasterImpact] = useState(0.3);

  const handleTriggerDisaster = () => {
    onTriggerDisaster(selectedDisaster, disasterImpact);
  };

  return (
    <div className="control-panel">
      <h2>Simulation Control</h2>
      
      <div className="simulation-controls">
        <div className="button-group">
          {!isRunning ? (
            <button className="btn btn-start" onClick={onStart}>
              ▶ Start Simulation
            </button>
          ) : (
            <button className="btn btn-stop" onClick={onStop}>
              ⏸ Stop Simulation
            </button>
          )}
          
          <button className="btn btn-reset" onClick={onReset}>
            ↺ Reset
          </button>
        </div>
        
        <div className="status-indicator">
          <span className={`status ${isRunning ? 'running' : 'stopped'}`}>
            {isRunning ? '● Running' : '○ Stopped'}
          </span>
        </div>
      </div>
      
      <div className="disaster-controls">
        <h3>Disaster Events</h3>
        
        <div className="disaster-selector">
          <label htmlFor="disaster-type">Disaster Type:</label>
          <select 
            id="disaster-type"
            value={selectedDisaster}
            onChange={(e) => setSelectedDisaster(e.target.value)}
          >
            <option value="earthquake">Earthquake</option>
            <option value="flood">Flood</option>
            <option value="power_failure">Power Failure</option>
            <option value="storm">Storm</option>
          </select>
        </div>
        
        <div className="impact-slider">
          <label htmlFor="impact-level">Impact Level: {disasterImpact.toFixed(2)}</label>
          <input
            id="impact-level"
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={disasterImpact}
            onChange={(e) => setDisasterImpact(parseFloat(e.target.value))}
          />
        </div>
        
        <button className="btn btn-disaster" onClick={handleTriggerDisaster}>
          ⚡ Trigger Disaster
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;
