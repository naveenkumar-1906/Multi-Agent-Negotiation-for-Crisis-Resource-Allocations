# Autonomous Multi-Agent Negotiation for Crisis Resource Allocation

A real-time simulation system for decentralized power resource allocation during disaster scenarios.

## System Overview

This system simulates a city-wide power grid crisis where multiple utility agents negotiate for limited power resources. The system uses rule-based negotiation to prioritize critical services and ensure fair distribution.

## Architecture

- **Backend**: Python with FastAPI and WebSocket for real-time updates
- **Frontend**: React with real-time charts and dashboard
- **Simulation Engine**: Custom multi-agent negotiation system

## Features

- 4 types of agents with different priorities and demands
- Real-time resource allocation with fluctuating supply
- Multi-round negotiation mechanism
- Live visualization of allocation decisions
- Disaster event simulation

## Quick Start

1. Install dependencies:
   ```bash
   cd backend && pip install -r requirements.txt
   cd ../frontend && npm install
   ```

2. Start the backend:
   ```bash
   cd backend && python main.py
   ```

3. Start the frontend:
   ```bash
   cd frontend && npm start
   ```

4. Open http://localhost:3000 to view the dashboard

## Agents

1. **Hospital** (Priority 1): Critical life support systems
2. **Emergency Services** (Priority 2): Fire, police, ambulance services
3. **Water Supply** (Priority 3): Water treatment and distribution
4. **Residential/Commercial** (Priority 4): General power consumers

## Success Criteria

- Stable allocation under changing conditions
- Reduced service failure compared to naive allocation
- Clear prioritization of critical services
- Dynamic adaptation to disasters
