"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE 1: Single Agent Architecture                                           ║
║ Capacity: 50 orders/day | Response Time: ~2.0s                               ║
║                                                                              ║
║ Pattern: Monolithic agent with direct Aurora PostgreSQL access               ║
║ Perfect for: MVPs, prototypes, weekend projects                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import time
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from rich.console import Console
from rich.panel import Panel

# Setup
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.aurora_db import get_product, check_inventory, create_order

load_dotenv()
console = Console()

# ═══════════════════════════════════════════════════════════════════════════
# BEDROCK MODEL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
# Using Claude Sonnet 4.5 via Amazon Bedrock for LLM inference
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID"),
    region_name=os.getenv("BEDROCK_REGION", "us-west-2"),
    temperature=0.3  # Lower temperature for consistent responses
)

# ═══════════════════════════════════════════════════════════════════════════
# AGENT TOOLS - Direct Aurora Database Access
# ═══════════════════════════════════════════════════════════════════════════
# Each tool directly calls Aurora PostgreSQL via psycopg3
# This is simple but creates tight coupling between agent and database

@tool
def identify_product_from_stream(stream_id: str) -> dict:
    """
    Find product from live stream context.
    
    ARCHITECTURE NOTE: Direct database call via psycopg3
    - Simple and fast for low volume
    - Tight coupling to database schema
    - Manual connection management required
    """
    print(f"🔍 Searching stream {stream_id}...")
    
    try:
        # Direct Aurora query via psycopg3
        product = get_product("shoe_001")
        
        if not product:
            return {"error": "Product not found"}
        
        print(f"✅ Found: {product['name']}")
        
        return {
            "product_id": product['product_id'],
            "name": product['name'],
            "price": float(product['price']),
            "brand": product['brand'],
            "description": product['description']
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

@tool
def check_product_inventory(product_id: str, size: str = None) -> dict:
    """
    Check real-time inventory availability.
    
    ARCHITECTURE NOTE: Another direct database call
    - Each tool manages its own database interaction
    - No abstraction layer
    - Works great for 50 orders/day
    """
    print(f"📦 Checking inventory for size {size}...")
    
    try:
        # Direct Aurora query
        inventory = check_inventory(product_id, size)
        print(f"✅ Inventory checked")
        return inventory
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

@tool
def calculate_order_total(product_id: str) -> dict:
    """
    Calculate price with tax and shipping.
    
    BUSINESS LOGIC:
    - 8% sales tax
    - Free shipping over $50
    - $9.99 flat rate shipping under $50
    """
    print("💰 Calculating total...")
    
    try:
        product = get_product(product_id)
        if not product:
            return {"error": "Product not found"}
        
        base_price = float(product['price'])
        tax = round(base_price * 0.08, 2)
        shipping = 0.00 if base_price > 50 else 9.99
        total = round(base_price + tax + shipping, 2)
        
        print(f"✅ Total: ${total}")
        
        return {
            "base_price": base_price,
            "tax": tax,
            "shipping": shipping,
            "total": total
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

@tool
def process_customer_order(product_id: str, customer_id: str, size: str, total_amount: float) -> dict:
    """
    Create order and update inventory.
    
    ARCHITECTURE NOTE: Transactional operation
    - Creates order record
    - Decrements inventory
    - All in single database transaction
    """
    print("🛒 Processing order...")
    
    try:
        product = get_product(product_id)
        base_price = float(product['price'])
        tax = round(base_price * 0.08, 2)
        
        # Single transaction: create order + update inventory
        order = create_order(
            product_id=product_id,
            customer_id=customer_id,
            size=size,
            base_price=base_price,
            tax=tax,
            total=total_amount,
            stream_id="fitness_stream_morning_001",
            processed_by="SingleAgent"
        )
        
        print(f"✅ Order created: {order['order_id']}")
        
        return {
            "order_id": order['order_id'],
            "status": order['status'],
            "total": float(order['total_amount']),
            "estimated_delivery": "2-3 business days"
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════
# SINGLE AGENT DEFINITION
# ═══════════════════════════════════════════════════════════════════════════
# One agent handles entire workflow: search → inventory → calculate → order
# ReAct pattern: Reason → Act → Observe loop

clickshop_agent = Agent(
    model=bedrock_model,
    tools=[
        identify_product_from_stream,     # Tool 1: Product discovery
        check_product_inventory,          # Tool 2: Inventory check
        calculate_order_total,            # Tool 3: Price calculation
        process_customer_order            # Tool 4: Order processing
    ],
    system_prompt="""You are ClickShop AI - helping customers buy from live streams.

WORKFLOW:
1. Identify product from stream
2. Ask customer for size
3. Check inventory
4. Calculate total
5. Process order

Be friendly and use emojis. Stream ID: fitness_stream_morning_001"""
)

# ═══════════════════════════════════════════════════════════════════════════
# DEMO RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_interactive_demo():
    """Run Phase 1 demo"""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🛍️  PHASE 1: Single Agent[/bold cyan]\n"
        "[yellow]Monolithic architecture with direct Aurora access[/yellow]\n"
        "[green]Capacity: 50 orders/day | Response: ~2.0s[/green]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]📊 Architecture:[/bold]")
    console.print("  • 1 Agent (monolithic)")
    console.print("  • 4 Tools (direct DB access)")
    console.print("  • Aurora PostgreSQL (psycopg3)")
    console.print("  • Tight coupling\n")
    
    # Get input
    console.print("[dim]Press Enter for default: 'I want those running shoes!'[/dim]")
    customer_request = input("👤 You: ").strip() or "I want those running shoes!"
    console.print(f"[yellow]👤 You: {customer_request}[/yellow]\n")
    
    console.print("[dim]Press Enter for default: 'CUST-123'[/dim]")
    customer_id = input("👤 Customer ID: ").strip() or "CUST-123"
    console.print(f"[yellow]Using: {customer_id}[/yellow]\n")
    
    # Process with agent
    full_request = f"{customer_request} (Customer ID: {customer_id})"
    response = clickshop_agent(full_request)
    
    # Handle size follow-up
    if "size" in str(response).lower():
        console.print()
        console.print("[dim]Press Enter for default: 'Size 10'[/dim]")
        size_input = input("👤 You: ").strip() or "Size 10"
        console.print(f"[yellow]👤 You: {size_input}[/yellow]\n")
        clickshop_agent(size_input)
    
    console.print("\n[bold green]✅ Phase 1 Complete![/bold green]")
    console.print("\n[bold]Key Characteristics:[/bold]")
    console.print("  ✓ Simple and fast to build")
    console.print("  ✓ Direct database access")
    console.print("  ✓ Perfect for MVPs")
    console.print("  ⚠ Tight coupling")
    console.print("  ⚠ Limited scalability\n")

if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]\n")
