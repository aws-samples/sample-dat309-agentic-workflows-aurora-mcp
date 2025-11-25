# ClickShop: Agentic Architecture Evolution Demo

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Aurora PostgreSQL](https://img.shields.io/badge/Amazon-Aurora-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)](https://aws.amazon.com/rds/aurora/)
[![Claude](https://img.shields.io/badge/Claude-Sonnet_4.5-8E75B2?style=for-the-badge&logo=anthropic&logoColor=white)](https://www.anthropic.com/claude)
[![MCP](https://img.shields.io/badge/MCP-Protocol-00A67E?style=for-the-badge)](https://modelcontextprotocol.io)

![License](https://img.shields.io/badge/License-MIT_0-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Educational-blue?style=for-the-badge)

**A production-oriented demonstration of scaling agentic systems from MVP to 50K orders/day**

[Overview](#overview) • [Architecture](#architecture-evolution) • [Quick Start](#quick-start) • [Demos](#running-the-demos) • [Resources](#technical-resources)

</div>

---

## Overview

**ClickShop** demonstrates the architectural evolution of agentic systems through three production-grade implementations. Built for AWS re:Invent 2025 (DAT309 Chalk Talk), this project showcases scaling patterns from a weekend MVP to enterprise-scale multi-agent orchestration with semantic search capabilities.

> **⚠️ Educational Use Only**: This demonstration is designed for learning purposes and illustrates production patterns without production-level error handling, monitoring, or security hardening.

### The ClickShop Story

A live-streaming shopping platform that evolved from 50 orders/day to 50,000 orders/day through three architectural iterations—demonstrating how thoughtful design enables exponential scaling without complete rewrites.

---

## Architecture Evolution

### Performance & Scale Comparison

| Metric              | Phase 1: Single Agent | Phase 2: Agent + MCP | Phase 3: Multi-Agent |
| ------------------- | --------------------- | -------------------- | -------------------- |
| **Daily Capacity**  | 50 orders             | 5,000 orders         | 50,000 orders        |
| **Response Time**   | ~2.0s                 | ~3.5s                | ~200ms               |
| **Architecture**    | Monolithic            | MCP-mediated         | Supervisor pattern   |
| **Database Access** | Direct (`psycopg3`)   | RDS Data API (MCP)   | Direct (`psycopg3`) + pgvector |
| **Search Type**     | Exact match           | Exact match          | Semantic (vector)    |
| **Coupling**        | Tight                 | Loose (MCP)          | Loose + Specialized  |

### Technical Architecture Details

<details>
<summary><strong>Phase 1: Single Agent Architecture</strong></summary>

**Capacity:** 50 orders/day | **Response Time:** ~2.0s

**Architecture:**

- **1 Agent:** Monolithic agent handles all responsibilities
- **4 Custom Tools:**
  - `identify_product_from_stream()` - Product discovery
  - `check_product_inventory()` - Real-time inventory verification
  - `calculate_order_total()` - Price calculation with tax/shipping
  - `process_customer_order()` - Order persistence and workflow
- **Database:** Direct Aurora PostgreSQL access via `psycopg3`
- **Pattern:** Tight coupling with inline database operations

**Key Characteristics:**

- ReAct pattern with Chain of Thought reasoning
- Sequential tool execution
- Manual connection pooling
- Ideal for MVPs and prototypes

</details>

<details>
<summary><strong>Phase 2: MCP-Powered Architecture</strong></summary>

**Capacity:** 5,000 orders/day | **Response Time:** ~3.5s

**Architecture:**

- **1 Agent:** Single agent with MCP integration
- **MCP Tools:** Auto-discovered from `awslabs.postgres-mcp-server`
  - `query` - SQL queries via RDS Data API
- **1 Custom Tool:**
  - `create_order()` - Order processing logic
- **Database:** Aurora PostgreSQL accessed via MCP (stdio transport)
- **Pattern:** Loose coupling through Model Context Protocol

**Key Improvements:**

- Database abstraction layer via standardized MCP protocol
- RDS Data API for serverless scaling
- IAM-based authentication
- Horizontal scaling capability
- Connection pooling handled by MCP server

**Implementation:**

```python
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx",
        args=[
            "awslabs.postgres-mcp-server@latest",
            "--resource_arn", "arn:aws:rds:region:account:cluster:cluster-id",
            "--secret_arn", "arn:aws:secretsmanager:region:account:secret:secret-name",
            "--database", "postgres",
            "--region", "us-west-2",
            "--readonly", "True"
        ]
    )
))
```

</details>

<details>
<summary><strong>Phase 3: Multi-Agent Supervisor Architecture</strong></summary>

**Capacity:** 50,000 orders/day | **Response Time:** ~200ms

**Architecture:**

- **4 Specialized Agents:**
  1. **Supervisor Agent** 🎯 - Workflow orchestration (no tools)
  2. **Search Agent** 🔍 - Semantic product discovery
     - Tool: `semantic_product_search()` (pgvector-powered)
  3. **Product Agent** 📋 - Product information and inventory
     - Tools: `get_product_details()`, `check_inventory_status()`
  4. **Order Agent** 🛒 - Order processing and confirmation
     - Tool: `simulate_order_placement()`
- **Database:** Aurora PostgreSQL + pgvector extension
- **Search:** Vector embeddings with HNSW index (cosine similarity)
- **Pattern:** Supervisor orchestration with specialized agents

**Key Improvements:**

- Parallel agent execution for sub-200ms response times
- Semantic search using vector embeddings
- Single Responsibility Principle per agent
- Natural language product discovery
- Horizontal and vertical scaling capabilities

**Semantic Search Implementation:**

```python
# Vector embedding generation and similarity search
CREATE INDEX ON products USING hnsw (embedding vector_cosine_ops);

# Natural language search: "comfortable running shoes"
# Matches semantically similar products, not just keywords
```

</details>

---

## Quick Start

### Prerequisites

**Required:**

- Python 3.11+
- AWS Account with Amazon Bedrock access
- Claude Sonnet 4.5 model access in Bedrock
- AWS CLI configured with credentials

**Recommended:**

- Familiarity with agentic frameworks (Strands, LangChain)
- Understanding of Model Context Protocol (MCP)
- Basic PostgreSQL and vector search knowledge

### Installation

```bash
# Clone repository
git clone <REPOSITORY_URL>
cd sample-dat309-agentic-workflows-aurora-mcp/clickshop-demo

# Run automated setup
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials and region

# Verify installation
python -m demos.run_demo
```

### Environment Configuration

```bash
# .env file structure
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
BEDROCK_MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
```

---

## Running the Demos

### Interactive Demo Launcher

```bash
python -m demos.run_demo
```

Select from the interactive menu to run any architecture demonstration.

### Individual Demo Execution

#### Phase 1: Single Agent (Monolithic)

```bash
python -m demos.phase_1_single_agent
```

**Demonstrates:**

- Basic agentic loop with ReAct pattern
- Chain of Thought (CoT) reasoning
- Sequential tool execution
- Direct database access patterns
- Manual connection management

#### Phase 2: Agent + MCP (Scaling)

```bash
python -m demos.phase_2_agent_mcp
```

**Demonstrates:**

- MCP server integration for database abstraction
- RDS Data API for serverless compute
- IAM-based authentication
- Tool auto-discovery from MCP servers
- Read-only database operations via MCP

#### Phase 3: Multi-Agent System (Production)

```bash
python -m demos.phase_3_multi_agent
```

**Demonstrates:**

- Supervisor pattern for agent orchestration
- Specialized agents with single responsibilities
- Semantic search with pgvector (0.8.0+)
- Parallel agent execution
- HNSW vector indexing for similarity search

---

## Project Structure

```
clickshop-demo/
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
│
├── demos/                         # Demo implementations
│   ├── run_demo.py               # Main entry point with interactive menu
│   ├── phase_1_single_agent.py   # Monolithic agent (50 orders/day)
│   ├── phase_2_agent_mcp.py      # MCP integration (5K orders/day)
│   └── phase_3_multi_agent.py    # Multi-agent (50K orders/day)
│
├── lib/                           # Core library modules
│   └── aurora_db.py              # Database operations and utilities
│
├── scripts/                       # Automation scripts
│   └── setup.sh                  # Environment setup
│
└── data/                          # Static data
    └── products.json             # Product catalog
```

---

## Technical Stack

| Component           | Technology                  | Purpose                                              |
| ------------------- | --------------------------- | ---------------------------------------------------- |
| **Agent Framework** | Strands                     | Agent orchestration, tool management, execution flow |
| **LLM Runtime**     | Amazon Bedrock              | Claude Sonnet 4.5 model hosting and inference        |
| **Database**        | Amazon Aurora PostgreSQL    | Transactional data storage with serverless v2        |
| **Vector Search**   | pgvector 0.8.0+             | Semantic search with HNSW indexing                   |
| **Protocol**        | Model Context Protocol      | Standardized tool/resource integration               |
| **MCP Server**      | awslabs.postgres-mcp-server | PostgreSQL access via RDS Data API                   |
| **SDK**             | boto3                       | AWS service integration                              |
| **Language**        | Python 3.11+                | Implementation language                              |

---

## Troubleshooting

### AWS Authentication Issues

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Verify Bedrock access
aws bedrock list-foundation-models --region us-west-2

# Test Bedrock model invocation
aws bedrock-runtime invoke-model \
    --model-id global.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
    --region us-west-2 \
    output.json
```

### Python Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### MCP Server Connection Issues

```bash
# Verify MCP server installation
uvx awslabs.postgres-mcp-server@latest --version

# Test MCP server connectivity
uvx awslabs.postgres-mcp-server@latest \
    --resource_arn "arn:aws:rds:region:account:cluster:cluster-id" \
    --secret_arn "arn:aws:secretsmanager:region:account:secret:secret-name" \
    --database "postgres" \
    --region "us-west-2" \
    --readonly "True"
```

---

## Technical Resources

### Documentation & Specifications

| Resource                                                                           | Description                                     |
| ---------------------------------------------------------------------------------- | ----------------------------------------------- |
| [Strands Framework](https://docs.strands.ai)                                       | Agent framework documentation and API reference |
| [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/)                             | AWS managed LLM service documentation           |
| [Model Context Protocol](https://modelcontextprotocol.io)                          | MCP specification and implementation guides     |
| [pgvector Extension](https://github.com/pgvector/pgvector)                         | PostgreSQL vector similarity search             |
| [Aurora PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/) | Serverless database documentation               |

### AWS Blogs & Technical Articles

**[Supercharging Vector Search with pgvector 0.8.0 on Aurora PostgreSQL](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/)**  
Deep dive into pgvector 0.8.0 improvements including HNSW indexing, scalar quantization, and performance optimizations for semantic search workloads.

**[Supercharging AWS Database Development with MCP Servers](https://aws.amazon.com/blogs/database/supercharging-aws-database-development-with-aws-mcp-servers/)**  
Guide to using Model Context Protocol servers for building AI agent applications with standardized database access patterns.

---

## Key Learnings & Best Practices

### Architectural Principles

1. **Start Monolithic, Evolve Deliberately**  
   Begin with a single agent to validate product-market fit. Introduce complexity only when metrics demonstrate the need.

2. **Abstract Early, Scale Later**  
   Introduce MCP for database abstraction before scaling bottlenecks emerge. Protocol-driven design enables horizontal scaling.

3. **Specialize Agents by Responsibility**  
   Multi-agent systems should follow Single Responsibility Principle. Each agent should have one clear purpose with dedicated tools.

4. **Use Supervisor Pattern for Orchestration**  
   Complex workflows require a supervisor agent that delegates to specialists rather than monolithic agents handling everything.

### Performance Optimization

- **Semantic Search**: pgvector with HNSW indexing dramatically improves search relevance and reduces latency
- **Parallel Execution**: Supervisor pattern enables concurrent agent operations for sub-second response times
- **Connection Pooling**: MCP servers handle connection lifecycle, eliminating manual pool management
- **IAM Authentication**: Credential management via AWS IAM reduces operational overhead

### Security Considerations

- Use IAM roles and policies for database access (no hardcoded credentials)
- Implement least-privilege access patterns for each agent/tool
- Enable audit logging for all agent actions
- Use AWS Secrets Manager for credential rotation

---

## Dependencies

```txt
# Core Framework
python>=3.11
strands-framework>=1.0.0
boto3>=1.34.0

# Database
psycopg3>=3.1.0
psycopg3-binary>=3.1.0

# Vector Search (Phase 3)
sentence-transformers>=2.2.0
pgvector>=0.8.0

# MCP Protocol (Phase 2, 3)
mcp>=0.1.0

# Utilities
python-dotenv>=1.0.0
rich>=13.7.0
```

---

<div align="center">

**AWS re:Invent 2025 | DAT309 Chalk Talk**

**Built with production-grade patterns for educational purposes**

[![Powered by AWS](https://img.shields.io/badge/Powered_by-AWS-FF9900?style=flat&logo=amazon-aws)](https://aws.amazon.com)
[![Architecture](https://img.shields.io/badge/Multi--Agent-Architecture-green?style=flat)](https://github.com)

---

Copyright © 2025 Shayon Sanyal, Amazon Web Services

Licensed under MIT-0 (MIT No Attribution)

</div>
