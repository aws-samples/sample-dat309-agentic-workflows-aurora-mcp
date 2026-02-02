"""
Phase 3 Multi-Agent System - Supervisor architecture with semantic/visual search.

This module demonstrates the enterprise pattern with:
- Supervisor agent that orchestrates specialized sub-agents
- Search agent with Nova 2 Multimodal embeddings (3072 dimensions)
- Product agent for details and inventory
- Order agent for order processing
- Cross-modal search (text and image)
"""

from .supervisor import SupervisorAgent
from .search_agent import SearchAgent, create_search_agent
from .product_agent import ProductAgent, create_product_agent
from .order_agent import OrderAgent, create_order_agent

__all__ = [
    "SupervisorAgent",
    "SearchAgent", "create_search_agent",
    "ProductAgent", "create_product_agent",
    "OrderAgent", "create_order_agent"
]


def create_phase3_system(activity_callback=None):
    """
    Create the complete Phase 3 multi-agent system.
    
    Returns:
        SupervisorAgent configured with all sub-agents
    """
    search_agent = create_search_agent(activity_callback)
    product_agent = create_product_agent(activity_callback)
    order_agent = create_order_agent(activity_callback)
    
    return SupervisorAgent(
        search_agent=search_agent,
        product_agent=product_agent,
        order_agent=order_agent,
        activity_callback=activity_callback
    )
