"""
Phase 2 Agent - Agent with MCP abstraction layer.

This agent demonstrates the scalable pattern with:
- MCP integration using awslabs.postgres-mcp-server
- RDS Data API for database operations
- Claude Sonnet 4.5 via Amazon Bedrock
- Auto-discovered tools from MCP server
"""

from .agent import Phase2Agent, create_phase2_agent

__all__ = ["Phase2Agent", "create_phase2_agent"]
