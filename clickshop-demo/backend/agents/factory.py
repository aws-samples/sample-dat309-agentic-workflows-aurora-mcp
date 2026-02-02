"""
Agent Factory for ClickShop.

Creates phase-specific agents based on the requested architecture pattern.
"""

from typing import Literal, Protocol, Callable, Any, Optional
from pydantic import BaseModel


class ActivityEntry(BaseModel):
    """Model for agent activity entries."""
    id: str
    timestamp: str
    activity_type: str
    title: str
    details: Optional[str] = None
    sql_query: Optional[str] = None
    execution_time_ms: Optional[int] = None
    agent_name: Optional[str] = None


class AgentResponse(BaseModel):
    """Response from agent processing."""
    message: str
    products: Optional[list] = None
    order: Optional[dict] = None


class ShoppingAgent(Protocol):
    """Protocol defining the interface for shopping agents."""
    
    async def process_message(
        self,
        message: str,
        customer_id: str,
        activity_callback: Callable[[ActivityEntry], Any]
    ) -> AgentResponse:
        """
        Process a customer message and return a response.
        
        Args:
            message: The customer's message
            customer_id: Identifier for the customer
            activity_callback: Callback function to report agent activities
            
        Returns:
            AgentResponse with message, optional products, and optional order
        """
        ...


def create_agent(phase: Literal[1, 2, 3]) -> ShoppingAgent:
    """
    Create an agent for the specified phase.
    
    Args:
        phase: The architecture phase (1, 2, or 3)
        
    Returns:
        A ShoppingAgent implementation for the specified phase
        
    Raises:
        ValueError: If an invalid phase is specified
    """
    if phase == 1:
        from agents.phase1 import create_phase1_agent
        return create_phase1_agent()
    elif phase == 2:
        from agents.phase2 import create_phase2_agent
        return create_phase2_agent()
    elif phase == 3:
        from agents.phase3 import create_phase3_system
        return create_phase3_system()
    else:
        raise ValueError(f"Invalid phase: {phase}. Must be 1, 2, or 3.")
