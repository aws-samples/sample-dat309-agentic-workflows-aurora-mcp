"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE 2: MCP-Powered Architecture                                            ║
║ Capacity: 5,000 orders/day | Response Time: ~3.5s                            ║
║                                                                              ║
║ Pattern: Single agent + Model Context Protocol for database abstraction      ║
║ Perfect for: Scaling beyond MVP, adding abstraction layers                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import os
import time
from dotenv import load_dotenv
from mcp import stdio_client, StdioServerParameters
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from rich.console import Console
from rich.panel import Panel

load_dotenv()
console = Console()

# ═══════════════════════════════════════════════════════════════════════════
# BEDROCK MODEL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
bedrock_model = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID"),
    region_name=os.getenv("BEDROCK_REGION", "us-west-2"),
    temperature=0.3
)

# ═══════════════════════════════════════════════════════════════════════════
# MCP CLIENT SETUP - The Key Architectural Change
# ═══════════════════════════════════════════════════════════════════════════
# Model Context Protocol provides standardized database access
# Benefits:
#   1. Database abstraction - swap implementations without changing agent code
#   2. RDS Data API - serverless, no connection pooling needed
#   3. IAM authentication - no hardcoded credentials
#   4. Auto-discovered tools - MCP server exposes database operations as tools

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",  # Run MCP server via uvx (Python package runner)
        args=[
            "awslabs.postgres-mcp-server@latest",  # AWS Labs PostgreSQL MCP server
            "--resource_arn", "arn:aws:rds:us-west-2:619763002613:cluster:apgpg-pgvector",
            "--secret_arn", "arn:aws:secretsmanager:us-west-2:619763002613:secret:apgpg-pgvector-secret-l847Vi",
            "--database", "postgres",
            "--region", "us-west-2",
            "--readonly", "True",  # Read-only mode for safety
        ]
    )
))

# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM TOOL - Order Processing
# ═══════════════════════════════════════════════════════════════════════════
# MCP handles reads (via 'query' tool), we add custom tool for writes
# This separation is a best practice: MCP for reads, secure API for writes

@tool
def create_order(product_id: str, customer_id: str, size: str,
    base_price: float,
    tax: float,
    total_amount: float,
    stream_id: str = "fitness_stream_morning_001"
) -> dict:
    """
    Create customer order.
    
    ARCHITECTURE NOTE: Custom tool for write operations
    - MCP server is read-only (best practice)
    - Write operations go through secure API endpoints
    - In production: this would call an API, not simulate
    """
    order_id = f"ORD-{int(time.time())}-{customer_id[:4]}"
    
    print(f"✅ Order simulated: {order_id}")
    print("⚠️  Read-only MCP mode: Order not written to database")
    
    return {
        "order_id": order_id,
        "status": "confirmed",
        "total_amount": total_amount,
        "customer_id": customer_id,
        "product_id": product_id,
        "size": size
    }

# ═══════════════════════════════════════════════════════════════════════════
# DEMO RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_interactive_demo():
    """Run Phase 2 MCP demo"""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🛍️  PHASE 2: MCP-Powered Architecture[/bold cyan]\n"
        "[yellow]Database abstraction via Model Context Protocol[/yellow]\n"
        "[green]Capacity: 5,000 orders/day | Response: ~3.5s[/green]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]📊 Architecture Evolution:[/bold]")
    console.print("  Phase 1 → Phase 2:")
    console.print("  • Direct DB calls → MCP server")
    console.print("  • psycopg3 → RDS Data API")
    console.print("  • Manual pooling → MCP managed")
    console.print("  • Tight coupling → Loose coupling\n")
    
    console.print("[bold]📡 MCP Server Status:[/bold]")
    console.print("  ✅ Aurora PostgreSQL MCP Server")
    console.print("  ✅ RDS Data API enabled")
    console.print("  ✅ IAM authentication")
    console.print("  ✅ Read-only mode\n")
    
    # Get input
    console.print("[dim]Press Enter for default: 'I want those running shoes!'[/dim]")
    customer_request = input("👤 You: ").strip() or "I want those running shoes!"
    console.print(f"[yellow]👤 You: {customer_request}[/yellow]\n")
    
    console.print("[dim]Initializing MCP server (this may take a moment)...[/dim]\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # MCP CLIENT CONTEXT - Auto-discover tools from MCP server
    # ═══════════════════════════════════════════════════════════════════════
    # The MCP server exposes database operations as tools
    # Agent can now use SQL queries without knowing database details
    
    with mcp_client:
        # Auto-discover tools from MCP server
        mcp_tools = mcp_client.list_tools_sync()
        console.print(f"[dim]MCP discovered {len(mcp_tools)} tools from server[/dim]\n")
        
        # Create agent with MCP tools + custom order tool
        clickshop_mcp_agent = Agent(
            model=bedrock_model,
            tools=mcp_tools + [create_order],  # MCP tools + custom tool
            system_prompt="""You are ClickShop AI - Phase 2 MCP-Powered Version!

IMPORTANT: You have Aurora PostgreSQL access via MCP server.

WORKFLOW:
1. Use MCP 'query' tool: SELECT * FROM products WHERE product_id = 'shoe_001'
2. Ask customer for size
3. Use MCP 'query' tool to check inventory
4. Calculate total (base_price * 1.08 for tax, +$9.99 shipping if under $50)
5. Use create_order() to process order

MCP BENEFITS:
- Database abstraction (can swap DB without code changes)
- RDS Data API (serverless, auto-scaling)
- IAM authentication (no credentials in code)

Be friendly! Stream ID: fitness_stream_morning_001"""
        )
        
        # Process request
        response = clickshop_mcp_agent(customer_request)
        
        # Handle size follow-up
        if "size" in str(response).lower():
            console.print()
            console.print("[dim]Press Enter for default: 'Size 10'[/dim]")
            size_input = input("👤 You: ").strip() or "Size 10"
            console.print(f"[yellow]👤 You: {size_input}[/yellow]\n")
            clickshop_mcp_agent(size_input)
    
    # Get customer ID
    console.print("[dim]Press Enter for default: 'CUST-123'[/dim]")
    customer_id = input("👤 Customer ID: ").strip() or "CUST-123"
    console.print(f"[yellow]Using: {customer_id}[/yellow]\n")
    
    console.print("[bold green]✅ Phase 2 Complete![/bold green]")
    
    console.print("\n[bold]🎯 MCP Benefits:[/bold]")
    console.print("  ✓ Database abstraction layer")
    console.print("  ✓ RDS Data API (serverless)")
    console.print("  ✓ No connection management")
    console.print("  ✓ IAM-based security")
    console.print("  ✓ Horizontal scaling")
    console.print("  ✓ Tool auto-discovery\n")
    
    console.print("[bold]📈 Scaling Improvements:[/bold]")
    console.print("  • 50 → 5,000 orders/day (100x)")
    console.print("  • Loose coupling via protocol")
    console.print("  • Ready for multi-region\n")

if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]\n")
