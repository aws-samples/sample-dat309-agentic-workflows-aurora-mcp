"""
Phase 1 Agent - Single agent with direct database access.

Implements the MVP pattern using:
- Strands SDK (strands-agents) for agent framework
- Claude Sonnet 4.5 via Amazon Bedrock (cross-region inference)
- RDS Data API for Aurora PostgreSQL access
- Tools for product lookup, inventory check, price calculation, order processing

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
"""

import os
import json
import uuid
from datetime import datetime
from typing import Callable, Any, Optional, List
from decimal import Decimal

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


class AgentResponse(BaseModel):
    """Response from agent processing."""
    message: str
    products: Optional[List[dict]] = None
    order: Optional[dict] = None


class Phase1Agent:
    """
    Phase 1 Shopping Agent with direct database access.
    
    Uses Strands SDK with Claude Sonnet 4.5 via Bedrock (cross-region inference).
    Connects to Aurora PostgreSQL using RDS Data API.
    
    Requirements:
    - 9.1: Implemented using Strands SDK
    - 9.2: Uses Claude Sonnet 4.5 via Amazon Bedrock
    - 9.3: Connects to Aurora PostgreSQL using RDS Data API
    - 9.4: Has tools for product lookup, inventory check, price calculation, order processing
    - 9.5: Logs all database queries and execution times
    """
    
    def __init__(self, activity_callback: Optional[Callable[[ActivityEntry], Any]] = None):
        """
        Initialize Phase 1 agent.
        
        Args:
            activity_callback: Optional callback for reporting agent activities
        """
        self.activity_callback = activity_callback or (lambda x: None)
        self.db = get_rds_data_client()
        
        # Initialize Bedrock model - Claude Sonnet 4.5 (cross-region inference)
        # Requirement 9.2
        self.model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        )
        
        # Create agent with tools
        self.agent = Agent(
            model=self.model,
            tools=[
                self._lookup_product,
                self._search_products,
                self._check_inventory,
                self._calculate_total,
                self._process_order
            ],
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the shopping assistant."""
        return """You are a helpful shopping assistant for AgentStride, an athletic and fitness equipment store.

Your capabilities:
- Look up product details by ID or search for products
- Check inventory and available sizes
- Calculate order totals with tax and shipping
- Process orders for customers

Guidelines:
- Be friendly and helpful
- Provide accurate product information
- Recommend products based on customer needs
- Always confirm order details before processing
- If a product is out of stock, suggest alternatives

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
        """Log an activity entry. Requirement 9.5."""
        entry = ActivityEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            activity_type=activity_type,
            title=title,
            details=details,
            sql_query=sql_query,
            execution_time_ms=execution_time_ms,
            agent_name="Phase1Agent"
        )
        self.activity_callback(entry)
    
    @tool
    async def _lookup_product(self, product_id: str) -> dict:
        """
        Look up a product by its ID.
        
        Args:
            product_id: The product identifier (e.g., 'RUN-001')
            
        Returns:
            Product details including name, price, description, and availability
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
            title=f"Product lookup: {product_id}",
            details=f"Found: {result['name'] if result else 'Not found'}",
            sql_query=query.strip(),
            execution_time_ms=execution_time
        )
        
        if not result:
            return {"error": f"Product {product_id} not found"}
        
        # Convert Decimal to float for JSON serialization
        result['price'] = float(result['price'])
        return dict(result)
    
    @tool
    async def _search_products(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Search for products by text query.
        
        Args:
            query: Search terms (e.g., 'running shoes', 'lightweight')
            category: Optional category filter
            limit: Maximum number of results (default 5)
            
        Returns:
            List of matching products
        """
        start_time = datetime.utcnow()
        
        sql = """
            SELECT product_id, name, brand, price, description, 
                   image_url, category, available_sizes
            FROM products
            WHERE (name ILIKE %s OR description ILIKE %s OR brand ILIKE %s)
        """
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if category:
            sql += " AND category = %s"
            params.append(category)
        
        sql += " LIMIT %s"
        params.append(limit)
        
        results = await self.db.execute(sql, tuple(params))
        
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        self._log_activity(
            activity_type="search",
            title=f"Product search: '{query}'",
            details=f"Found {len(results)} products" + (f" in {category}" if category else ""),
            sql_query=sql.strip(),
            execution_time_ms=execution_time
        )
        
        # Convert Decimal to float
        for r in results:
            r['price'] = float(r['price'])
        
        return [dict(r) for r in results]
    
    @tool
    async def _check_inventory(
        self,
        product_id: str,
        size: Optional[str] = None
    ) -> dict:
        """
        Check inventory status for a product.
        
        Args:
            product_id: The product identifier
            size: Optional size to check (for sized products like shoes/apparel)
            
        Returns:
            Inventory status with quantity and availability
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
                "size": size,
                "quantity": quantity,
                "in_stock": quantity > 0
            }
        else:
            # Return total inventory across all sizes/variants
            if isinstance(inventory, dict):
                if 'quantity' in inventory:
                    total = inventory['quantity']
                else:
                    total = sum(inventory.values())
            else:
                total = 0
            
            return {
                "product_id": product_id,
                "total_quantity": total,
                "inventory_by_size": inventory,
                "in_stock": total > 0
            }
    
    @tool
    async def _calculate_total(self, items: List[dict]) -> dict:
        """
        Calculate order total including tax and shipping.
        
        Args:
            items: List of items with product_id, quantity, and optional size
                   Example: [{"product_id": "RUN-001", "quantity": 1, "size": "10"}]
            
        Returns:
            Order total breakdown with subtotal, tax, shipping, and total
        """
        start_time = datetime.utcnow()
        
        subtotal = Decimal('0')
        item_details = []
        
        for item in items:
            query = "SELECT product_id, name, price FROM products WHERE product_id = %s"
            product = await self.db.execute_one(query, (item['product_id'],))
            
            if product:
                item_total = product['price'] * item.get('quantity', 1)
                subtotal += item_total
                item_details.append({
                    "product_id": product['product_id'],
                    "name": product['name'],
                    "quantity": item.get('quantity', 1),
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
    
    @tool
    async def _process_order(
        self,
        customer_id: str,
        items: List[dict]
    ) -> dict:
        """
        Process a new order for a customer.
        
        Args:
            customer_id: Customer identifier
            items: List of items with product_id, quantity, and optional size
            
        Returns:
            Order confirmation with order_id, status, and estimated delivery
        """
        start_time = datetime.utcnow()
        
        # Calculate totals first
        totals = await self._calculate_total(items)
        
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
        
        # Calculate estimated delivery (5-7 business days)
        from datetime import timedelta
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
        
        self._log_activity(
            activity_type="search",
            title="Processing customer message",
            details=f"Message: {message[:100]}..."
        )
        
        # Run the agent
        response = await self.agent.run(message)
        
        # Parse response for products and orders
        # The agent's response is the final message
        return AgentResponse(
            message=str(response),
            products=None,  # Would be populated from tool results
            order=None  # Would be populated from order processing
        )


def create_phase1_agent(
    activity_callback: Optional[Callable[[ActivityEntry], Any]] = None
) -> Phase1Agent:
    """
    Create a Phase 1 agent instance.
    
    Args:
        activity_callback: Optional callback for activity updates
        
    Returns:
        Configured Phase1Agent instance
    """
    return Phase1Agent(activity_callback=activity_callback)
