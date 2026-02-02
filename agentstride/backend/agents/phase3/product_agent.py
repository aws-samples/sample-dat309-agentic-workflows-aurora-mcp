"""
Phase 3 Product Agent - Specialized in product details and inventory.

Implements product operations using:
- RDS Data API for Aurora PostgreSQL access
- Claude Sonnet 4.5 via Amazon Bedrock (cross-region inference)

Requirements: 11.3
"""

import os
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List

from strands import Agent, tool
from strands.models import BedrockModel
from pydantic import BaseModel

from db.rds_data_client import get_rds_data_client


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


class ProductAgent:
    """
    Product Agent specialized in product details and inventory.
    
    Requirements:
    - 11.3: Product_Agent specialized in product details and inventory
    """
    
    def __init__(self, activity_callback: Optional[Callable[[ActivityEntry], Any]] = None):
        """
        Initialize Product agent.
        
        Args:
            activity_callback: Optional callback for reporting agent activities
        """
        self.activity_callback = activity_callback or (lambda x: None)
        self.db = get_rds_data_client()
        
        # Initialize model (cross-region inference)
        self.model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Create agent with product tools
        self.agent = Agent(
            model=self.model,
            tools=[self._get_details_tool, self._check_inventory_tool],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the product agent."""
        return """You are a Product Agent specialized in providing product information.

Your capabilities:
- Get detailed product information by ID
- Check inventory status and available sizes

When helping customers:
- Provide accurate product details
- Check stock availability before recommending
- Suggest alternatives if items are out of stock"""
    
    def _log_activity(
        self,
        activity_type: str,
        title: str,
        details: Optional[str] = None,
        sql_query: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ):
        """Log an activity entry."""
        entry = ActivityEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            activity_type=activity_type,
            title=title,
            details=details,
            sql_query=sql_query,
            execution_time_ms=execution_time_ms,
            agent_name="ProductAgent"
        )
        self.activity_callback(entry)
    
    @tool
    async def _get_details_tool(self, product_id: str) -> dict:
        """
        Get detailed product information.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product details
        """
        return await self.get_product_details(product_id)
    
    @tool
    async def _check_inventory_tool(self, product_id: str, size: Optional[str] = None) -> dict:
        """
        Check inventory status for a product.
        
        Args:
            product_id: Product identifier
            size: Optional size to check
            
        Returns:
            Inventory status
        """
        return await self.check_inventory_status(product_id, size)
    
    async def get_product_details(self, product_id: str) -> dict:
        """
        Get detailed information about a product.
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product details dictionary
        """
        start_time = datetime.utcnow()
        
        query = """
            SELECT product_id, name, brand, price, description,
                   image_url, category, available_sizes, inventory
            FROM products
            WHERE product_id = %s
        """
        
        result = await self.db.execute_one(query, (product_id,))
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="search",
            title=f"Product details: {product_id}",
            details=f"Found: {result['name'] if result else 'Not found'}",
            sql_query=query.strip(),
            execution_time_ms=execution_time
        )
        
        if not result:
            return {"error": f"Product {product_id} not found"}
        
        result['price'] = float(result['price'])
        return dict(result)
    
    async def check_inventory_status(self, product_id: str, size: Optional[str] = None) -> dict:
        """
        Check inventory status for a product.
        
        Args:
            product_id: Product identifier
            size: Optional size to check
            
        Returns:
            Inventory status with availability
        """
        start_time = datetime.utcnow()
        
        query = """
            SELECT product_id, name, inventory, available_sizes
            FROM products
            WHERE product_id = %s
        """
        
        result = await self.db.execute_one(query, (product_id,))
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="inventory",
            title=f"Inventory check: {product_id}" + (f" size {size}" if size else ""),
            sql_query=query.strip(),
            execution_time_ms=execution_time
        )
        
        if not result:
            return {"error": f"Product {product_id} not found"}
        
        inventory = result['inventory']
        
        if size:
            quantity = inventory.get(size, 0)
            return {
                "product_id": product_id,
                "name": result['name'],
                "size": size,
                "quantity": quantity,
                "in_stock": quantity > 0,
                "available_sizes": result['available_sizes']
            }
        else:
            if isinstance(inventory, dict):
                if 'quantity' in inventory:
                    total = inventory['quantity']
                else:
                    total = sum(inventory.values())
            else:
                total = 0
            
            return {
                "product_id": product_id,
                "name": result['name'],
                "total_quantity": total,
                "inventory_by_size": inventory,
                "in_stock": total > 0,
                "available_sizes": result['available_sizes']
            }


def create_product_agent(
    activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
) -> ProductAgent:
    """Create a Product agent instance."""
    return ProductAgent(activity_callback=activity_callback)
