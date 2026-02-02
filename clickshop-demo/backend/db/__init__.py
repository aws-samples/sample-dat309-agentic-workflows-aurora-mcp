"""
Database layer for ClickShop.

Contains:
- rds_data_client.py: RDS Data API client for Aurora PostgreSQL (Phase 1 & 3)
- mcp_client.py: MCP server client for Aurora PostgreSQL (Phase 2)
- embedding_service.py: Nova Multimodal Embeddings service
"""

from .rds_data_client import RDSDataClient, get_rds_data_client

__all__ = ["RDSDataClient", "get_rds_data_client"]
