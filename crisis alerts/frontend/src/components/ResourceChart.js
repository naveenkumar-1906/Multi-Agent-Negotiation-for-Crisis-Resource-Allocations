import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './ResourceChart.css';

const ResourceChart = ({ data }) => {
  // Prepare data for bar chart
  const allocationData = data.agents.map(agent => ({
    name: agent.name.length > 15 ? agent.name.substring(0, 15) + '...' : agent.name,
    demand: agent.demand,
    allocated: agent.allocated,
    minRequired: agent.min_required,
    type: agent.type
  }));

  // Prepare data for pie chart
  const pieData = data.agents.map(agent => ({
    name: agent.name.length > 20 ? agent.name.substring(0, 20) + '...' : agent.name,
    value: agent.allocated,
    type: agent.type
  }));

  // Color mapping for agent types
  const typeColors = {
    'hospital': '#f44336',
    'emergency_services': '#ff9800', 
    'water_supply': '#2196f3',
    'residential_commercial': '#4caf50'
  };

  // Custom tooltip for bar chart
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{label}</p>
          <p className="tooltip-demand">Demand: {payload[0].payload.demand.toFixed(1)}</p>
          <p className="tooltip-allocated">Allocated: {payload[0].payload.allocated.toFixed(1)}</p>
          <p className="tooltip-min">Min Required: {payload[0].payload.minRequired.toFixed(1)}</p>
          <p className="tooltip-ratio">
            Allocation Ratio: {((payload[0].payload.allocated / payload[0].payload.demand) * 100).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="resource-chart">
      <h2>Resource Allocation Visualization</h2>
      
      <div className="chart-grid">
        <div className="chart-container">
          <h3>Demand vs Allocation</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={allocationData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                height={100}
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="demand" fill="#e0e0e0" name="Demand" />
              <Bar dataKey="allocated" fill="#667eea" name="Allocated" />
              <Bar dataKey="minRequired" fill="#ff9800" name="Min Required" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="chart-container">
          <h3>Allocation Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={typeColors[entry.type] || '#8884d8'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="chart-legend">
        <h4>Agent Types</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: typeColors.hospital }}></span>
            <span>Hospital</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: typeColors.emergency_services }}></span>
            <span>Emergency Services</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: typeColors.water_supply }}></span>
            <span>Water Supply</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: typeColors.residential_commercial }}></span>
            <span>Residential/Commercial</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResourceChart;
