"""
Phase 3 Multi-Agent System - Supervisor architecture with semantic search.

- Supervisor agent orchestrates specialized sub-agents
- Search agent with Cohere Embed v4 embeddings (1024 dimensions)
- Package agent for trip details and departure availability
- Booking agent for reservation processing
"""

from .supervisor import RetrievalAgent
from .search_agent import SearchAgent, create_search_agent
from .package_agent import PackageAgent, create_package_agent
from .booking_agent import BookingAgent, create_booking_agent

__all__ = [
    "RetrievalAgent",
    "SearchAgent", "create_search_agent",
    "PackageAgent", "create_package_agent",
    "BookingAgent", "create_booking_agent",
]


def create_phase3_system(activity_callback=None):
    """Create the complete Phase 3 multi-agent system."""
    search_agent = create_search_agent(activity_callback)
    package_agent = create_package_agent(activity_callback)
    booking_agent = create_booking_agent(activity_callback)

    return RetrievalAgent(
        search_agent=search_agent,
        package_agent=package_agent,
        booking_agent=booking_agent,
        activity_callback=activity_callback
    )
