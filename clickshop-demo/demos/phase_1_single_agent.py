"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE 1: Single Agent Architecture                                           ║
║ Capacity: 50 orders/day | Response Time: ~2.0s                               ║
║                                                                              ║
║ Pattern: Monolithic agent with direct Aurora PostgreSQL access               ║
║ When to use: MVPs, prototypes, validating product-market fit                 ║
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
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID"),
    region_name=os.getenv("BEDROCK_REGION", "us-west-2"),
    temperature=0.3  # Lower = more consistent, Higher = more creative
)

# ═══════════════════════════════════════════════════════════════════════════
# AGENT TOOLS - Direct Aurora Database Access
# ═══════════════════════════════════════════════════════════════════════════
# ARCHITECTURE DECISION: Start simple with direct database calls
# Why? Ship fast, validate use case, avoid premature abstraction
# When to evolve? >1K orders/day or need multi-region support

@tool
def identify_product_from_stream(stream_id: str) -> dict:
    """
    Find product from live stream context.
    
    PATTERN: Direct database query via psycopg3
    - Fastest path: ~50ms query time
    - Simplest code: No abstraction layers
    - Trade-off: Tight coupling to Aurora schema
    
    Perfect for Phase 1. Refactor when you need portability.
    """
    print(f"🔍 Searching stream {stream_id}...")
    
    try:
        # Direct Aurora query - no MCP, no API layer
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
    
    SCALING TIP: This works for 50 orders/day
    At 1K+ orders/day, add caching (Redis) to reduce DB load 60-80%
    """
    print(f"📦 Checking inventory for size {size}...")
    
    try:
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
    - $9.99 flat rate under $50
    
    Note: This is stateless calculation - could move to client side
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
    
    TRANSACTION PATTERN: Single DB call handles both writes
    - Creates order record
    - Decrements inventory
    - Atomic operation (both succeed or both fail)
    
    PRODUCTION TIP: Add idempotency key to prevent duplicate orders
    """
    print("🛒 Processing order...")
    
    try:
        product = get_product(product_id)
        base_price = float(product['price'])
        tax = round(base_price * 0.08, 2)
        
        # Single transaction ensures consistency
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
# PATTERN: Monolithic agent with 4 tools
# Why start here? 
# - Ship in a weekend
# - Validate product-market fit
# - No premature optimization
#
# When to evolve?
# - >1K orders/day (add caching, optimize)
# - Need portability (add MCP layer)
# - Complex workflows (add specialized agents)

clickshop_agent = Agent(
    model=bedrock_model,
    tools=[
        identify_product_from_stream,     # Tool 1: Product discovery
        check_product_inventory,          # Tool 2: Inventory check
        calculate_order_total,            # Tool 3: Price calculation
        process_customer_order            # Tool 4: Order processing
    ],
    system_prompt="""You are ClickShop AI, an intelligent shopping assistant for live-stream commerce.

WORKFLOW:
1. Identify the product from the live stream context
2. Request the customer's preferred size
3. Verify inventory availability for the selected size
4. Calculate the order total including tax and shipping
5. Process and confirm the customer order

IMPORTANT: The customer ID is always provided in the initial request. Do not request it again.

Maintain a professional yet approachable tone throughout the interaction.
Default stream context: fitness_stream_morning_001"""
)

# ═══════════════════════════════════════════════════════════════════════════
# DEMO RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_interactive_demo():
    """Run Phase 1 demo"""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🛍️  PHASE 1: Single Agent[/bold cyan]\n"
        "[yellow]Direct Aurora access - built in a weekend[/yellow]\n"
        "[green]Capacity: 50 orders/day | Response: ~2.0s[/green]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]🏗️  Phase 1 Architecture:[/bold]")
    console.print("  • 1 Agent (handles entire workflow)")
    console.print("  • 4 Tools (direct Aurora access)")
    console.print("  • psycopg3 connection pooling")
    console.print("  • Aurora PostgreSQL single region\n")
    
    console.print("[bold]✅ Why Start Here:[/bold]")
    console.print("  • Ship in days, not weeks")
    console.print("  • Validate product-market fit")
    console.print("  • Simplest possible architecture")
    console.print("  • Fastest response time (~2.0s)\n")
    
    console.print("[bold]⚠️  When to Evolve:[/bold]")
    console.print("  • >1K orders/day (add caching)")
    console.print("  • Need portability (add MCP)")
    console.print("  • Complex workflows (multi-agent)\n")
    
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
    
    console.print("\n[bold]🎯 Phase 1 Characteristics:[/bold]")
    console.print("  ✓ Fast to build (weekend project)")
    console.print("  ✓ Fast response time (~2.0s)")
    console.print("  ✓ Perfect for MVPs and prototypes")
    console.print("  ✓ Direct control over queries")
    console.print("  ⚠️  Tight coupling to Aurora")
    console.print("  ⚠️  Limited to 50 orders/day")
    console.print("  ⚠️  Manual connection management\n")
    
    console.print("[bold]🚀 Next Step:[/bold]")
    console.print("  When traffic grows, see Phase 2 (MCP) for 100x scaling\n")

if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]\n")