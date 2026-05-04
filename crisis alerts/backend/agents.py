from models import Agent, AgentType, AgentStatus
import random
import math

class AgentFactory:
    @staticmethod
    def create_hospital(agent_id: str) -> Agent:
        return Agent(
            id=agent_id,
            type=AgentType.HOSPITAL,
            name=f"City Hospital {agent_id}",
            demand=random.uniform(25, 35),
            min_required=random.uniform(15, 20),
            priority=1,
            penalty_rate=10.0
        )
    
    @staticmethod
    def create_emergency_services(agent_id: str) -> Agent:
        return Agent(
            id=agent_id,
            type=AgentType.EMERGENCY_SERVICES,
            name=f"Emergency Services {agent_id}",
            demand=random.uniform(15, 25),
            min_required=random.uniform(8, 12),
            priority=2,
            penalty_rate=8.0
        )
    
    @staticmethod
    def create_water_supply(agent_id: str) -> Agent:
        return Agent(
            id=agent_id,
            type=AgentType.WATER_SUPPLY,
            name=f"Water Supply Station {agent_id}",
            demand=random.uniform(20, 30),
            min_required=random.uniform(10, 15),
            priority=3,
            penalty_rate=5.0
        )
    
    @staticmethod
    def create_residential_commercial(agent_id: str) -> Agent:
        return Agent(
            id=agent_id,
            type=AgentType.RESIDENTIAL_COMMERCIAL,
            name=f"Residential/Commercial Zone {agent_id}",
            demand=random.uniform(10, 20),
            min_required=random.uniform(2, 5),
            priority=4,
            penalty_rate=2.0
        )

class AgentBehavior:
    @staticmethod
    def update_demand(agent: Agent, time_step: int):
        """Dynamic demand update based on time and agent type"""
        base_demand = agent.demand
        
        if agent.type == AgentType.HOSPITAL:
            # Hospitals have relatively stable demand with small variations
            variation = math.sin(time_step * 0.1) * 2
            agent.demand = max(agent.min_required, base_demand + variation)
        
        elif agent.type == AgentType.EMERGENCY_SERVICES:
            # Emergency services have more volatile demand
            variation = math.sin(time_step * 0.2) * 5 + random.uniform(-2, 2)
            agent.demand = max(agent.min_required, base_demand + variation)
        
        elif agent.type == AgentType.WATER_SUPPLY:
            # Water demand follows daily patterns
            daily_pattern = math.sin(time_step * 0.05) * 3
            agent.demand = max(agent.min_required, base_demand + daily_pattern)
        
        else:  # Residential/Commercial
            # Residential demand has daily peaks
            daily_peak = math.sin(time_step * 0.05 - math.pi/2) * 4
            agent.demand = max(agent.min_required, base_demand + daily_peak)
    
    @staticmethod
    def negotiate_request(agent: Agent, round_number: int, total_supply: float) -> float:
        """Agent's negotiation strategy"""
        if round_number == 0:
            # First round: request full demand
            return agent.demand
        
        # Adjust request based on previous allocation
        allocation_ratio = agent.allocated / agent.demand if agent.demand > 0 else 0
        
        if allocation_ratio >= 0.9:
            # Well allocated, maintain demand
            return agent.demand
        elif allocation_ratio >= agent.min_required / agent.demand:
            # Partially allocated, request min_required + some buffer
            buffer = (agent.demand - agent.min_required) * 0.5
            return agent.min_required + buffer
        else:
            # Poorly allocated, request minimum
            return agent.min_required
    
    @staticmethod
    def apply_disaster_impact(agent: Agent, disaster_type: str, impact_factor: float):
        """Apply disaster impact to agent demand"""
        if disaster_type == "earthquake":
            if agent.type == AgentType.HOSPITAL:
                agent.demand *= (1 + impact_factor * 0.5)  # Hospitals need more power
            elif agent.type == AgentType.EMERGENCY_SERVICES:
                agent.demand *= (1 + impact_factor * 0.3)
        
        elif disaster_type == "flood":
            if agent.type == AgentType.WATER_SUPPLY:
                agent.demand *= (1 + impact_factor * 0.4)  # Water treatment needs more power
            elif agent.type == AgentType.HOSPITAL:
                agent.demand *= (1 + impact_factor * 0.2)
        
        elif disaster_type == "power_failure":
            # All agents affected equally
            agent.demand *= (1 + impact_factor * 0.1)
