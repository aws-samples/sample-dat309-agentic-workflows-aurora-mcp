"""
Phase 1 Agent - Single agent with direct database access.

This agent demonstrates the MVP pattern with:
- RDS Data API for Aurora PostgreSQL access
- Claude Sonnet 4.5 via Amazon Bedrock (cross-region inference)
- Tools for product lookup, inventory check, price calculation, order processing
"""

from .agent import Phase1Agent, create_phase1_agent

__all__ = ["Phase1Agent", "create_phase1_agent"]
