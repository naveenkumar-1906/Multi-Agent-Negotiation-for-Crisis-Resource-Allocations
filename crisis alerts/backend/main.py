from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from simulation import SimulationEngine
import json
import asyncio
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Crisis Resource Allocation System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global simulation engine
simulation = SimulationEngine()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection might be closed
                pass

manager = ConnectionManager()

@app.get("/")
async def get():
    return {"message": "Crisis Resource Allocation System API"}

@app.get("/api/status")
async def get_status():
    """Get current simulation status"""
    return simulation.get_allocation_summary()


@app.get("/api/analytics")
async def get_analytics():
    """Get performance analytics and optimization suggestions"""
    summary = simulation.get_allocation_summary()
    
    # Calculate efficiency metrics
    total_penalty = sum(agent.get('penalty', 0) for agent in summary.get('agents', []))
    critical_agents = len([a for a in summary.get('agents', []) if a.get('status') == 'critical'])
    failing_agents = len([a for a in summary.get('agents', []) if a.get('status') == 'failing'])
    stable_agents = len([a for a in summary.get('agents', []) if a.get('status') == 'stable'])
    
    # Generate optimization suggestions
    suggestions = []
    if critical_agents > 0:
        suggestions.append(f"URGENT: {critical_agents} critical agents need immediate resource allocation")
    if failing_agents > 3:
        suggestions.append("Consider enabling preparation mode for better resource management")
    if summary.get('system_stress', 0) > 0.8:
        suggestions.append("System stress is high - consider using reserves or reducing demand")
    if summary.get('utilization', 0) < 70:
        suggestions.append("Utilization is low - reallocate unused resources to failing agents")
    
    return {
        "efficiency_metrics": {
            "total_penalty": total_penalty,
            "critical_count": critical_agents,
            "failing_count": failing_agents,
            "stable_count": stable_agents,
            "efficiency_score": max(0, 100 - total_penalty / 100)  # Simple efficiency calculation
        },
        "optimization_suggestions": suggestions,
        "system_health": "CRITICAL" if critical_agents > 0 else "WARNING" if failing_agents > 0 else "STABLE"
    }

@app.get("/api/history")
async def get_history():
    """Get historical data for charts"""
    return simulation.get_history_data()

@app.post("/api/simulation/start")
async def start_simulation():
    """Start the simulation"""
    if not simulation.is_running:
        simulation.is_running = True
        asyncio.create_task(run_simulation())
        return {"message": "Simulation started"}
    return {"message": "Simulation already running"}

@app.post("/api/simulation/stop")
async def stop_simulation():
    """Stop the simulation"""
    simulation.is_running = False
    return {"message": "Simulation stopped"}

@app.post("/api/simulation/reset")
async def reset_simulation():
    """Reset the simulation"""
    simulation.reset()
    await manager.broadcast(json.dumps({
        "type": "simulation_reset",
        "data": simulation.get_allocation_summary()
    }))
    return {"message": "Simulation reset"}

@app.post("/api/disaster/trigger")
async def trigger_disaster(disaster_data: dict):
    """Manually trigger a disaster event"""
    disaster_type = disaster_data.get("type", "earthquake")
    impact_factor = disaster_data.get("impact", 0.3)
    
    # Apply unique disaster effects based on type
    if disaster_type == "earthquake":
        # Earthquake: Critical infrastructure damage, massive demand spike
        supply_reduction = impact_factor * 0.4  # Higher supply loss
        demand_multiplier = 1.5  # Massive demand increase
        stress_multiplier = 1.3  # Higher system stress
        
    elif disaster_type == "flood":
        # Flood: Water system overload, moderate demand spike
        supply_reduction = impact_factor * 0.3  # Moderate supply loss
        demand_multiplier = 1.3  # Moderate demand increase
        stress_multiplier = 1.2  # Moderate stress increase
        
    elif disaster_type == "power_failure":
        # Power Failure: Direct supply loss, minimal demand change
        supply_reduction = impact_factor * 0.5  # Highest supply loss
        demand_multiplier = 1.1  # Minimal demand increase
        stress_multiplier = 1.4  # High stress due to direct failure
        
    elif disaster_type == "storm":
        # Storm: Variable impact, mixed effects
        supply_reduction = impact_factor * 0.35  # Variable supply loss
        demand_multiplier = 1.25  # Variable demand increase
        stress_multiplier = 1.15  # Variable stress increase
        
    else:
        # Default: Standard disaster
        supply_reduction = impact_factor * 0.3
        demand_multiplier = 1.2
        stress_multiplier = 1.1
    
    # Apply supply reduction
    new_supply = simulation.resource_constraint.total_supply * (1 - supply_reduction)
    simulation.resource_constraint.update_supply(new_supply)
    
    # Apply disaster-specific demand changes
    from agents import AgentBehavior
    for agent in simulation.agents:
        AgentBehavior.apply_disaster_impact(agent, disaster_type, impact_factor)
        
        # Additional disaster-specific demand modifications
        if disaster_type == "earthquake":
            if agent.type.value == "hospital":
                agent.demand *= demand_multiplier * 1.2  # Extra hospital demand
            elif agent.type.value == "emergency_services":
                agent.demand *= demand_multiplier * 1.1
                
        elif disaster_type == "flood":
            if agent.type.value == "water_supply":
                agent.demand *= demand_multiplier * 1.3  # Extra water demand
            elif agent.type.value == "hospital":
                agent.demand *= demand_multiplier * 0.8  # Reduced hospital impact
                
        elif disaster_type == "power_failure":
            # All agents equally affected by power failure
            agent.demand *= demand_multiplier
            
        elif disaster_type == "storm":
            # Randomized storm effects
            import random
            storm_effect = random.uniform(0.8, 1.5)
            agent.demand *= demand_multiplier * storm_effect
    
    # Run immediate negotiation to update allocations
    if simulation.is_running:
        from negotiation import NegotiationEngine
        negotiation_engine = NegotiationEngine()
        
        # Apply stress multiplier to negotiation
        original_stress = simulation.negotiation_engine.calculate_system_stress(simulation.agents)
        modified_agents = []
        for agent in simulation.agents:
            modified_agents.append(agent)
        
        allocation_result = negotiation_engine.run_negotiation(
            modified_agents, 
            simulation.resource_constraint, 
            len(simulation.negotiation_history)
        )
        
        # Update agent allocations
        for agent_id, allocated_amount in allocation_result.allocations.items():
            for agent in simulation.agents:
                if agent.id == agent_id:
                    agent.allocated = allocated_amount
                    break
    
    # Broadcast update with detailed disaster information
    await manager.broadcast(json.dumps({
        "type": "disaster_triggered",
        "data": {
            "type": disaster_type,
            "impact": impact_factor,
            "new_supply": new_supply,
            "supply_reduction": supply_reduction * 100,
            "demand_multiplier": demand_multiplier,
            "stress_multiplier": stress_multiplier
        }
    }))
    
    return {"message": f"Disaster {disaster_type} triggered with {supply_reduction*100:.1f}% supply reduction and {demand_multiplier:.1f}x demand increase"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await manager.send_personal_message(
            json.dumps({
                "type": "initial_state",
                "data": simulation.get_allocation_summary()
            }), 
            websocket
        )
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def run_simulation():
    """Main simulation loop"""
    while simulation.is_running:
        try:
            # Run one simulation step
            state = simulation.step()
            
            # Broadcast state to all connected clients
            await manager.broadcast(json.dumps({
                "type": "simulation_update",
                "data": simulation.get_allocation_summary()
            }))
            
            # Wait before next step (2 seconds for real-time feel)
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            simulation.is_running = False
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
