import React from 'react';
import './StatusPanel.css';

const StatusPanel = ({ data }) => {
  const getStressColor = (stress) => {
    if (stress < 0.3) return '#4caf50';
    if (stress < 0.7) return '#ff9800';
    return '#f44336';
  };

  const getUtilizationColor = (utilization) => {
    if (utilization < 50) return '#2196f3';
    if (utilization < 80) return '#ff9800';
    return '#f44336';
  };

  return (
    <div className="status-panel">
      <h2>System Status</h2>
      
      <div className="status-grid">
        <div className="status-card">
          <h3>Power Supply</h3>
          <div className="metric-value">
            {data.total_supply.toFixed(1)} units
          </div>
        </div>
        
        <div className="status-card">
          <h3>Total Demand</h3>
          <div className="metric-value">
            {data.total_demand.toFixed(1)} units
          </div>
        </div>
        
        <div className="status-card">
          <h3>Allocated</h3>
          <div className="metric-value">
            {data.total_allocated.toFixed(1)} units
          </div>
        </div>
        
        <div className="status-card">
          <h3>Utilization</h3>
          <div className="metric-value" style={{ color: getUtilizationColor(data.utilization) }}>
            {data.utilization.toFixed(1)}%
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${Math.min(data.utilization, 100)}%`,
                backgroundColor: getUtilizationColor(data.utilization)
              }}
            />
          </div>
        </div>
        
        <div className="status-card">
          <h3>System Stress</h3>
          <div className="metric-value" style={{ color: getStressColor(data.system_stress) }}>
            {(data.system_stress * 100).toFixed(1)}%
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${data.system_stress * 100}%`,
                backgroundColor: getStressColor(data.system_stress)
              }}
            />
          </div>
        </div>
        
        <div className="status-card">
          <h3>Total Penalty</h3>
          <div className="metric-value">
            {data.total_penalty.toFixed(1)}
          </div>
        </div>
      </div>
      
      <div className="agent-summary">
        <h3>Agent Status Summary</h3>
        <div className="agent-counts">
          <div className="agent-count critical">
            <span className="count">{data.agents.filter(a => a.status === 'critical').length}</span>
            <span className="label">Critical</span>
          </div>
          <div className="agent-count stable">
            <span className="count">{data.agents.filter(a => a.status === 'stable').length}</span>
            <span className="label">Stable</span>
          </div>
          <div className="agent-count failing">
            <span className="count">{data.agents.filter(a => a.status === 'failing').length}</span>
            <span className="label">Failing</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPanel;
