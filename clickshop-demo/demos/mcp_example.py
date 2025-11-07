from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

# Create MCP client with stdio transport
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=["awslabs.postgres-mcp-server@latest", 
              "--resource_arn", "arn:aws:rds:..."]
    )
))

# Use MCP client in Agent
with mcp_client:
    tools = mcp_client.list_tools_sync()
    agent = Agent(model=bedrock_model, tools=tools)
    agent("Get product details for shoe_001")
