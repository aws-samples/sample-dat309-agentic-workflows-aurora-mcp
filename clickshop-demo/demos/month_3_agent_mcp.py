"""
ClickShop - Month 3: MCP-Powered Agent with Aurora PostgreSQL
Evolution from direct DB access to MCP architecture
5,000 orders/day, database operations via MCP server
"""
import os
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
from mcp import stdio_client, StdioServerParameters
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
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
    format="%(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Initialize Bedrock model
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"),
    region_name=os.getenv("BEDROCK_REGION", "us-west-2"),
    temperature=0.3,
)

# ============================================================================
# MCP CLIENT SETUP
# ============================================================================

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=[
            "awslabs.postgres-mcp-server@latest",
            "--resource_arn", "arn:aws:rds:us-west-2:619763002613:cluster:apgpg-pgvector",
            "--secret_arn", "arn:aws:secretsmanager:us-west-2:619763002613:secret:apgpg-pgvector-secret-l847Vi",
            "--database", "postgres",
            "--region", "us-west-2",
            "--readonly", "True",
        ]
    )
))

# ============================================================================
# CUSTOM TOOLS
# ============================================================================

@tool
def create_order(
    product_id: str,
    customer_id: str,
    size: str,
    base_price: float,
    tax: float,
    total_amount: float,
    stream_id: str = "fitness_stream_morning_001"
) -> dict:
    """
    Create order for customer.
    
    Args:
        product_id: Product being ordered
        customer_id: Customer placing order
        size: Size selected
        base_price: Base price of product
        tax: Tax amount
        total_amount: Total amount
        stream_id: Stream where order originated
    
    Returns:
        Order confirmation
    """
    order_id = f"ORD-{int(time.time())}-{customer_id[:4]}"
    
    return {
        "order_id": order_id,
        "status": "confirmed",
        "total_amount": total_amount,
        "customer_id": customer_id,
        "product_id": product_id,
        "size": size,
        "stream_id": stream_id
    }

# ============================================================================
# CLICKSHOP MCP AGENT (initialized in run_interactive_demo)
# ============================================================================

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
        "[green]Scaling to 5,000 orders/day with proper abstraction[/green]",
        border_style="cyan"
    ))
    
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
    
    # Create agent with MCP client
    with mcp_client:
        mcp_tools = mcp_client.list_tools_sync()
        
        clickshop_mcp_agent = Agent(
            model=bedrock_model,
            tools=mcp_tools + [create_order],
            callback_handler=PrintingCallbackHandler(),
            system_prompt="""You are the ClickShop AI assistant - Month 3 MCP-Powered Version!

    IMPORTANT: You have access to Aurora PostgreSQL through an MCP server.
    
    Your workflow:
    1. Use MCP 'query' tool to get product info: SELECT * FROM products WHERE product_id = 'shoe_001'
    2. Ask customer for size if needed
    3. Use MCP 'query' tool to check inventory: SELECT * FROM products WHERE product_id = 'shoe_001'
    4. Calculate total (base_price * 1.08 for tax, +$9.99 shipping if under $50)
    5. Use create_order() to create the order
    6. Confirm order to customer
    
    Be friendly and conversational. Use emojis occasionally.
    The stream_id is: fitness_stream_morning_001
    
    Architecture: Month 3 - MCP-mediated database access (5,000 orders/day capacity)"""
        )
        
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
    console.print("[dim]Enter your customer ID (or press Enter for: 'CUST-123')[/dim]\n")
    customer_id = input("👤 Customer ID: ").strip()
    if not customer_id:
        customer_id = "CUST-123"
        console.print(f"[yellow]Using customer ID: {customer_id}[/yellow]")
    
    # Show completion
    console.print("\n[dim]─────────────────────────────────────────────────────────────[/dim]")
    console.print("\n[bold green]✅ MCP Transaction Complete![/bold green]")
    console.print(f"[cyan]Customer ID: {customer_id}[/cyan]\n")
    
    # Architecture evolution
    console.print("[bold]🏗️  Architecture Evolution:[/bold]")
    arch_table = Table(show_header=True, box=None)
    arch_table.add_column("Aspect", style="cyan", width=20)
    arch_table.add_column("Month 1", style="yellow", width=30)
    arch_table.add_column("Month 3", style="green", width=30)
    arch_table.add_row("Database Access", "Direct Python imports", "MCP Server (RDS Data API)")
    arch_table.add_row("Capacity", "50 orders/day", "5,000 orders/day")
    arch_table.add_row("Agent Tools", "Direct DB functions", "MCP auto-discovered tools")
    arch_table.add_row("Abstraction", "Tight coupling", "Loose coupling via MCP")
    console.print(arch_table)
    
    # Performance comparison
    console.print("\n[bold]⚡ Performance Comparison:[/bold]")
    perf_table = Table(show_header=True, box=None)
    perf_table.add_column("Metric", style="cyan", width=25)
    perf_table.add_column("Month 1 (Direct)", style="yellow", width=20)
    perf_table.add_column("Month 3 (MCP)", style="green", width=20)
    perf_table.add_row("Avg Response Time", "~2.0s", "~3.5s")
    perf_table.add_row("Daily Capacity", "50 orders", "5,000 orders")
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
    console.print("[dim]Transport: stdio via uvx[/dim]")
    console.print("[dim]Server: awslabs.postgres-mcp-server@latest[/dim]\n")

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
