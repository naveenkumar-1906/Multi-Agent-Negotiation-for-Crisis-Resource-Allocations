from models import Agent, ResourceConstraint, SimulationState, DisasterEvent, NegotiationRound
from agents import AgentFactory, AgentBehavior
from negotiation import NegotiationEngine
from typing import List, Dict
import random
import math
import time

class SimulationEngine:
    def __init__(self):
        self.agents: List[Agent] = []
        self.resource_constraint = ResourceConstraint(
            total_supply=100.0,
            available=100.0,
            timestamp=0
        )
        self.negotiation_engine = NegotiationEngine()
        self.timestamp = 0
        self.negotiation_history: List[NegotiationRound] = []
        self.disaster_events: List[DisasterEvent] = []
        self.is_running = False
        self.dynamic_priorities = {}
        self.efficiency_history = []
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Create initial set of agents"""
        # Create 2 hospitals
        self.agents.append(AgentFactory.create_hospital("H1"))
        self.agents.append(AgentFactory.create_hospital("H2"))
        
        # Create 2 emergency services
        self.agents.append(AgentFactory.create_emergency_services("E1"))
        self.agents.append(AgentFactory.create_emergency_services("E2"))
        
        # Create 2 water supply stations
        self.agents.append(AgentFactory.create_water_supply("W1"))
        self.agents.append(AgentFactory.create_water_supply("W2"))
        
        # Create 3 residential/commercial zones
        self.agents.append(AgentFactory.create_residential_commercial("R1"))
        self.agents.append(AgentFactory.create_residential_commercial("R2"))
        self.agents.append(AgentFactory.create_residential_commercial("R3"))
    
    def step(self) -> SimulationState:
        """Execute one simulation time step"""
        self.timestamp += 1
        
        # Update resource supply (fluctuating)
        self._update_supply()
        
        # Update agent demands
        self._update_demands()
        
        # Check for disaster events
        self._check_disaster_events()
        
        # Run negotiation
        negotiation_round = self.negotiation_engine.run_negotiation(
            self.agents, self.resource_constraint, len(self.negotiation_history)
        )
        self.negotiation_history.append(negotiation_round)
        
        # Calculate system metrics
        system_stress = self.negotiation_engine.calculate_system_stress(self.agents)
        total_penalty = sum(agent.calculate_penalty() for agent in self.agents)
        
        # Create simulation state
        state = SimulationState(
            timestamp=self.timestamp,
            agents=self.agents.copy(),
            resource_constraint=self.resource_constraint,
            current_round=len(self.negotiation_history),
            negotiation_history=self.negotiation_history[-10:],  # Keep last 10 rounds
            system_stress=system_stress,
            total_penalty=total_penalty
        )
        
        return state
    
    def _update_supply(self):
        """Update power supply with realistic fluctuations"""
        base_supply = 100.0
        
        # Normal fluctuation
        fluctuation = math.sin(self.timestamp * 0.1) * 10
        noise = random.uniform(-5, 5)
        
        new_supply = max(30, base_supply + fluctuation + noise)
        self.resource_constraint.update_supply(new_supply)
    
    def _update_demands(self):
        """Update all agent demands"""
        for agent in self.agents:
            AgentBehavior.update_demand(agent, self.timestamp)
        
        # Dynamic priority adjustment based on critical conditions
        self._adjust_dynamic_priorities()
    
    def _adjust_dynamic_priorities(self):
        """Dynamically adjust priorities based on critical conditions"""
        for agent in self.agents:
            # Elevate priority for critical agents
            if agent.status == AgentStatus.CRITICAL and agent.priority > 1:
                self.dynamic_priorities[agent.id] = agent.priority - 1
            # Restore original priority if stable
            elif agent.status == AgentStatus.STABLE and agent.id in self.dynamic_priorities:
                del self.dynamic_priorities[agent.id]
    
    def get_effective_priority(self, agent):
        """Get effective priority considering dynamic adjustments"""
        return self.dynamic_priorities.get(agent.id, agent.priority)
    
    def track_efficiency(self):
        """Track system efficiency over time"""
        total_penalty = sum(agent.calculate_penalty() for agent in self.agents)
        efficiency_score = max(0, 100 - total_penalty / 100)
        
        self.efficiency_history.append({
            "timestamp": self.timestamp,
            "efficiency": efficiency_score,
            "penalty": total_penalty,
            "critical_count": len([a for a in self.agents if a.status == AgentStatus.CRITICAL])
        })
        
        # Keep only last 50 records
        if len(self.efficiency_history) > 50:
            self.efficiency_history = self.efficiency_history[-50:]
    
    def _check_disaster_events(self):
        """Randomly trigger disaster events"""
        if random.random() < 0.05:  # 5% chance per step
            self._trigger_disaster()
    
    def _trigger_disaster(self):
        """Trigger a random disaster event"""
        disasters = [
            ("earthquake", 0.3, "Earthquake strikes the city"),
            ("flood", 0.4, "Major flooding in downtown area"),
            ("power_failure", 0.5, "Grid failure in industrial district"),
            ("storm", 0.2, "Severe storm approaching")
        ]
        
        disaster_type, impact_factor, description = random.choice(disasters)
        
        # Apply supply impact
        supply_reduction = random.uniform(0.1, 0.4) * impact_factor
        new_supply = self.resource_constraint.total_supply * (1 - supply_reduction)
        self.resource_constraint.update_supply(new_supply)
        
        # Apply demand impacts
        demand_impacts = {}
        for agent in self.agents:
            AgentBehavior.apply_disaster_impact(agent, disaster_type, impact_factor)
            demand_impacts[agent.id] = agent.demand
        
        # Create disaster event record
        disaster = DisasterEvent(
            timestamp=self.timestamp,
            type=disaster_type,
            impact_supply=supply_reduction,
            impact_demands=demand_impacts,
            description=description
        )
        
        self.disaster_events.append(disaster)
    
    def get_allocation_summary(self) -> Dict:
        """Get current allocation summary for visualization"""
        summary = {
            "timestamp": self.timestamp,
            "total_supply": self.resource_constraint.total_supply,
            "total_demand": sum(agent.demand for agent in self.agents),
            "total_allocated": sum(agent.allocated for agent in self.agents),
            "utilization": (sum(agent.allocated for agent in self.agents) / 
                          self.resource_constraint.total_supply * 100) if self.resource_constraint.total_supply > 0 else 0,
            "system_stress": self.negotiation_engine.calculate_system_stress(self.agents),
            "agents": []
        }
        
        for agent in self.agents:
            agent_data = {
                "id": agent.id,
                "name": agent.name,
                "type": agent.type.value,
                "priority": agent.priority,
                "demand": agent.demand,
                "allocated": agent.allocated,
                "min_required": agent.min_required,
                "status": agent.status.value,
                "allocation_ratio": agent.allocated / agent.demand if agent.demand > 0 else 0,
                "penalty": agent.calculate_penalty()
            }
            summary["agents"].append(agent_data)
        
        return summary
    
    def reset(self):
        """Reset simulation to initial state"""
        self.timestamp = 0
        self.agents.clear()
        self.negotiation_history.clear()
        self.disaster_events.clear()
        self.resource_constraint = ResourceConstraint(
            total_supply=100.0,
            available=100.0,
            timestamp=0
        )
        self._initialize_agents()
    
    def get_history_data(self) -> Dict:
        """Get historical data for charts"""
        if not self.negotiation_history:
            return {"timestamps": [], "supply": [], "demand": [], "allocated": []}
        
        timestamps = []
        supply = []
        demand = []
        allocated = []
        
        for i, round_data in enumerate(self.negotiation_history):
            timestamps.append(i)
            supply.append(round_data.total_supply)
            demand.append(round_data.total_demand)
            allocated.append(sum(round_data.allocations.values()))
        
        return {
            "timestamps": timestamps,
            "supply": supply,
            "demand": demand,
            "allocated": allocated
        }
