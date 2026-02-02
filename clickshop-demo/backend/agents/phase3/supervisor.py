"""
Phase 3 Supervisor Agent - Orchestrates specialized sub-agents.

Implements the enterprise pattern with:
- Supervisor agent with no direct tools
- Delegation logic to Search, Product, and Order agents
- Claude Sonnet 4.5 via Amazon Bedrock

Requirements: 11.1, 11.5
"""

import os
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List

from strands import Agent
from strands.models import BedrockModel
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


class SupervisorAgent:
    """
    Phase 3 Supervisor Agent that orchestrates specialized sub-agents.
    
    Requirements:
    - 11.1: Includes a Supervisor_Agent that orchestrates specialized sub-agents
    - 11.5: Supervisor has no direct tools and operates purely through delegation
    """
    
    def __init__(
        self,
        search_agent,
        product_agent,
        order_agent,
        activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
    ):
        """
        Initialize Supervisor agent.
        
        Args:
            search_agent: Search agent for semantic/visual search
            product_agent: Product agent for details and inventory
            order_agent: Order agent for order processing
            activity_callback: Optional callback for reporting agent activities
        """
        self.search_agent = search_agent
        self.product_agent = product_agent
        self.order_agent = order_agent
        self.activity_callback = activity_callback or (lambda x: None)
        
        # Initialize Bedrock model - Claude Sonnet 4.5 (cross-region inference)
        self.model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Supervisor has no direct tools - only delegation
        # Requirement 11.5
        self.agent = Agent(
            model=self.model,
            tools=[
                self._delegate_to_search,
                self._delegate_to_product,
                self._delegate_to_order
            ],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor."""
        return """You are a supervisor agent for ClickShop, coordinating specialized agents to help customers.

You have three specialized agents you can delegate to:
1. Search Agent - For finding products via semantic text search or visual image search
2. Product Agent - For getting product details and checking inventory
3. Order Agent - For calculating totals and processing orders

Your role is to:
- Understand customer requests
- Delegate to the appropriate specialized agent
- Coordinate multi-step workflows (e.g., search -> details -> order)
- Synthesize responses from multiple agents

Guidelines:
- For product searches, delegate to Search Agent
- For specific product info or inventory, delegate to Product Agent
- For orders and pricing, delegate to Order Agent
- You can delegate to multiple agents in sequence for complex requests"""
    
    def _log_activity(
        self,
        activity_type: str,
        title: str,
        details: Optional[str] = None,
        sql_query: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        agent_name: str = "SupervisorAgent"
    ):
        """Log an activity entry. Requirement 11.9."""
        entry = ActivityEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            activity_type=activity_type,
            title=title,
            details=details,
            sql_query=sql_query,
            execution_time_ms=execution_time_ms,
            agent_name=agent_name
        )
        self.activity_callback(entry)
    
    async def _delegate_to_search(self, query: str, use_image: bool = False, image_data: Optional[bytes] = None) -> dict:
        """
        Delegate to Search Agent for product search.
        
        Args:
            query: Search query text
            use_image: Whether to use visual search
            image_data: Image bytes for visual search
            
        Returns:
            Search results from Search Agent
        """
        start_time = datetime.utcnow()
        
        self._log_activity(
            activity_type="delegation",
            title="Delegating to Search Agent",
            details=f"Query: {query}, Visual: {use_image}"
        )
        
        if use_image and image_data:
            result = await self.search_agent.visual_search(image_data)
        else:
            result = await self.search_agent.semantic_search(query)
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="delegation",
            title="Search Agent completed",
            details=f"Found {len(result.get('products', []))} products",
            execution_time_ms=execution_time,
            agent_name="SearchAgent"
        )
        
        return result
    
    async def _delegate_to_product(self, action: str, product_id: Optional[str] = None, size: Optional[str] = None) -> dict:
        """
        Delegate to Product Agent for product operations.
        
        Args:
            action: 'details' or 'inventory'
            product_id: Product identifier
            size: Optional size for inventory check
            
        Returns:
            Product information from Product Agent
        """
        start_time = datetime.utcnow()
        
        self._log_activity(
            activity_type="delegation",
            title="Delegating to Product Agent",
            details=f"Action: {action}, Product: {product_id}"
        )
        
        if action == "details":
            result = await self.product_agent.get_product_details(product_id)
        elif action == "inventory":
            result = await self.product_agent.check_inventory_status(product_id, size)
        else:
            result = {"error": f"Unknown action: {action}"}
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="delegation",
            title="Product Agent completed",
            execution_time_ms=execution_time,
            agent_name="ProductAgent"
        )
        
        return result
    
    async def _delegate_to_order(self, action: str, customer_id: Optional[str] = None, items: Optional[List[dict]] = None) -> dict:
        """
        Delegate to Order Agent for order operations.
        
        Args:
            action: 'calculate' or 'process'
            customer_id: Customer identifier (for process)
            items: Order items
            
        Returns:
            Order information from Order Agent
        """
        start_time = datetime.utcnow()
        
        self._log_activity(
            activity_type="delegation",
            title="Delegating to Order Agent",
            details=f"Action: {action}, Items: {len(items or [])}"
        )
        
        if action == "calculate":
            result = await self.order_agent.calculate_total(items or [])
        elif action == "process":
            result = await self.order_agent.process_order(customer_id, items or [])
        else:
            result = {"error": f"Unknown action: {action}"}
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="delegation",
            title="Order Agent completed",
            execution_time_ms=execution_time,
            agent_name="OrderAgent"
        )
        
        return result
    
    async def process_message(
        self,
        message: str,
        customer_id: str,
        activity_callback: Optional[Callable[[ActivityEntry], Any]] = None,
        image_data: Optional[bytes] = None
    ) -> AgentResponse:
        """
        Process a customer message by coordinating sub-agents.
        
        Args:
            message: The customer's message
            customer_id: Identifier for the customer
            activity_callback: Optional callback for activity updates
            image_data: Optional image for visual search
            
        Returns:
            AgentResponse with message, optional products, and optional order
        """
        if activity_callback:
            self.activity_callback = activity_callback
        
        self._log_activity(
            activity_type="delegation",
            title="Supervisor processing request",
            details=f"Message: {message[:100]}..." + (" [with image]" if image_data else "")
        )
        
        start_time = datetime.utcnow()
        
        # If image provided, include it in context
        context = {"customer_id": customer_id}
        if image_data:
            context["image_data"] = image_data
        
        # Run the supervisor agent
        response = await self.agent.run(message, context=context)
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="delegation",
            title="Supervisor completed coordination",
            execution_time_ms=execution_time
        )
        
        return AgentResponse(
            message=str(response),
            products=None,
            order=None
        )
