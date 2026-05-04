from models import Agent, NegotiationRound, ResourceConstraint
from agents import AgentBehavior
from typing import Dict, List, Tuple
import logging

class NegotiationEngine:
    def __init__(self):
        self.max_rounds = 5
        self.fairness_threshold = 0.1  # Minimum allocation for lowest priority
        self.preparation_mode = False  # New attribute to track preparation mode
    
    def run_negotiation(self, agents: List[Agent], resource_constraint: ResourceConstraint, round_number: int) -> NegotiationRound:
        """Run a single round of negotiation"""
        
        # Collect requests from all agents
        agent_requests = {}
        for agent in agents:
            request = AgentBehavior.negotiate_request(agent, round_number, resource_constraint.total_supply)
            agent_requests[agent.id] = request
        
        # Update agent priorities dynamically
        self._update_agent_priorities(agents)
        
        # Calculate allocations
        allocations = self._allocate_resources(agents, agent_requests, resource_constraint)
        
        # Update agents with allocations
        for agent in agents:
            agent.allocated = allocations.get(agent.id, 0.0)
            agent.update_status()
        
        # Generate decisions log
        decisions = self._generate_decisions(agents, allocations, resource_constraint)
        
        # Create negotiation round record
        negotiation_round = NegotiationRound(
            round_number=round_number,
            agent_requests=agent_requests,
            allocations=allocations,
            total_demand=sum(agent_requests.values()),
            total_supply=resource_constraint.total_supply,
            decisions=decisions
        )
        
        return negotiation_round
    
    def _allocate_resources(self, agents: List[Agent], requests: Dict[str, float], 
                           constraint: ResourceConstraint) -> Dict[str, float]:
        """Allocate resources based on priority and constraints"""
        
        # Sort agents by priority (lower number = higher priority)
        sorted_agents = sorted(agents, key=lambda a: a.priority)
        
        allocations = {}
        remaining_supply = constraint.total_supply
        
        # First pass: satisfy minimum requirements for all agents
        for agent in sorted_agents:
            min_req = min(agent.min_required, remaining_supply)
            allocations[agent.id] = min_req
            remaining_supply -= min_req
        
        # Second pass: distribute remaining supply by priority
        if remaining_supply > 0:
            for agent in sorted_agents:
                request = requests.get(agent.id, 0)
                current_alloc = allocations.get(agent.id, 0)
                
                # Can allocate up to request amount or remaining supply
                additional = min(request - current_alloc, remaining_supply)
                allocations[agent.id] = current_alloc + additional
                remaining_supply -= additional
                
                if remaining_supply <= 0:
                    break
        
        # If still have supply, distribute to lower priority agents with fairness
        if remaining_supply > 0:
            self._apply_fairness_distribution(agents, allocations, remaining_supply, requests)
        
        return allocations
    
    def _apply_fairness_distribution(self, agents: List[Agent], allocations: Dict[str, float], 
                                   remaining_supply: float, requests: Dict[str, float]):
        """Apply fairness rule to prevent starvation of low-priority agents"""
        
        # Find agents getting less than fairness threshold
        under_allocated = []
        for agent in agents:
            request = requests.get(agent.id, 0)
            current = allocations.get(agent.id, 0)
            if request > 0 and current < request * self.fairness_threshold:
                under_allocated.append(agent)
        
        # Distribute remaining supply proportionally
        if under_allocated and remaining_supply > 0:
            total_deficit = sum(requests[a.id] - allocations[a.id] for a in under_allocated)
            
            for agent in under_allocated:
                deficit = requests[agent.id] - allocations[agent.id]
                if total_deficit > 0:
                    fair_share = (deficit / total_deficit) * remaining_supply
                    allocations[agent.id] += fair_share
    
    def _generate_decisions(self, agents: List[Agent], allocations: Dict[str, float], 
                           constraint: ResourceConstraint) -> List[str]:
        """Generate human-readable decisions for the round"""
        decisions = []
        
        total_allocated = sum(allocations.values())
        total_requested = sum(agent.demand for agent in agents)
        
        decisions.append(f"Total Supply: {constraint.total_supply:.1f} units")
        decisions.append(f"Total Requested: {total_requested:.1f} units")
        decisions.append(f"Total Allocated: {total_allocated:.1f} units")
        decisions.append(f"Utilization: {(total_allocated/constraint.total_supply)*100:.1f}%")
        
        # Priority-based decisions
        critical_agents = [a for a in agents if a.status.value == "critical"]
        if critical_agents:
            decisions.append(f"ALERT: {len(critical_agents)} critical agents detected")
        
        # Check for high-priority agents with poor allocation
        high_priority_poor = [a for a in agents if a.priority <= 2 and 
                             a.allocated < a.min_required]
        if high_priority_poor:
            decisions.append(f"WARNING: High-priority services under-allocated")
        
        return decisions
    
    def calculate_system_stress(self, agents: List[Agent]) -> float:
        """Calculate overall system stress level (0-1)"""
        if not agents:
            return 0.0
        
        total_penalty = sum(agent.calculate_penalty() for agent in agents)
        max_possible_penalty = sum(agent.demand * agent.penalty_rate for agent in agents)
        
        if max_possible_penalty == 0:
            return 0.0
        
        return min(1.0, total_penalty / max_possible_penalty)
    
    def check_convergence(self, agents: List[Agent], previous_allocations: Dict[str, float]) -> bool:
        """Check if negotiation has converged (allocations stable)"""
        tolerance = 0.01  # 1% tolerance
        
        for agent in agents:
            current = agent.allocated
            previous = previous_allocations.get(agent.id, 0)
            
            if abs(current - previous) > tolerance:
                return False
        
        return True
