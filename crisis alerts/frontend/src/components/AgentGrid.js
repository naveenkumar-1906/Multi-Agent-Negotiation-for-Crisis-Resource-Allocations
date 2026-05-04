import React from 'react';
import './AgentGrid.css';

const AgentGrid = ({ agents }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'critical':
        return '#f44336';
      case 'stable':
        return '#4caf50';
      case 'failing':
        return '#ff9800';
      default:
        return '#666';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'hospital':
        return '🏥';
      case 'emergency_services':
        return '🚑';
      case 'water_supply':
        return '💧';
      case 'residential_commercial':
        return '🏢';
      default:
        return '📊';
    }
  };

  const getAllocationRatio = (allocated, demand) => {
    if (demand === 0) return 100;
    return (allocated / demand) * 100;
  };

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 1:
        return 'Critical';
      case 2:
        return 'High';
      case 3:
        return 'Medium';
      case 4:
        return 'Low';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="agent-grid">
      <h2>Agent Status Details</h2>
      
      <div className="agents-container">
        {agents.map((agent) => {
          const allocationRatio = getAllocationRatio(agent.allocated, agent.demand);
          
          return (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <div className="agent-icon">
                  {getTypeIcon(agent.type)}
                </div>
                <div className="agent-info">
                  <h3 className="agent-name">{agent.name}</h3>
                  <span className={`agent-status ${agent.status}`}>
                    {agent.status.toUpperCase()}
                  </span>
                </div>
                <div className="agent-priority">
                  <span className="priority-badge priority-{agent.priority}">
                    P{agent.priority}
                  </span>
                </div>
              </div>
              
              <div className="agent-metrics">
                <div className="metric-row">
                  <span className="metric-label">Demand:</span>
                  <span className="metric-value">{agent.demand.toFixed(1)}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Allocated:</span>
                  <span className="metric-value">{agent.allocated.toFixed(1)}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Min Required:</span>
                  <span className="metric-value">{agent.min_required.toFixed(1)}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Allocation Ratio:</span>
                  <span className="metric-value" style={{ 
                    color: allocationRatio >= 80 ? '#4caf50' : 
                           allocationRatio >= 50 ? '#ff9800' : '#f44336'
                  }}>
                    {allocationRatio.toFixed(1)}%
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Penalty:</span>
                  <span className="metric-value">{agent.penalty.toFixed(1)}</span>
                </div>
              </div>
              
              <div className="allocation-bar">
                <div className="bar-background">
                  <div 
                    className="bar-allocated" 
                    style={{ 
                      width: `${Math.min(allocationRatio, 100)}%`,
                      backgroundColor: getStatusColor(agent.status)
                    }}
                  />
                  <div 
                    className="bar-minimum" 
                    style={{ 
                      width: `${(agent.min_required / agent.demand) * 100}%`,
                      backgroundColor: '#ff9800'
                    }}
                  />
                </div>
                <div className="bar-labels">
                  <span>0%</span>
                  <span>Min</span>
                  <span>Allocated</span>
                  <span>100%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AgentGrid;
