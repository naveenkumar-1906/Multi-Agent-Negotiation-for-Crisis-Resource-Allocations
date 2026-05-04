from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class AgentType(str, Enum):
    HOSPITAL = "hospital"
    EMERGENCY_SERVICES = "emergency_services"
    WATER_SUPPLY = "water_supply"
    RESIDENTIAL_COMMERCIAL = "residential_commercial"

class AgentStatus(str, Enum):
    CRITICAL = "critical"
    STABLE = "stable"
    FAILING = "failing"

class Agent(BaseModel):
    id: str
    type: AgentType
    name: str
    demand: float
    min_required: float
    allocated: float = 0.0
    priority: int
    penalty_rate: float
    status: AgentStatus = AgentStatus.STABLE
    negotiation_round: int = 0
    
    def update_status(self):
        allocation_ratio = self.allocated / self.demand if self.demand > 0 else 0
        if allocation_ratio < (self.min_required / self.demand):
            self.status = AgentStatus.CRITICAL
        elif allocation_ratio < 0.8:
            self.status = AgentStatus.FAILING
        else:
            self.status = AgentStatus.STABLE
    
    def calculate_penalty(self) -> float:
        shortage = max(0, self.demand - self.allocated)
        return shortage * self.penalty_rate

class ResourceConstraint(BaseModel):
    total_supply: float
    available: float
    timestamp: int
    
    def update_supply(self, new_supply: float):
        self.total_supply = new_supply
        self.available = new_supply

class NegotiationRound(BaseModel):
    round_number: int
    agent_requests: Dict[str, float]
    allocations: Dict[str, float]
    total_demand: float
    total_supply: float
    decisions: List[str]

class SimulationState(BaseModel):
    timestamp: int
    agents: List[Agent]
    resource_constraint: ResourceConstraint
    current_round: int
    negotiation_history: List[NegotiationRound]
    system_stress: float
    total_penalty: float

class DisasterEvent(BaseModel):
    timestamp: int
    type: str
    impact_supply: float
    impact_demands: Dict[str, float]
    description: str
