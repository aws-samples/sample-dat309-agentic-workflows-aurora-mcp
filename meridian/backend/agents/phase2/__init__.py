"""
Phase 2 Agent - Agent with MCP abstraction layer.

This agent demonstrates the scalable pattern with:
- MCP integration using awslabs.postgres-mcp-server
- RDS Data API for database operations
- Claude Opus 4.7 via Amazon Bedrock
- Auto-discovered tools from MCP server
"""

from .agent import MCPAgent, create_mcp_agent

__all__ = ["MCPAgent", "create_mcp_agent"]
