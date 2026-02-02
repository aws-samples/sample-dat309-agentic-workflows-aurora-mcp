"""
Phase 2 Agent - Agent with MCP abstraction layer.

Implements the scalable pattern using:
- Strands SDK with MCP integration
- awslabs.postgres-mcp-server for RDS Data API
- Claude Sonnet 4.5 via Amazon Bedrock
- Auto-discovered tools from MCP server

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
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
    products: Optional[List[dict]] = None
    order: Optional[dict] = None


class Phase2Agent:
    """
    Phase 2 Shopping Agent with MCP abstraction layer.
    
    Uses Strands SDK with MCP client for database operations via RDS Data API.
    
    Requirements:
    - 10.1: Implemented using Strands SDK with MCP integration
    - 10.2: Uses awslabs.postgres-mcp-server for database operations via RDS Data API
    - 10.3: Uses Claude Sonnet 4.5 via Amazon Bedrock
    - 10.4: Auto-discovers available tools from MCP server
    - 10.5: Logs MCP tool invocations and execution times
    """
    
    def __init__(self, activity_callback: Optional[Callable[[ActivityEntry], Any]] = None):
        """
        Initialize Phase 2 agent.
        
        Args:
            activity_callback: Optional callback for reporting agent activities
        """
        self.activity_callback = activity_callback or (lambda x: None)
        
        # Initialize Bedrock model - Claude Sonnet 4.5
        # Requirement 10.3
        self.model = BedrockModel(
            model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Initialize MCP client for postgres-mcp-server
        # Requirement 10.2
        self.mcp_client = MCPClient(
            server_name="postgres-mcp-server",
            command="uvx",
            args=[
                "awslabs.postgres-mcp-server@latest",
                "--cluster-arn", os.getenv("AURORA_CLUSTER_ARN", ""),
                "--secret-arn", os.getenv("AURORA_SECRET_ARN", ""),
                "--database", os.getenv("AURORA_DATABASE", "clickshop"),
                "--region", os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            ]
        )
        
        # Create agent - tools will be auto-discovered from MCP server
        # Requirement 10.4
        self.agent = None  # Initialized in async context
    
    async def _initialize_agent(self):
        """Initialize the agent with MCP tools."""
        if self.agent is not None:
            return
        
        # Connect to MCP server and discover tools
        await self.mcp_client.connect()
        mcp_tools = await self.mcp_client.list_tools()
        
        self._log_activity(
            activity_type="mcp",
            title="MCP server connected",
            details=f"Discovered {len(mcp_tools)} tools from postgres-mcp-server"
        )
        
        # Create agent with discovered MCP tools
        self.agent = Agent(
            model=self.model,
            tools=mcp_tools,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the shopping assistant."""
        return """You are a helpful shopping assistant for ClickShop, an athletic and fitness equipment store.

You have access to database tools through MCP (Model Context Protocol) that allow you to:
- Query the products table for product information
- Check inventory levels
- Process orders
- Search for products

The database schema includes:
- products: product_id, name, brand, price, description, image_url, category, available_sizes, inventory, embedding
- customers: customer_id, name, email
- orders: order_id, customer_id, status, total_amount
- order_items: item_id, order_id, product_id, size, quantity, unit_price

Guidelines:
- Be friendly and helpful
- Use SQL queries through the MCP tools to get accurate product information
- Recommend products based on customer needs
- Always confirm order details before processing

Available product categories:
- Running Shoes
- Training Shoes
- Fitness Equipment
- Apparel
- Accessories
- Recovery"""
    
    def _log_activity(
        self,
        activity_type: str,
        title: str,
        details: Optional[str] = None,
        sql_query: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        """Log an activity entry. Requirement 10.5."""
        entry = ActivityEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            activity_type=activity_type,
            title=title,
            details=details,
            sql_query=sql_query,
            execution_time_ms=execution_time_ms,
            agent_name="Phase2Agent"
        )
        self.activity_callback(entry)
    
    def _wrap_mcp_tool(self, tool_func, tool_name: str):
        """Wrap an MCP tool to add activity logging."""
        async def wrapped(*args, **kwargs):
            start_time = datetime.utcnow()
            
            self._log_activity(
                activity_type="mcp",
                title=f"MCP tool invocation: {tool_name}",
                details=f"Args: {kwargs}"
            )
            
            result = await tool_func(*args, **kwargs)
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            self._log_activity(
                activity_type="mcp",
                title=f"MCP tool completed: {tool_name}",
                details=f"Result received",
                execution_time_ms=execution_time
            )
            
            return result
        
        return wrapped
    
    async def process_message(
        self,
        message: str,
        customer_id: str,
        activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
    ) -> AgentResponse:
        """
        Process a customer message and return a response.
        
        Args:
            message: The customer's message
            customer_id: Identifier for the customer
            activity_callback: Optional callback for activity updates
            
        Returns:
            AgentResponse with message, optional products, and optional order
        """
        if activity_callback:
            self.activity_callback = activity_callback
        
        # Initialize agent if needed
        await self._initialize_agent()
        
        self._log_activity(
            activity_type="mcp",
            title="Processing customer message via MCP",
            details=f"Message: {message[:100]}..."
        )
        
        start_time = datetime.utcnow()
        
        # Run the agent
        response = await self.agent.run(message)
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="mcp",
            title="Agent response generated",
            execution_time_ms=execution_time
        )
        
        return AgentResponse(
            message=str(response),
            products=None,
            order=None
        )
    
    async def close(self):
        """Close MCP client connection."""
        if self.mcp_client:
            await self.mcp_client.disconnect()


def create_phase2_agent(
    activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
) -> Phase2Agent:
    """
    Create a Phase 2 agent instance.
    
    Args:
        activity_callback: Optional callback for activity updates
        
    Returns:
        Configured Phase2Agent instance
    """
    return Phase2Agent(activity_callback=activity_callback)
