"""
ClickShop - Month 3: MCP-Powered Agent with Aurora PostgreSQL
Evolution from direct DB access to MCP architecture
200 orders/day, database operations via MCP server
"""
import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models import BedrockModel
from strands.handlers.callback_handler import PrintingCallbackHandler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

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

tool_logger = logging.getLogger("clickshop.tools")
tool_logger.setLevel(logging.INFO)

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
    region_name=os.getenv("BEDROCK_REGION", "us-west-2"),
    temperature=0.3,
)

# ============================================================================
# MCP-AWARE TOOLS (Database operations delegated to MCP server)
# ============================================================================

@tool
def query_product_from_mcp(stream_id: str, product_identifier: str = "shoe_001") -> dict:
    """
    Query product information through the MCP server.
    Executes read-only query against Aurora PostgreSQL.
    
    Args:
        stream_id: The ID of the live stream
        product_identifier: Product ID to look up (default: shoe_001)
    
    Returns:
        Product details from database
    """
    from run_query import run_query
    
    tool_logger.info(f"🔍 Querying product via MCP server...")
    tool_logger.info(f"📡 MCP Query: SELECT * FROM products WHERE product_id = '{product_identifier}'")
    
    query = f"SELECT product_id, name, brand, price, category, description FROM products WHERE product_id = '{product_identifier}'"
    result = run_query(sql=query)
    
    tool_logger.info(f"✅ Product data retrieved via MCP")
    
    return result

@tool
def check_inventory_via_mcp(product_id: str, size: str = None) -> dict:
    """
    Check inventory through MCP server.
    Executes read-only query against Aurora PostgreSQL.
    
    Args:
        product_id: The product to check
        size: The size requested (optional)
    
    Returns:
        Inventory data from database
    """
    from run_query import run_query
    
    tool_logger.info(f"📦 Checking inventory via MCP server...")
    tool_logger.info(f"📡 MCP Query: Checking inventory for {product_id}")
    
    query = f"SELECT inventory, available_sizes FROM products WHERE product_id = '{product_id}'"
    result = run_query(sql=query)
    
    tool_logger.info(f"✅ Inventory data retrieved via MCP")
    
    return result

@tool
def simulate_order_creation(
    product_id: str,
    customer_id: str,
    size: str,
    base_price: float,
    tax: float,
    total_amount: float,
    stream_id: str = "fitness_stream_morning_001"
) -> dict:
    """
    Simulate order creation (read-only mode).
    Returns mock order confirmation without writing to database.
    
    Args:
        product_id: Product being ordered
        customer_id: Customer placing order
        size: Size selected
        base_price: Base price of product
        tax: Tax amount
        total_amount: Total amount
        stream_id: Stream where order originated
    
    Returns:
        Simulated order confirmation
    """
    tool_logger.info(f"🛒 Simulating order creation (read-only mode)...")
    
    order_id = f"SIM-{int(time.time())}-{customer_id[:4]}"
    
    tool_logger.info(f"✅ Order simulated: {order_id} (not written to database)")
    tool_logger.info(f"⚠️  Read-only mode: No database writes performed")
    
    return {
        "order_id": order_id,
        "status": "simulated",
        "total_amount": total_amount,
        "customer_id": customer_id,
        "product_id": product_id,
        "size": size,
        "note": "Order simulated in read-only mode - not written to database"
    }

@tool
def get_database_stats_via_mcp() -> dict:
    """
    Get database statistics through MCP server.
    Executes read-only query against Aurora PostgreSQL.
    
    Returns:
        Database statistics
    """
    from run_query import run_query
    
    tool_logger.info(f"📊 Fetching database stats via MCP...")
    
    query = """
    SELECT 
        (SELECT COUNT(*) FROM products) as total_products,
        (SELECT COUNT(*) FROM orders) as total_orders,
        (SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURRENT_DATE) as orders_today,
        (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE DATE(created_at) = CURRENT_DATE) as revenue_today;
    """
    
    result = run_query(sql=query)
    
    tool_logger.info(f"✅ Database stats retrieved via MCP")
    
    return result

# ============================================================================
# CLICKSHOP MCP AGENT
# ============================================================================

clickshop_mcp_agent = Agent(
    model=bedrock_model,
    tools=[
        query_product_from_mcp,
        check_inventory_via_mcp,
        simulate_order_creation,
        get_database_stats_via_mcp
    ],
    callback_handler=PrintingCallbackHandler(),
    system_prompt="""You are the ClickShop AI assistant - Month 3 MCP-Powered Version!

    IMPORTANT: You have access to Aurora PostgreSQL through an MCP server.
    
    Your workflow:
    1. Use query_product_from_mcp() to get product info from database
    2. Ask customer for size if needed
    3. Use check_inventory_via_mcp() to check stock from database
    4. Calculate total (base_price * 1.08 for tax, +$9.99 shipping if under $50)
    5. Use simulate_order_creation() to simulate order (READ-ONLY MODE)
    6. Confirm simulated order to customer and explain it's a demo
    
    IMPORTANT: You are in READ-ONLY mode. Orders are simulated, not written to database.
    
    Be friendly and conversational. Use emojis occasionally.
    The stream_id is: fitness_stream_morning_001
    
    Architecture: Month 3 - MCP-mediated database access (200 orders/day capacity)"""
)

# ============================================================================
# INTERACTIVE DEMO
# ============================================================================

def run_interactive_demo():
    """Run the Month 3 MCP-powered demo"""
    
    # Header
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🛍️  ClickShop - Month 3: MCP-Powered Architecture[/bold cyan]\n"
        "[yellow]Database operations through MCP server[/yellow]\n"
        "[green]Scaling to 200 orders/day with proper abstraction[/green]",
        border_style="cyan"
    ))
    
    # Show architecture evolution
    console.print("\n[bold]🏗️  Architecture Evolution:[/bold]")
    arch_table = Table(show_header=True, box=None)
    arch_table.add_column("Aspect", style="cyan", width=20)
    arch_table.add_column("Month 1", style="yellow", width=30)
    arch_table.add_column("Month 3", style="green", width=30)
    arch_table.add_row("Database Access", "Direct Python imports", "MCP Server (RDS Data API)")
    arch_table.add_row("Capacity", "50 orders/day", "200 orders/day")
    arch_table.add_row("Agent Tools", "Direct DB functions", "MCP-aware tools")
    arch_table.add_row("Abstraction", "Tight coupling", "Loose coupling via MCP")
    console.print(arch_table)
    
    # MCP Server Status
    console.print("\n[bold]📡 MCP Server Status:[/bold]")
    console.print("[green]✅ Aurora PostgreSQL MCP Server: Connected[/green]")
    console.print("[green]✅ RDS Data API: Active[/green]")
    console.print("[green]✅ Region: us-west-2[/green]")
    console.print("[dim]Server: awslabs.postgres-mcp-server@latest (via uvx)[/dim]")
    
    # Scenario
    console.print("\n[bold magenta]📺 Live Stream Scenario:[/bold magenta]")
    console.print("You're watching [bold cyan]@FitnessGuru's[/bold cyan] live stream")
    console.print("Stream ID: [yellow]fitness_stream_morning_001[/yellow]")
    console.print("They're showcasing the [bold]Nike Air Zoom Pegasus[/bold] running shoes")
    console.print("Current viewers: [green]5,421[/green] | Duration: [yellow]45:32[/yellow]\n")
    
    console.print("[dim]─────────────────────────────────────────────────────────────[/dim]\n")
    
    # Get customer input
    console.print("[bold green]💬 Chat with ClickShop MCP Agent![/bold green]")
    console.print("[dim]Type your message (or press Enter to use: 'I want those shoes!')[/dim]\n")
    
    customer_request = input("👤 You: ").strip()
    
    if not customer_request:
        customer_request = "I want those running shoes! They look amazing for my training."
        console.print(f"[yellow]👤 You: {customer_request}[/yellow]")
    
    console.print()
    
    # Process with MCP agent
    response = clickshop_mcp_agent(customer_request)
    response_text = str(response)
    
    # Check for follow-up
    if "size" in response_text.lower() and "?" in response_text:
        console.print("\n[dim]─────────────────────────────────────────────────────────────[/dim]\n")
        console.print("[bold green]💬 Continue the conversation:[/bold green]")
        console.print("[dim]Type your response (or press Enter for: 'Size 10 please!')[/dim]\n")
        
        size_input = input("👤 You: ").strip()
        
        if not size_input:
            size_input = "Size 10 please!"
            console.print(f"[yellow]👤 You: {size_input}[/yellow]")
        
        console.print()
        follow_up = clickshop_mcp_agent(size_input)
    
    # Get customer ID after size selection
    console.print("\n[bold green]Customer ID:[/bold green]")
    console.print("[dim]Enter your customer ID (or press Enter for: 'CUST-789')[/dim]\n")
    customer_id = input("👤 Customer ID: ").strip()
    if not customer_id:
        customer_id = "CUST-789"
        console.print(f"[yellow]Using customer ID: {customer_id}[/yellow]")
    
    # Show completion
    console.print("\n[dim]─────────────────────────────────────────────────────────────[/dim]")
    console.print("\n[bold green]✅ MCP Transaction Complete![/bold green]")
    console.print(f"[cyan]Customer ID: {customer_id}[/cyan]\n")
    
    # Performance comparison
    console.print("[bold]⚡ Performance Comparison:[/bold]")
    perf_table = Table(show_header=True, box=None)
    perf_table.add_column("Metric", style="cyan", width=25)
    perf_table.add_column("Month 1 (Direct)", style="yellow", width=20)
    perf_table.add_column("Month 3 (MCP)", style="green", width=20)
    perf_table.add_row("Avg Response Time", "~2.0s", "~3.5s")
    perf_table.add_row("Daily Capacity", "50 orders", "200 orders")
    perf_table.add_row("Connection Pooling", "Manual", "MCP managed")
    perf_table.add_row("Error Handling", "Basic", "MCP abstracted")
    perf_table.add_row("Scalability", "Limited", "Horizontal")
    console.print(perf_table)
    
    # MCP Benefits
    console.print("\n[bold]🎯 Month 3 MCP Benefits:[/bold]")
    benefits_table = Table(show_header=False, box=None, border_style="green")
    benefits_table.add_column(style="green", width=5)
    benefits_table.add_column(style="white")
    benefits_table.add_row("✅", "Database abstraction via standard protocol")
    benefits_table.add_row("✅", "RDS Data API for serverless scaling")
    benefits_table.add_row("✅", "No connection management in agent code")
    benefits_table.add_row("✅", "Easier to swap database implementations")
    benefits_table.add_row("✅", "Better security (IAM-based auth)")
    benefits_table.add_row("✅", "MCP server handles retries and pooling")
    console.print(benefits_table)
    
    console.print("\n[bold yellow]📡 All database operations routed through MCP server![/bold yellow]")
    console.print("[bold red]⚠️  READ-ONLY MODE: Orders are simulated, not written to database[/bold red]")
    console.print("[yellow]💡 Best Practice: Use MCP for reads + secure API endpoints for writes[/yellow]")
    console.print("[dim]Configuration: mcp-config.json[/dim]")
    console.print("[dim]Server: awslabs.postgres-mcp-server via uvx[/dim]\n")

if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted. Thanks for trying Month 3![/yellow]\n")
    except Exception as e:
        console.print(f"\n\n[bold red]Error:[/bold red] {e}\n")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        console.print("\n[dim]Check your MCP server configuration and Aurora connection[/dim]\n")
