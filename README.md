# ClickShop Agent Evolution Demo

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Aurora](https://img.shields.io/badge/Amazon-Aurora-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-Sonnet_4.5-8E75B2?style=for-the-badge&logo=anthropic&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Protocol-00A67E?style=for-the-badge&logo=protocol&logoColor=white)

![License](https://img.shields.io/badge/License-MIT--0-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Educational-blue?style=for-the-badge)
![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-green?style=for-the-badge)

**Frameworks & Tools**

![Strands](https://img.shields.io/badge/Strands-Framework-blueviolet?style=flat-square)
![boto3](https://img.shields.io/badge/boto3-AWS_SDK-orange?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17+-336791?style=flat-square&logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-Embeddings-4169E1?style=flat-square)

</div>

---

## 📖 Overview

This demo shows the evolution from single agent to multi-agent architecture using the **ClickShop** use case - a live shopping platform built by two friends using "vibe coding."

> **⚠️ Important Notice:** The examples in this repository are for demonstration and educational purposes only. They demonstrate concepts and techniques but are not intended for direct use in production environments. Always apply proper security, testing, and compliance procedures before using in production.

---

## 🎭 Story Arc

**The Journey:**
Two friends created ClickShop in a weekend using Claude and "vibe coding." Six months later, they're processing 50K orders/day - still just two friends, still vibe coding. This is their architectural journey.

### 📊 Evolution Timeline

<table>
<tr>
<th>Month 1: Single Agent</th>
<th>Month 3: Agent + MCP</th>
<th>Month 6: Multi-Agent</th>
</tr>
<tr>
<td>

**Scale:** 50 orders/day  
**Architecture:** Monolithic agent  
**Response Time:** ~2 seconds  
**Database:** Direct psycopg2  
**Status:** "Just make it work"

</td>
<td>

**Scale:** 5,000 orders/day  
**Architecture:** MCP tools  
**Response Time:** ~1 second  
**Database:** RDS Data API  
**Status:** "Starting to scale"

</td>
<td>

**Scale:** 50,000 orders/day  
**Architecture:** Supervisor pattern  
**Response Time:** ~200ms  
**Database:** Aurora + pgvector  
**Status:** "Ready for anything"

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

<table>
<tr>
<td>

**Required**

- Python 3.11 or higher
- AWS Account with Bedrock access
- Claude Sonnet 4 model access
- AWS CLI configured

</td>
<td>

**Recommended**

- Virtual environment (venv)
- AWS credentials with admin access
- Familiarity with agent frameworks
- Understanding of MCP protocol

</td>
</tr>
</table>

### Installation

```bash
# 1. Navigate to the demo directory
cd clickshop-demo

# 2. Run the setup script
./scripts/setup.sh

# 3. Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 5. Run demos
python run_demo.py
```

---

## 🎬 Running the Demos

### 🎯 Interactive Menu (Recommended)

```bash
python run_demo.py
```

This launches an interactive menu where you can select which demo to run.

### 📦 Month 1: Single Agent

```bash
python -m demos.month_1_single_agent
```

<details>
<summary><strong>What it demonstrates</strong></summary>

- ✅ Basic agentic loop with ReAct pattern
- ✅ Chain of Thought (CoT) reasoning
- ✅ Asking clarifying questions
- ✅ Sequential tool execution
- ✅ Aurora PostgreSQL integration
- ✅ Direct database access (psycopg2)
- ✅ Manual connection pooling

**Key Concepts:**

- Single agent handles all tasks
- Tight coupling to database
- Simple but not scalable
- Perfect for MVPs and prototypes

</details>

### 🔧 Month 3: Agent + MCP

```bash
python -m demos.month_3_agent_mcp
```

<details>
<summary><strong>What it demonstrates</strong></summary>

- ✅ MCP server integration for database access
- ✅ Tool-based specialization
- ✅ RDS Data API for serverless scaling
- ✅ IAM-based authentication
- ✅ Connection pooling abstraction
- ✅ Read-only mode with simulated writes

**Key Concepts:**

- Database abstraction via MCP
- Better separation of concerns
- Horizontal scaling capability
- Production-ready architecture

</details>

### 🎯 Month 6: Multi-Agent System

```bash
python -m demos.month_6_multi_agent
```

<details>
<summary><strong>What it demonstrates</strong></summary>

- ✅ Supervisor pattern for orchestration
- ✅ Specialized agents (Search, Product, Order)
- ✅ Semantic search with pgvector
- ✅ Agent-based task delegation
- ✅ Parallel execution
- ✅ Sub-200ms response time

**Key Concepts:**

- Supervisor orchestrates specialized agents
- Each agent has single responsibility
- Semantic search for better matching
- High-performance distributed system

</details>

---

## 📁 Project Structure

```
clickshop-demo/
├── run_demo.py                 # 🎯 Main entry point
├── requirements.txt            # 📦 Python dependencies
├── .env.example               # 🔐 Environment template
├── mcp-config.json            # 🔧 MCP server configuration
│
├── demos/                     # 🎬 Demo implementations
│   ├── month_1_single_agent.py    # Month 1: Single agent
│   ├── month_3_agent_mcp.py       # Month 3: MCP integration
│   └── month_6_multi_agent.py     # Month 6: Multi-agent system
│
├── lib/                       # 📚 Core library modules
│   └── aurora_db.py              # Database operations
│
├── scripts/                   # 🛠️ Utility scripts
│   └── setup.sh                  # Installation script
│
└── data/                      # 📊 Static data files
    └── products.json             # Product catalog
```

---

## 🔧 Technologies Used

<table>
<tr>
<th>Technology</th>
<th>Purpose</th>
<th>Version/Details</th>
</tr>
<tr>
<td><strong>Strands Framework</strong></td>
<td>Agent orchestration and management</td>
<td>Latest stable</td>
</tr>
<tr>
<td><strong>Amazon Bedrock</strong></td>
<td>Claude Sonnet 4 LLM access</td>
<td>claude-sonnet-4-5-20250929</td>
</tr>
<tr>
<td><strong>Amazon Aurora</strong></td>
<td>Serverless PostgreSQL for data persistence</td>
<td>PostgreSQL 17+ compatible</td>
</tr>
<tr>
<td><strong>MCP Protocol</strong></td>
<td>Standardized tool integration</td>
<td>awslabs.postgres-mcp-server</td>
</tr>
<tr>
<td><strong>pgvector</strong></td>
<td>Vector embeddings for semantic search</td>
<td>0.8.0+</td>
</tr>
<tr>
<td><strong>Python</strong></td>
<td>Primary development language</td>
<td>3.11+</td>
</tr>
<tr>
<td><strong>boto3</strong></td>
<td>AWS SDK for Python</td>
<td>Latest stable</td>
</tr>
</table>

---

## 🛠️ Troubleshooting

### 🔴 Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### 🔐 AWS Credentials Issues

```bash
# Verify your credentials
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-west-2

# Test Bedrock invocation
aws bedrock-runtime invoke-model \
    --model-id us.anthropic.claude-sonnet-4-20250514-v1:0 \
    --body '{"prompt":"Hello","max_tokens":10}' \
    --region us-west-2 \
    output.txt
```

### ⚙️ Setup Script Permission Error

```bash
chmod +x scripts/setup.sh
```

---

## 📚 Additional Resources

<table>
<tr>
<td width="33%">

### 🔗 Strands Framework

- [Documentation](https://docs.strands.ai)
- [GitHub](https://github.com/strands-ai/strands-framework)
- [Examples](https://github.com/strands-ai/examples)

</td>
<td width="33%">

### ☁️ Amazon Bedrock

- [Documentation](https://docs.aws.amazon.com/bedrock/)
- [Model Access](https://console.aws.amazon.com/bedrock/)
- [Pricing](https://aws.amazon.com/bedrock/pricing/)

</td>
<td width="33%">

### 🔌 Model Context Protocol

- [Specification](https://modelcontextprotocol.io)
- [GitHub](https://github.com/modelcontextprotocol)
- [Servers](https://github.com/awslabs/postgres-mcp-server)

</td>
</tr>
</table>

### 📝 AWS Blogs & Articles

<table>
<tr>
<td width="50%">

#### 🔍 Vector Search with pgvector

**[Supercharging Vector Search Performance with pgvector 0.8.0 on Amazon Aurora PostgreSQL](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)**

Learn about the latest pgvector improvements and how to optimize semantic search performance on Aurora PostgreSQL.

</td>
<td width="50%">

#### 🔧 MCP Servers for AWS

**[Supercharging AWS Database Development with AWS MCP Servers](https://aws.amazon.com/blogs/database/supercharging-aws-database-development-with-aws-mcp-servers/)**

Discover how to use Model Context Protocol servers to build better database-connected applications with AI agents.

</td>
</tr>
</table>

---

## 🎯 Key Takeaways

### 📈 Architecture Evolution

| Month | Architecture            | Daily Capacity | Response Time | Key Feature          |
| ----- | ----------------------- | -------------- | ------------- | -------------------- |
| **1** | Monolithic single agent | 50 orders      | ~2.0s         | Direct DB access     |
| **3** | Tool-based with MCP     | 5,000 orders   | ~1.0s         | Database abstraction |
| **6** | Multi-agent supervisor  | 50,000 orders  | ~0.2s         | Parallel execution   |

### ✨ Best Practices

<table>
<tr>
<td>

**🏗️ Architecture**

- Use MCP for standardized data access
- Implement supervisor pattern for complex workflows
- Specialize agents for specific tasks
- Design for horizontal scaling

</td>
<td>

**⚡ Performance**

- Leverage semantic search for better UX
- Use parallel execution where possible
- Implement proper connection pooling
- Cache frequently accessed data

</td>
<td>

**🔐 Security**

- Use IAM-based authentication
- Rotate credentials regularly
- Implement least privilege access
- Monitor and audit agent actions

</td>
</tr>
</table>

### 💡 The "Vibe Coding" Philosophy

> **Remember:** The goal isn't just to scale - it's to scale while maintaining development velocity and developer happiness. That's the "vibe coding" philosophy! 🚀

**Core Principles:**

- 🎯 Start simple, evolve as needed
- 🔄 Iterate based on real requirements
- 🤝 Keep the team small and focused
- 📊 Let metrics guide architecture decisions
- 🎨 Maintain code quality and readability

---

## 📋 Requirements

```txt
# Core Dependencies
python>=3.11
strands-framework>=1.0.0
boto3>=1.34.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0

# Visualization
rich>=13.7.0

# AWS Services
aws-cli>=2.15.0
```

---

## 👤 Author

**Shayon Sanyal**  
_Principal Solutions Architect, AWS_

---

## 🙏 Acknowledgments

- **Anthropic** - For Claude Sonnet 4 and the amazing capabilities
- **AWS** - For Bedrock, Aurora, and the broader ecosystem
- **Strands Team** - For the excellent agent framework
- **MCP Community** - For the standardization efforts

---

<div align="center">

**Built with ❤️ using vibe coding**

[![AWS](https://img.shields.io/badge/Powered_by-AWS-FF9900?style=flat&logo=amazon-aws)](https://aws.amazon.com)

</div>
