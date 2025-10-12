# ClickShop Agent Evolution Demo

This demo shows the evolution from single agent to multi-agent architecture using the ClickShop use case - a live shopping platform built by two friends using "vibe coding."

> **⚠️ Important Notice:** The examples in this repository are for demonstration and educational purposes only. They demonstrate concepts and techniques but are not intended for direct use in production. Always apply proper security and testing procedures before using in production environments.

## 📖 Story Arc

**The Journey:**
Two friends created ClickShop in a weekend using Claude and "vibe coding." Six months later, they're processing 50K orders/day - still just two friends, still vibe coding. This is their architectural journey.

### Month 1: Single Agent System
- **Scale**: 50 orders/day
- **Architecture**: One agent handles everything
- **Response Time**: ~2 seconds
- **Status**: "Just make it work"

### Month 3: Agent + MCP Tools
- **Scale**: 5,000 orders/day
- **Architecture**: Single agent with specialized MCP tools
- **Response Time**: ~1 second
- **Status**: "Starting to scale"

### Month 6: Multi-Agent Supervisor Pattern
- **Scale**: 50,000 orders/day
- **Architecture**: Supervisor orchestrating specialized agents
- **Response Time**: ~200ms
- **Status**: "Ready for anything"

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- AWS Account with Bedrock access
- Access to Claude Sonnet 4 model in Amazon Bedrock
- AWS CLI configured (optional but recommended)

### Installation

```bash
# 1. Navigate to the demo directory
cd clickshop-demo

# 2. Run the setup script
./scripts/setup.sh

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 5. Test Aurora connection
python scripts/test_aurora_connection.py

# 6. Initialize database
python scripts/init_aurora_schema.py

# 7. Run demos
python run_demo.py
```

---

## 🎬 Running the Demos

### Interactive Menu (Recommended)

```bash
python run_demo.py
```

This launches an interactive menu where you can select which demo to run.

### Month 1: Single Agent

```bash
python -m demos.month_1_single_agent
```

**What it demonstrates:**
- Basic agentic loop with ReAct pattern
- Chain of Thought (CoT) reasoning
- Asking clarifying questions
- Sequential tool execution
- Aurora PostgreSQL integration

### Month 3: Agent + MCP

```bash
python -m demos.month_3_agent_mcp
```

**What it demonstrates:**
- MCP server integration for database access
- Tool-based specialization
- RDS Data API for serverless scaling
- Read-only mode with simulated writes

### Month 6: Multi-Agent System

```bash
python -m demos.month_6_multi_agent
```

**What it demonstrates:**
- Supervisor pattern for orchestration
- Specialized agents (Search, Product, Order)
- Semantic search with pgvector
- Agent-based task delegation
- Sub-200ms response time

---

## 📁 Project Structure

```
clickshop-demo/
├── run_demo.py              # Main entry point
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── mcp-config.json         # MCP server configuration
│
├── demos/                  # Demo implementations
│   ├── month_1_single_agent.py
│   ├── month_3_agent_mcp.py
│   └── month_6_multi_agent.py
│
├── lib/                    # Core library modules
│   └── aurora_db.py        # Database operations
│
├── scripts/                # Utility scripts
│   ├── setup.sh
│   ├── verify_installation.py
│   ├── test_aurora_connection.py
│   ├── init_aurora_schema.py
│   └── generate_embeddings.py
│
└── data/                   # Static data files
    └── products.json
```

---

## 🔧 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Strands Framework** | Agent orchestration and management |
| **Amazon Bedrock** | Claude Sonnet 4 LLM access |
| **Amazon Aurora** | Serverless PostgreSQL for data persistence |
| **MCP (Model Context Protocol)** | Standardized tool integration |
| **Python** | Primary development language |
| **AWS SDK (boto3)** | AWS service integration |

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### AWS Credentials Issues

```bash
# Verify your credentials
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-west-2
```

### Setup Script Permission Error

```bash
chmod +x scripts/setup.sh
```

---

## 🎓 Demo Tips

### For Presentations

1. **Start with the story** - Two friends, weekend project, explosive growth
2. **Show Month 1 first** - Establish the baseline (50 orders/day)
3. **Month 3: MCP integration** - Show tool-based specialization (200 orders/day)
4. **Month 6: Multi-agent** - Demonstrate supervisor pattern (50K orders/day)
5. **Highlight the evolution** - Monolithic → Tool-based → Agent-based

### Live Demo Tips

- Use the interactive menu (`python run_demo.py`)
- Show the architecture evolution table at the end
- Demonstrate semantic search in Month 6
- Highlight the orchestration workflow diagram
- Use consistent customer ID (CUST-123) across demos

---

## 📚 Additional Resources

### Strands Framework
- Documentation: https://docs.strands.ai
- GitHub: https://github.com/strands-ai/strands-framework

### Amazon Bedrock
- Documentation: https://docs.aws.amazon.com/bedrock/
- Model Access: https://console.aws.amazon.com/bedrock/

### Model Context Protocol
- Specification: https://modelcontextprotocol.io
- GitHub: https://github.com/modelcontextprotocol

---

## 🎯 Key Takeaways

**Architecture Evolution:**
- **Month 1**: Monolithic single agent (50 orders/day)
- **Month 3**: Tool-based specialization with MCP (200 orders/day)
- **Month 6**: Agent-based with supervisor pattern (50K orders/day)

**Best Practices:**
- Use MCP for standardized data access
- Implement supervisor pattern for complex workflows
- Specialize agents for specific tasks
- Leverage semantic search for better UX

**Remember:** The goal isn't just to scale - it's to scale while maintaining development velocity and developer happiness. That's the "vibe coding" philosophy! 🚀

---

© Shayon Sanyal, Principal Solutions Architect, AWS
