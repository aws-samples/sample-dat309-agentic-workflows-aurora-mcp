"""
ClickShop - Month 1: Single Agent with Aurora PostgreSQL (Interactive with Strands Logging)
Two friends built this in a weekend using "vibe coding"
50 orders/day, all data in Aurora from day one
"""
import os
import time
import logging
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from strands.handlers.callback_handler import PrintingCallbackHandler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import Aurora database operations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.aurora_db import (
    get_product,
    get_all_products,
    check_inventory,
    create_order,
    log_agent_action,
    get_database_stats,
    get_recent_orders
)

load_dotenv()
console = Console()

# ============================================================================
# CONFIGURE STRANDS LOGGING
# ============================================================================

logging.getLogger("strands").setLevel(logging.WARNING)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Custom logger for our tools
tool_logger = logging.getLogger("clickshop.tools")
tool_logger.setLevel(logging.INFO)

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
    region_name=os.getenv("BEDROCK_REGION", "us-west-2"),
    temperature=0.3,
)

# ============================================================================
# CLICKSHOP TOOLS WITH STRANDS LOGGING
# ============================================================================

@tool
def identify_product_from_stream(stream_id: str, timestamp: str = "now") -> dict:
    """
    Identify which product the customer is referring to from a live stream.
    Uses Aurora database to fetch real product information.
    
    Args:
        stream_id: The ID of the live stream
        timestamp: When the user made the request (default: "now")
    
    Returns:
        Product details including ID, name, price, and availability
    """
    tool_logger.info(f"🔍 Searching stream {stream_id} for product...")
    time.sleep(0.3)
    
    start_time = time.time()
    
    try:
        tool_logger.info("📊 Querying Aurora database (products table)")
        product = get_product("shoe_001")
        
        if not product:
            tool_logger.error("❌ Product not found in database")
            return {"error": "Product not found in database"}
        
        tool_logger.info(f"✅ Product identified: {product['brand']} {product['name']}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "identify_product", duration_ms, "success",
                        metadata={"stream_id": stream_id})
        
        return {
            "product_id": product['product_id'],
            "name": product['name'],
            "price": float(product['price']),
            "brand": product['brand'],
            "category": product['category'],
            "description": product['description']
        }
    
    except Exception as e:
        tool_logger.error(f"❌ Error identifying product: {e}")
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "identify_product", duration_ms, "error", error_message=str(e))
        return {"error": str(e)}

@tool
def check_product_inventory(product_id: str, size: str = None) -> dict:
    """
    Check if a product is available in the requested size.
    Queries Aurora database for real-time inventory.
    
    Args:
        product_id: The product to check
        size: The size requested by customer (optional for non-sized items)
    
    Returns:
        Availability status, quantity, and available sizes
    """
    tool_logger.info(f"📦 Checking inventory for size {size if size else 'any'}...")
    time.sleep(0.2)
    
    start_time = time.time()
    
    try:
        tool_logger.info("📊 Querying Aurora database (inventory check)")
        inventory = check_inventory(product_id, size)
        
        if inventory.get('in_stock'):
            qty = inventory.get('quantity', 0)
            tool_logger.info(f"✅ In stock: {qty} units available")
        else:
            tool_logger.warning(f"⚠️  Out of stock for size {size}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "check_inventory", duration_ms, "success")
        
        return inventory
    
    except Exception as e:
        tool_logger.error(f"❌ Error checking inventory: {e}")
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "check_inventory", duration_ms, "error", error_message=str(e))
        return {"error": str(e)}

@tool
def calculate_order_total(product_id: str, quantity: int = 1) -> dict:
    """
    Calculate the total price including tax and shipping.
    Fetches current price from Aurora database.
    
    Args:
        product_id: The product being purchased
        quantity: Number of items (default: 1)
    
    Returns:
        Price breakdown with base, tax, shipping, and total
    """
    tool_logger.info("💰 Calculating order total...")
    time.sleep(0.2)
    
    start_time = time.time()
    
    try:
        tool_logger.info("📊 Querying Aurora database (price lookup)")
        product = get_product(product_id)
        
        if not product:
            return {"error": "Product not found"}
        
        base_price = float(product['price']) * quantity
        tax = round(base_price * 0.08, 2)  # 8% tax
        shipping = 0.00 if base_price > 50 else 9.99
        total = round(base_price + tax + shipping, 2)
        
        tool_logger.info(f"✅ Total calculated: ${base_price} + ${tax} tax + ${shipping} shipping = ${total}")
        
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "calculate_total", duration_ms, "success")
        
        return {
            "base_price": base_price,
            "tax": tax,
            "shipping": shipping,
            "total": total,
            "quantity": quantity
        }
    
    except Exception as e:
        tool_logger.error(f"❌ Error calculating total: {e}")
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "calculate_total", duration_ms, "error", error_message=str(e))
        return {"error": str(e)}

@tool
def process_customer_order(
    product_id: str,
    customer_id: str,
    size: str,
    total_amount: float
) -> dict:
    """
    Process the customer's order and store it in Aurora database.
    Updates inventory and creates order record.
    
    Args:
        product_id: Product being ordered
        customer_id: Customer placing the order
        size: Size selected
        total_amount: Total amount calculated
    
    Returns:
        Order confirmation with order ID and details
    """
    tool_logger.info("🛒 Processing customer order...")
    time.sleep(0.3)
    
    start_time = time.time()
    
    try:
        # Calculate breakdown
        product = get_product(product_id)
        base_price = float(product['price'])
        tax = round(base_price * 0.08, 2)
        
        tool_logger.info("📊 Writing to Aurora database (orders table)")
        
        # Create order in database
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
        
        tool_logger.info(f"✅ Order created: {order['order_id']}")
        
        tool_logger.info("📦 Updating inventory (decrementing stock)")
        time.sleep(0.1)
        tool_logger.info("✅ Inventory updated")
        
        tool_logger.info("📈 Logging analytics (performance tracking)")
        
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "process_order", duration_ms, "success", 
                        metadata={"order_id": order['order_id']})
        
        tool_logger.info(f"✅ Analytics logged (execution time: {duration_ms}ms)")
        
        return {
            "order_id": order['order_id'],
            "status": order['status'],
            "total": float(order['total_amount']),
            "estimated_delivery": "2-3 business days",
            "tracking_available": True,
            "created_at": str(order['created_at'])
        }
    
    except Exception as e:
        tool_logger.error(f"❌ Error processing order: {e}")
        duration_ms = int((time.time() - start_time) * 1000)
        log_agent_action("SingleAgent", "process_order", duration_ms, "error", error_message=str(e))
        return {"error": str(e)}

# ============================================================================
# CLICKSHOP SINGLE AGENT WITH CALLBACK HANDLER
# ============================================================================

clickshop_agent = Agent(
    model=bedrock_model,
    tools=[
        identify_product_from_stream,
        check_product_inventory,
        calculate_order_total,
        process_customer_order
    ],
    callback_handler=PrintingCallbackHandler(),
    system_prompt="""You are the ClickShop AI assistant helping customers purchase products 
    from live fitness streams. 
    
    You have access to a real Aurora PostgreSQL database with product catalog and inventory.
    
    Your workflow:
    1. Identify what product the customer wants from the stream
    2. Ask for necessary information (like size for shoes/apparel) in a friendly way
    3. Check inventory availability in real-time
    4. Calculate the total price with tax
    5. Process the order and provide confirmation
    
    Be friendly, enthusiastic, and conversational. Use emojis occasionally.
    Always confirm details before completing orders.
    The stream_id is: fitness_stream_morning_001
    All your actions are logged to the database for analytics."""
)

# ============================================================================
# INTERACTIVE DEMO FUNCTION
# ============================================================================

def run_interactive_demo():
    """Run the Month 1 Single Agent demo - Interactive with Strands logging"""
    
    # Header
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🛍️  ClickShop - Month 1: Single Agent[/bold cyan]\n"
        "[yellow]Two friends, one weekend, one agent, Aurora from day one[/yellow]",
        border_style="cyan"
    ))
    
    # Show database stats
    stats = get_database_stats()
    console.print("\n[bold]📊 Aurora Database Status:[/bold]")
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column(style="cyan")
    stats_table.add_column(style="green")
    stats_table.add_row("Products in catalog", str(stats['total_products']))
    stats_table.add_row("Total orders", str(stats['total_orders']))
    stats_table.add_row("Orders today", str(stats['orders_today']))
    stats_table.add_row("Revenue today", f"${stats['revenue_today']:.2f}")
    console.print(stats_table)
    
    # Interactive Scenario
    console.print("\n[bold magenta]📺 Live Stream Scenario:[/bold magenta]")
    console.print("You're watching [bold cyan]@FitnessGuru's[/bold cyan] live stream")
    console.print("Stream ID: [yellow]fitness_stream_morning_001[/yellow]")
    console.print("They're showcasing the [bold]Nike Air Zoom Pegasus[/bold] running shoes")
    console.print("Current viewers: [green]2,847[/green] | Duration: [yellow]23:15[/yellow]\n")
    
    console.print("[dim]─────────────────────────────────────────────────────────────────[/dim]\n")
    
    # Get customer input
    console.print("[bold green]💬 Chat with ClickShop Agent![/bold green]")
    console.print("[dim]Type your message (or press Enter to use: 'I want those shoes!')[/dim]\n")
    
    customer_request = input("👤 You: ").strip()
    
    # Use default if no input
    if not customer_request:
        customer_request = "I want those running shoes from the stream! They look perfect for my morning runs."
        console.print(f"[yellow]👤 You: {customer_request}[/yellow]")
    
    # Get customer ID
    console.print("\n[bold green]Customer ID:[/bold green]")
    console.print("[dim]Enter your customer ID (or press Enter for: '123')[/dim]\n")
    customer_id = input("👤 Customer ID: ").strip()
    if not customer_id:
        customer_id = "123"
        console.print(f"[yellow]Using customer ID: {customer_id}[/yellow]")
    
    console.print()
    
    # Process with agent
    response = clickshop_agent(customer_request)
    response_text = str(response)
    
    # Check if agent is asking for size (interactive follow-up)
    if "size" in response_text.lower() and "?" in response_text:
        console.print("\n[dim]─────────────────────────────────────────────────────────────────[/dim]\n")
        console.print("[bold green]💬 Continue the conversation:[/bold green]")
        console.print("[dim]Type your response (or press Enter for: 'Size 10 please')[/dim]\n")
        
        size_input = input("👤 You: ").strip()
        
        if not size_input:
            size_input = "Size 10 please"
            console.print(f"[yellow]👤 You: {size_input}[/yellow]")
        
        console.print()
        follow_up = clickshop_agent(size_input)
    
    # Show transaction complete
    console.print("\n[dim]─────────────────────────────────────────────────────────────────[/dim]")
    console.print("\n[bold green]✅ Transaction Complete![/bold green]")
    console.print(f"[cyan]Customer ID: {customer_id}[/cyan]\n")
    
    # Show latest order
    recent_orders = get_recent_orders(limit=1)
    
    if recent_orders:
        latest_order = recent_orders[0]
        console.print("[bold]📦 Order Confirmation:[/bold]")
        order_table = Table(show_header=False, box=None, border_style="green")
        order_table.add_column(style="cyan", width=20)
        order_table.add_column(style="green")
        order_table.add_row("Order ID", f"[bold]{latest_order['order_id']}[/bold]")
        order_table.add_row("Product", latest_order['product_name'])
        order_table.add_row("Brand", latest_order['brand'])
        order_table.add_row("Size", latest_order['size'] or "N/A")
        order_table.add_row("Total", f"[bold]${latest_order['total_amount']}[/bold]")
        order_table.add_row("Status", f"[bold green]{latest_order['status'].upper()}[/bold green]")
        order_table.add_row("Delivery", "2-3 business days")
        console.print(order_table)
        console.print()
    
    # Performance metrics
    console.print("[bold]⏱️  Month 1 Architecture:[/bold]")
    metrics_table = Table(show_header=False, box=None)
    metrics_table.add_column(style="cyan", width=25)
    metrics_table.add_column(style="green")
    metrics_table.add_row("Response time", "~2 seconds")
    metrics_table.add_row("Daily capacity", "50 orders/day")
    metrics_table.add_row("Database", "Aurora PostgreSQL")
    metrics_table.add_row("Architecture", "Single Agent")
    metrics_table.add_row("Development team", "2 friends 🚀")
    metrics_table.add_row("Development time", "1 weekend")
    console.print(metrics_table)
    
    console.print("\n[bold yellow]💾 All operations persisted in Aurora PostgreSQL![/bold yellow]")
    console.print("[dim]Query: SELECT * FROM orders ORDER BY created_at DESC LIMIT 5;[/dim]\n")

if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted. Thanks for trying ClickShop![/yellow]\n")
    except Exception as e:
        console.print(f"\n\n[bold red]Error:[/bold red] {e}\n")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        console.print("\n[dim]Check your .env file and Aurora connection[/dim]\n")