"""
Phase 1 Agent - Single agent with direct database access.

Implements the MVP pattern using:
- Strands SDK (strands-agents) for agent framework
- Claude Opus 4.7 via Amazon Bedrock (cross-region inference)
- RDS Data API for Aurora PostgreSQL access
- Tools for package lookup, availability check, price calculation, booking processing

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

from backend.db.rds_data_client import get_rds_data_client


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
    Phase 1 travel concierge with direct database access.
    
    Uses Strands SDK with Claude Opus 4.7 via Bedrock (cross-region inference).
    Connects to Aurora PostgreSQL using RDS Data API.
    
    Requirements:
    - 9.1: Implemented using Strands SDK
    - 9.2: Uses Claude Opus 4.7 via Amazon Bedrock
    - 9.3: Connects to Aurora PostgreSQL using RDS Data API
    - 9.4: Has tools for package lookup, availability check, price calculation, booking processing
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
        
        # Initialize Bedrock model - Claude Opus 4.7 (cross-region inference)
        # Requirement 9.2
        self.model = BedrockModel(
            model_id="global.anthropic.claude-opus-4-7-v1",
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
        """Get the system prompt for the travel concierge."""
        return """You are a helpful travel concierge for Meridian.

Your capabilities:
- Look up trip package details by ID or search the catalog
- Check departure availability and duration options
- Calculate booking totals with tax and fees
- Process bookings for travelers

Guidelines:
- Be friendly and helpful
- Provide accurate trip information (destination, operator, price per person)
- Recommend packages based on traveler needs
- Always confirm booking details before processing
- If a package is sold out, suggest alternatives

Trip types in the catalog:
- City Breaks
- Beach & Resort
- Adventure & Outdoors
- Wellness & Luxury
- Family Trips
- Business Travel"""
    
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
    async def _lookup_product(self, package_id: str) -> dict:
        """
        Look up a trip package by its ID.

        Args:
            package_id: Package identifier (e.g., 'CTY-002')
        """
        start_time = datetime.utcnow()

        query = """
            SELECT package_id, name, operator, price_per_person, description,
                   image_url, trip_type, destination, durations, availability
            FROM trip_packages
            WHERE package_id = %s
        """

        result = await self.db.execute_one(query, (package_id,))

        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        self._log_activity(
            activity_type="search",
            title=f"Package lookup: {package_id}",
            details=f"Found: {result['name'] if result else 'Not found'}",
            sql_query=query.strip(),
            execution_time_ms=execution_time
        )

        if not result:
            return {"error": f"Package {package_id} not found"}

        result['price_per_person'] = float(result['price_per_person'])
        return dict(result)
    
    @tool
    async def _search_products(
        self,
        query: str,
        trip_type: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        Search trip packages by text query.

        Args:
            query: Search terms (e.g., 'Tokyo', 'beach resort')
            trip_type: Optional trip type filter
            limit: Maximum number of results (default 5)
        """
        start_time = datetime.utcnow()

        sql = """
            SELECT package_id, name, operator, price_per_person, description,
                   image_url, trip_type, destination, durations
            FROM trip_packages
            WHERE (name ILIKE %s OR description ILIKE %s OR operator ILIKE %s
                   OR destination ILIKE %s)
        """
        params = [f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]

        if trip_type:
            sql += " AND trip_type = %s"
            params.append(trip_type)

        sql += " LIMIT %s"
        params.append(limit)

        results = await self.db.execute(sql, tuple(params))

        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        self._log_activity(
            activity_type="search",
            title=f"Package search: '{query}'",
            details=f"Found {len(results)} packages" + (f" in {trip_type}" if trip_type else ""),
            sql_query=sql.strip(),
            execution_time_ms=execution_time
        )

        for r in results:
            r['price_per_person'] = float(r['price_per_person'])

        return [dict(r) for r in results]
    
    @tool
    async def _check_inventory(
        self,
        package_id: str,
        duration: Optional[str] = None
    ) -> dict:
        """
        Check departure availability for a trip package.

        Args:
            package_id: Package identifier
            duration: Optional duration key (e.g., '7 nights')
        """
        start_time = datetime.utcnow()

        query = """
            SELECT package_id, name, durations, availability
            FROM trip_packages
            WHERE package_id = %s
        """

        result = await self.db.execute_one(query, (package_id,))

        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        self._log_activity(
            activity_type="availability",
            title=f"Availability check: {package_id}" + (f" duration {duration}" if duration else ""),
            sql_query=query.strip(),
            execution_time_ms=execution_time
        )

        if not result:
            return {"error": f"Package {package_id} not found"}

        availability = result.get('availability') or {}

        if duration:
            slots = availability.get(duration, 0)
            return {
                "package_id": package_id,
                "duration": duration,
                "slots": slots,
                "available": slots > 0,
            }

        total = sum(availability.values()) if isinstance(availability, dict) else 0
        return {
            "package_id": package_id,
            "total_slots": total,
            "availability_by_duration": availability,
            "available": total > 0,
            "durations": result.get('durations'),
        }
    
    @tool
    async def _calculate_total(self, items: List[dict]) -> dict:
        """
        Calculate order total including tax and shipping.
        
        Args:
            items: List of items with package_id, travelers_count, and optional duration
                   Example: [{"package_id": "CTY-002", "travelers_count": 2, "duration": "7 nights"}]
            
        Returns:
            Order total breakdown with subtotal, tax, shipping, and total
        """
        start_time = datetime.utcnow()
        
        subtotal = Decimal('0')
        item_details = []
        
        for item in items:
            query = "SELECT package_id, name, price_per_person FROM trip_packages WHERE package_id = %s"
            package = await self.db.execute_one(query, (item['package_id'],))

            if package:
                travelers = item.get('travelers_count', item.get('quantity', 1))
                item_total = package['price_per_person'] * travelers
                subtotal += item_total
                item_details.append({
                    "package_id": package['package_id'],
                    "name": package['name'],
                    "travelers_count": travelers,
                    "duration": item.get('duration'),
                    "unit_price": float(package['price_per_person']),
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
        Process a new booking for a traveler.

        Args:
            traveler_id: Traveler identifier
            items: List of items with package_id, travelers_count, optional duration
        """
        start_time = datetime.utcnow()

        totals = await self._calculate_total(items)

        booking_id = f"BKG-{uuid.uuid4().hex[:8].upper()}"

        insert_booking = """
            INSERT INTO bookings (booking_id, traveler_id, status, total_amount)
            VALUES (%s, %s, 'confirmed', %s)
        """
        await self.db.execute(insert_booking, (booking_id, customer_id, totals['total']))

        for item in totals['items']:
            insert_line = """
                INSERT INTO booking_lines (booking_id, package_id, duration, travelers_count, unit_price)
                VALUES (%s, %s, %s, %s, %s)
            """
            await self.db.execute(insert_line, (
                booking_id,
                item['package_id'],
                item.get('duration'),
                item['travelers_count'],
                item['unit_price']
            ))

        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        self._log_activity(
            activity_type="order",
            title=f"Booking processed: {booking_id}",
            details=f"Traveler: {customer_id}, Total: ${totals['total']:.2f}",
            sql_query="INSERT INTO bookings...; INSERT INTO booking_lines...",
            execution_time_ms=execution_time
        )

        from datetime import timedelta
        departure_window = datetime.utcnow() + timedelta(days=30)

        return {
            "booking_id": booking_id,
            "status": "confirmed",
            "items": totals['items'],
            "subtotal": totals['subtotal'],
            "tax": totals['tax'],
            "shipping": totals['shipping'],
            "total": totals['total'],
            "estimated_departure": departure_window.strftime("%B %d, %Y")
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
