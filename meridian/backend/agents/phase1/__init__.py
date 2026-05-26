"""
Phase 1 Agent - Single agent with direct database access.

This agent demonstrates the MVP pattern with:
- RDS Data API for Aurora PostgreSQL access
- Claude Opus 4.7 via Amazon Bedrock (cross-region inference)
- Tools for product lookup, inventory check, price calculation, order processing
"""

from .agent import SQLAgent, create_sql_agent

__all__ = ["SQLAgent", "create_sql_agent"]
