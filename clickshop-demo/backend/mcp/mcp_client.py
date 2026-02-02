"""
MCP (Model Context Protocol) Client for ClickShop.

Provides integration with awslabs.postgres-mcp-server for Phase 2 database operations.
This enables the same search functionality as Phase 1, but through the MCP protocol.
"""

import os
import asyncio
import json
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class MCPConnectionConfig:
    """Configuration for MCP postgres server connection."""

    # Connection method: 'rdsapi', 'pgwire', or 'pgwire_iam'
    connection_method: str = "rdsapi"

    # Database type: 'APG' (Aurora PostgreSQL) or 'RPG' (RDS PostgreSQL)
    database_type: str = "APG"

    # Aurora cluster identifier (for rdsapi method)
    cluster_identifier: Optional[str] = None

    # Database endpoint (for pgwire methods)
    database_endpoint: Optional[str] = None

    # Database name
    database_name: str = "clickshop"

    # AWS region
    aws_region: str = "us-east-1"

    # AWS profile (optional)
    aws_profile: Optional[str] = None

    # Allow write queries
    allow_write_query: bool = False

    @classmethod
    def from_env(cls) -> "MCPConnectionConfig":
        """Create config from environment variables."""
        return cls(
            connection_method=os.getenv("MCP_CONNECTION_METHOD", "rdsapi"),
            database_type=os.getenv("MCP_DATABASE_TYPE", "APG"),
            cluster_identifier=os.getenv("AURORA_CLUSTER_IDENTIFIER"),
            database_endpoint=os.getenv("AURORA_DATABASE_ENDPOINT"),
            database_name=os.getenv("AURORA_DATABASE", "clickshop"),
            aws_region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            aws_profile=os.getenv("AWS_PROFILE"),
            allow_write_query=os.getenv("MCP_ALLOW_WRITE", "false").lower() == "true",
        )


class MCPPostgresClient:
    """
    MCP client for Aurora PostgreSQL via awslabs.postgres-mcp-server.

    This client connects to the MCP server via stdio transport and provides
    methods to execute SQL queries through MCP tool invocations.
    """

    def __init__(self, config: Optional[MCPConnectionConfig] = None):
        """
        Initialize MCP client.

        Args:
            config: Connection configuration. If None, loads from environment.
        """
        self.config = config or MCPConnectionConfig.from_env()
        self.session: Optional[ClientSession] = None
        self._connected = False
        self._available_tools: List[Dict] = []

    def _get_server_params(self) -> StdioServerParameters:
        """Build server parameters for stdio transport."""
        args = ["awslabs.postgres-mcp-server@latest"]

        if self.config.allow_write_query:
            args.append("--allow_write_query")

        env = {
            "AWS_REGION": self.config.aws_region,
            "FASTMCP_LOG_LEVEL": "ERROR",
        }

        if self.config.aws_profile:
            env["AWS_PROFILE"] = self.config.aws_profile

        # Pass through AWS credentials if set
        if os.getenv("AWS_ACCESS_KEY_ID"):
            env["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
        if os.getenv("AWS_SECRET_ACCESS_KEY"):
            env["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        if os.getenv("AWS_SESSION_TOKEN"):
            env["AWS_SESSION_TOKEN"] = os.getenv("AWS_SESSION_TOKEN")

        return StdioServerParameters(
            command="uvx",
            args=args,
            env=env
        )

    async def connect(self) -> None:
        """
        Connect to the MCP postgres server.

        Establishes stdio transport and initializes the MCP session.
        """
        if self._connected:
            return

        server_params = self._get_server_params()

        # Create stdio transport and session
        self._stdio_context = stdio_client(server_params)
        stdio_transport = await self._stdio_context.__aenter__()
        self._read, self._write = stdio_transport

        self._session_context = ClientSession(self._read, self._write)
        self.session = await self._session_context.__aenter__()

        # Initialize session
        await self.session.initialize()

        # Get available tools
        tools_response = await self.session.list_tools()
        self._available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools_response.tools
        ]

        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if not self._connected:
            return

        if hasattr(self, '_session_context'):
            await self._session_context.__aexit__(None, None, None)
        if hasattr(self, '_stdio_context'):
            await self._stdio_context.__aexit__(None, None, None)

        self._connected = False
        self.session = None

    async def connect_to_database(self) -> Dict[str, Any]:
        """
        Connect to the Aurora PostgreSQL database via MCP.

        Uses the configured connection method (rdsapi, pgwire, or pgwire_iam).

        Returns:
            Connection result from MCP server
        """
        if not self._connected:
            await self.connect()

        # Build connection arguments - all parameters required by postgres-mcp-server
        args = {
            "database": self.config.database_name,
            "database_type": self.config.database_type,
            "connection_method": self.config.connection_method,
            "region": self.config.aws_region,
            "port": 5432,
        }
        
        # cluster_identifier is required
        if self.config.cluster_identifier:
            args["cluster_identifier"] = self.config.cluster_identifier
        else:
            args["cluster_identifier"] = ""
            
        # db_endpoint - required param but can be empty for rdsapi
        if self.config.database_endpoint:
            args["db_endpoint"] = self.config.database_endpoint
        else:
            args["db_endpoint"] = ""

        result = await self.session.call_tool("connect_to_database", args)
        return self._parse_tool_result(result)

    async def run_query(self, sql: str) -> List[Dict]:
        """
        Execute a SQL query through MCP.

        Args:
            sql: SQL query string

        Returns:
            List of result rows as dictionaries
        """
        if not self._connected:
            await self.connect()
            await self.connect_to_database()

        # Build query arguments - MCP server requires connection params with each query
        args = {"sql": sql}
        
        # Add connection parameters based on method
        if self.config.connection_method == "rdsapi":
            args["connection_method"] = "rdsapi"
            args["database"] = self.config.database_name
            if self.config.cluster_identifier:
                args["cluster_identifier"] = self.config.cluster_identifier
            # db_endpoint is optional for rdsapi but may be required
            if self.config.database_endpoint:
                args["db_endpoint"] = self.config.database_endpoint
        else:
            args["connection_method"] = self.config.connection_method
            args["database"] = self.config.database_name
            args["db_endpoint"] = self.config.database_endpoint
            args["cluster_identifier"] = self.config.cluster_identifier or ""

        result = await self.session.call_tool("run_query", args)
        return self._parse_query_result(result)

    def _parse_tool_result(self, result) -> Dict[str, Any]:
        """Parse a generic tool result."""
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        return json.loads(content.text)
                    except json.JSONDecodeError:
                        return {"message": content.text}
        return {"message": str(result)}

    def _parse_query_result(self, result) -> List[Dict]:
        """Parse a query result into list of dictionaries."""
        if hasattr(result, 'content') and result.content:
            for content in result.content:
                if hasattr(content, 'text'):
                    try:
                        data = json.loads(content.text)
                        # Handle different result formats
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict) and "rows" in data:
                            return data["rows"]
                        elif isinstance(data, dict) and "data" in data:
                            return data["data"]
                        elif isinstance(data, dict) and "result" in data:
                            # Handle result wrapper format
                            inner = data["result"]
                            if isinstance(inner, list):
                                return inner
                            elif isinstance(inner, dict) and "rows" in inner:
                                return inner["rows"]
                        return [data] if data else []
                    except json.JSONDecodeError:
                        return []
        return []

    @property
    def available_tools(self) -> List[Dict]:
        """Get list of available MCP tools."""
        return self._available_tools


# Global client instance
_mcp_client: Optional[MCPPostgresClient] = None


def get_mcp_client() -> MCPPostgresClient:
    """Get or create the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPPostgresClient()
    return _mcp_client


@asynccontextmanager
async def mcp_session():
    """
    Context manager for MCP session.

    Handles connection lifecycle automatically.

    Usage:
        async with mcp_session() as client:
            results = await client.run_query("SELECT * FROM products")
    """
    client = get_mcp_client()
    try:
        await client.connect()
        await client.connect_to_database()
        yield client
    finally:
        # Keep connection alive for reuse
        pass
