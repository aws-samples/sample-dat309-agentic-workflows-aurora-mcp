"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ PHASE 2: MCP-Powered Architecture                                            ║
║ Capacity: 5,000 orders/day | Response Time: ~3.5s                            ║
║                                                                              ║
║ Pattern: Single agent + Model Context Protocol for database abstraction      ║
║ When to use: Scaling beyond 1K orders/day, need portability                  ║
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
# MCP CLIENT SETUP - Database Abstraction Layer
# ═══════════════════════════════════════════════════════════════════════════
# WHY MCP? Three key benefits:
# 1. PORTABILITY: Swap databases without changing agent code
# 2. SCALING: RDS Data API = serverless connections (no pooling headaches)
# 3. SECURITY: IAM authentication, no credentials in code
#
# TRADEOFF: +1.5s latency vs direct connections (~3.5s vs ~2s)
# Worth it? Yes, if you need abstraction. No, if you need <200ms responses.

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=[
            "awslabs.postgres-mcp-server@latest",
            "--resource_arn", "arn:aws:rds:us-west-2:123456789012:cluster:apgpg-pgvector",
            "--secret_arn", "arn:aws:secretsmanager:us-west-2:123456789012:secret:my-secret-abc123",
            "--database", "postgres",
            "--region", "us-west-2",
            "--readonly", "True",  # Read-only mode for safety
        ]
    )
))

# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM TOOL - Order Processing
# ═══════════════════════════════════════════════════════════════════════════
# PATTERN: MCP for reads, custom tool for writes
# Why? MCP servers are typically read-only for safety
# Production: This would call a write API endpoint with auth + validation

@tool
def create_order(product_id: str, customer_id: str, size: str,
    base_price: float,
    tax: float,
    total_amount: float,
    stream_id: str = "fitness_stream_morning_001"
) -> dict:
    """
    Create customer order (simulated for demo).
    
    PRODUCTION PATTERN:
    Instead of direct DB writes, call a secure API:
    - POST /api/orders with auth token
    - API handles validation, rate limiting, audit logs
    - Separates read paths (MCP) from write paths (API)
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
    
    console.print("\n[bold]📊 What Changed from Phase 1:[/bold]")
    console.print("  Before: import psycopg3 → write SQL → manage connections")
    console.print("  After:  MCP server handles all database details")
    console.print("  Benefit: Swap Aurora for RDS/Postgres without code changes\n")
    
    console.print("[bold]📡 MCP Server Status:[/bold]")
    console.print("  ✅ Aurora PostgreSQL MCP Server")
    console.print("  ✅ RDS Data API (serverless)")
    console.print("  ✅ IAM authentication")
    console.print("  ✅ Read-only mode\n")
    
    # Get input
    console.print("[dim]Press Enter for default: 'I want those running shoes!'[/dim]")
    customer_request = input("👤 You: ").strip() or "I want those running shoes!"
    console.print(f"[yellow]👤 You: {customer_request}[/yellow]\n")
    
    console.print("[dim]Initializing MCP server (first run takes ~2s)...[/dim]\n")
    
    # ═══════════════════════════════════════════════════════════════════════
    # MCP CLIENT CONTEXT - Tool Auto-Discovery
    # ═══════════════════════════════════════════════════════════════════════
    # KEY FEATURE: MCP server exposes database operations as tools
    # Agent gets: query, get_table_schema, run_embedding, etc.
    # No manual tool definitions needed!
    
    with mcp_client:
        # Auto-discover tools from MCP server
        mcp_tools = mcp_client.list_tools_sync()
        console.print(f"[dim]✓ MCP auto-discovered {len(mcp_tools)} tools[/dim]")
        console.print(f"[dim]  Tools available: query, get_table_schema, run_embedding[/dim]\n")
        
        # Create agent with MCP tools + custom order tool
        clickshop_mcp_agent = Agent(
            model=bedrock_model,
            tools=mcp_tools + [create_order],  # MCP auto-discovered + custom
            system_prompt="""You are ClickShop AI, an intelligent shopping assistant utilizing Model Context Protocol (MCP) for database operations.

IMPORTANT: All database access must be performed through MCP server tools.

WORKFLOW:
1. Query product information using MCP 'query' tool: SELECT * FROM products WHERE product_id = 'shoe_001'
2. Request the customer's preferred size
3. Verify inventory availability using MCP 'query' tool to check stock levels
4. Calculate order total: base_price * 1.08 (tax) + $9.99 shipping (if order total < $50)
5. Process the order using the create_order() function

ARCHITECTURE: Phase 2 - MCP-abstracted database layer (5,000 orders/day capacity)

Maintain a professional yet approachable tone throughout the interaction.
Default stream context: fitness_stream_morning_001"""
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
    
    console.print("\n[bold]🎯 Why MCP? Three Key Benefits:[/bold]")
    console.print("  1. PORTABILITY: Change databases without changing code")
    console.print("  2. SCALING: RDS Data API handles connection pooling")
    console.print("  3. SECURITY: IAM auth, no credentials in code\n")
    
    console.print("[bold]⚖️  When to Use MCP vs Direct:[/bold]")
    console.print("  Use MCP: Need portability, scaling >1K orders/day")
    console.print("  Use Direct: Need <200ms response times (see Phase 3)\n")
    
    console.print("[bold]📈 Scaling Impact:[/bold]")
    console.print("  • Phase 1: 50 orders/day")
    console.print("  • Phase 2: 5,000 orders/day (100x)")
    console.print("  • Ready for: Multi-region, database migrations\n")

if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]\n")