"""
Phase 3 Order Agent - Specialized in order processing.

Implements order operations using:
- RDS Data API for Aurora PostgreSQL access
- Claude Sonnet 4.5 via Amazon Bedrock (cross-region inference)

Requirements: 11.4
"""

import os
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
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


class OrderAgent:
    """
    Order Agent specialized in order processing.
    
    Requirements:
    - 11.4: Order_Agent specialized in order processing
    """
    
    def __init__(self, activity_callback: Optional[Callable[[ActivityEntry], Any]] = None):
        """
        Initialize Order agent.
        
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
        
        # Create agent with order tools
        self.agent = Agent(
            model=self.model,
            tools=[self._calculate_total_tool, self._process_order_tool],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the order agent."""
        return """You are an Order Agent specialized in processing customer orders.

Your capabilities:
- Calculate order totals including tax and shipping
- Process orders and create order records

Guidelines:
- Always show order breakdown before processing
- Apply free shipping for orders over $100
- Tax rate is 8.5%
- Confirm all details before finalizing orders"""
    
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
            agent_name="OrderAgent"
        )
        self.activity_callback(entry)
    
    @tool
    async def _calculate_total_tool(self, items: List[dict]) -> dict:
        """
        Calculate order total.
        
        Args:
            items: List of items with product_id, quantity, optional size
            
        Returns:
            Order total breakdown
        """
        return await self.calculate_total(items)
    
    @tool
    async def _process_order_tool(self, customer_id: str, items: List[dict]) -> dict:
        """
        Process a new order.
        
        Args:
            customer_id: Customer identifier
            items: List of order items
            
        Returns:
            Order confirmation
        """
        return await self.process_order(customer_id, items)
    
    async def calculate_total(self, items: List[dict]) -> dict:
        """
        Calculate order total including tax and shipping.
        
        Args:
            items: List of items with product_id, quantity, optional size
            
        Returns:
            Order total breakdown
        """
        start_time = datetime.utcnow()
        
        subtotal = Decimal('0')
        item_details = []
        
        for item in items:
            query = "SELECT product_id, name, price FROM products WHERE product_id = %s"
            product = await self.db.execute_one(query, (item['product_id'],))
            
            if product:
                quantity = item.get('quantity', 1)
                item_total = product['price'] * quantity
                subtotal += item_total
                item_details.append({
                    "product_id": product['product_id'],
                    "name": product['name'],
                    "quantity": quantity,
                    "size": item.get('size'),
                    "unit_price": float(product['price']),
                    "total": float(item_total)
                })
        
        # Calculate tax (8.5%) and shipping
        tax = subtotal * Decimal('0.085')
        shipping = Decimal('0') if subtotal >= Decimal('100') else Decimal('9.99')
        total = subtotal + tax + shipping
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="order",
            title=f"Calculate total for {len(items)} items",
            details=f"Subtotal: ${float(subtotal):.2f}, Total: ${float(total):.2f}",
            execution_time_ms=execution_time
        )
        
        return {
            "items": item_details,
            "subtotal": float(subtotal),
            "tax": float(tax),
            "shipping": float(shipping),
            "total": float(total),
            "free_shipping_applied": shipping == 0
        }
    
    async def process_order(self, customer_id: str, items: List[dict]) -> dict:
        """
        Process a new order.
        
        Args:
            customer_id: Customer identifier
            items: List of order items
            
        Returns:
            Order confirmation
        """
        start_time = datetime.utcnow()
        
        # Calculate totals
        totals = await self.calculate_total(items)
        
        # Generate order ID
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Insert order
        insert_order = """
            INSERT INTO orders (order_id, customer_id, status, total_amount)
            VALUES (%s, %s, 'confirmed', %s)
        """
        await self.db.execute(insert_order, (order_id, customer_id, totals['total']))
        
        # Insert order items
        for item in totals['items']:
            insert_item = """
                INSERT INTO order_items (order_id, product_id, size, quantity, unit_price)
                VALUES (%s, %s, %s, %s, %s)
            """
            await self.db.execute(insert_item, (
                order_id,
                item['product_id'],
                item.get('size'),
                item['quantity'],
                item['unit_price']
            ))
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="order",
            title=f"Order processed: {order_id}",
            details=f"Customer: {customer_id}, Total: ${totals['total']:.2f}",
            sql_query="INSERT INTO orders...; INSERT INTO order_items...",
            execution_time_ms=execution_time
        )
        
        # Estimated delivery (5-7 business days)
        delivery_date = datetime.utcnow() + timedelta(days=7)
        
        return {
            "order_id": order_id,
            "status": "confirmed",
            "items": totals['items'],
            "subtotal": totals['subtotal'],
            "tax": totals['tax'],
            "shipping": totals['shipping'],
            "total": totals['total'],
            "estimated_delivery": delivery_date.strftime("%B %d, %Y")
        }


def create_order_agent(
    activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
) -> OrderAgent:
    """Create an Order agent instance."""
    return OrderAgent(activity_callback=activity_callback)
