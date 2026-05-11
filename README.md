# AgentStride: Ask. Shop. Done.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![Aurora PostgreSQL](https://img.shields.io/badge/Amazon-Aurora-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)](https://aws.amazon.com/rds/aurora/)
[![Claude](https://img.shields.io/badge/Claude-Opus_4.7-8E75B2?style=for-the-badge&logo=anthropic&logoColor=white)](https://www.anthropic.com/claude)
[![MCP](https://img.shields.io/badge/MCP-Protocol-00A67E?style=for-the-badge)](https://modelcontextprotocol.io)

![License](https://img.shields.io/badge/License-MIT_0-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Educational-blue?style=for-the-badge)

**A production-oriented demonstration of scaling agentic systems from MVP to 50K orders/day**

**Shopping, powered by agents.**

[Overview](#overview) • [Architecture](#architecture-evolution) • [Quick Start](#quick-start) • [Demos](#running-the-demos) • [Resources](#technical-resources)

</div>

---

## Overview

**AgentStride** demonstrates the architectural evolution of agentic systems through three production-grade implementations. Built for AWS re:Invent 2025 (DAT309 Chalk Talk), this project showcases scaling patterns from a weekend MVP to enterprise-scale multi-agent orchestration with semantic search capabilities.

> **⚠️ Educational Use Only**: This demonstration is designed for learning purposes and illustrates production patterns without production-level error handling, monitoring, or security hardening.

### The AgentStride Story

A live-streaming shopping platform that evolved from 50 orders/day to 50,000 orders/day through three architectural iterations—demonstrating how thoughtful design enables exponential scaling without complete rewrites.

---

## Architecture Evolution

### Performance & Scale Comparison

| Metric              | Phase 1: Single Agent | Phase 2: Agent + MCP | Phase 3: Multi-Agent    |
| ------------------- | --------------------- | -------------------- | ----------------------- |
| **Daily Capacity**  | 50 orders             | 5,000 orders         | 50,000 orders           |
| **Response Time**   | ~2.0s                 | ~3.5s                | ~200ms                  |
| **Architecture**    | Monolithic            | MCP-mediated         | Supervisor pattern      |
| **Database Access** | RDS Data API          | RDS Data API (MCP)   | RDS Data API + pgvector |
| **Search Type**     | Exact match           | Exact match          | Semantic (vector)       |
| **Coupling**        | Tight                 | Loose (MCP)          | Loose + Specialized     |

### Technical Architecture Details

<details>
<summary><strong>Phase 1: Single Agent Architecture</strong></summary>

**Capacity:** 50 orders/day | **Response Time:** ~2.0s

**Architecture:**

- **1 Agent:** Monolithic agent handles all responsibilities
- **5 Custom Tools:**
  - `_lookup_product()` - Product lookup by ID
  - `_search_products()` - Text-based product search (ILIKE)
  - `_check_inventory()` - Real-time inventory verification
  - `_calculate_total()` - Price calculation with tax/shipping
  - `_process_order()` - Order persistence and workflow
- **Database:** Aurora PostgreSQL access via RDS Data API
- **Pattern:** Tight coupling with inline database operations

**Key Characteristics:**

- ReAct pattern with Chain of Thought reasoning
- Sequential tool execution
- RDS Data API for serverless database access
- Ideal for MVPs and prototypes

</details>

<details>
<summary><strong>Phase 2: MCP-Powered Architecture</strong></summary>

**Capacity:** 5,000 orders/day | **Response Time:** ~3.5s

**Architecture:**

- **1 Agent:** Single agent with MCP integration
- **MCP Tools:** Auto-discovered from `awslabs.postgres-mcp-server`
  - `run_query` - SQL queries via RDS Data API
  - `get_table_schema` - Table schema inspection
  - `connect_to_database` - Database connection management
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
from strands.tools.mcp import MCPClient

# Initialize MCP client - connection established via connect_to_database tool
mcp_client = MCPClient(
    server_name="postgres-mcp-server",
    command="uvx",
    args=["awslabs.postgres-mcp-server@latest"]
)

# Connection is established using the connect_to_database tool with:
# - database_type: "APG" (Aurora PostgreSQL)
# - connection_method: "rdsapi" (RDS Data API)
# - cluster_identifier, db_endpoint, database, port, region
```

</details>

<details>
<summary><strong>Phase 3: Multi-Agent Supervisor Architecture</strong></summary>

**Capacity:** 50,000 orders/day | **Response Time:** ~200ms

**Architecture:**

- **4 Specialized Agents:**
  1. **Supervisor Agent** 🎯 - Workflow orchestration (delegates only, no direct tools)
  2. **Search Agent** 🔍 - Semantic product discovery
     - Tool: `_semantic_search_tool()` - pgvector-powered text search
  3. **Product Agent** 📋 - Product information and inventory
     - Tool: `_get_details_tool()` - Full product information
     - Tool: `_check_inventory_tool()` - Stock availability
  4. **Order Agent** 🛒 - Order processing and confirmation
     - Tool: `_calculate_total_tool()` - Price calculation with tax/shipping
     - Tool: `_process_order_tool()` - Order creation and confirmation
- **Database:** Aurora PostgreSQL + pgvector extension
- **Embeddings:** Cohere Embed v4 (1024 dimensions)
- **Search:** Vector embeddings with HNSW index (cosine similarity)
- **Pattern:** Supervisor orchestration with specialized agents

**Key Improvements:**

- Parallel agent execution for sub-200ms response times
- Semantic search using vector embeddings
- Single Responsibility Principle per agent
- Natural language product discovery
- Semantic search using Cohere Embed v4 embeddings
- Horizontal and vertical scaling capabilities

**Semantic Search Implementation:**

```sql
-- HNSW index for fast vector similarity search
CREATE INDEX ON products USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 128);

-- Natural language search: "comfortable running shoes"
-- Matches semantically similar products, not just keywords
SELECT * FROM semantic_product_search(query_embedding, 5);
```

</details>

---

## Quick Start

### Prerequisites

**Required:**

- Python 3.11+
- AWS Account with Amazon Bedrock access
- Claude Opus 4.7 model access in Bedrock
- AWS CLI configured with credentials

**Recommended:**

- Familiarity with agentic frameworks (Strands, LangChain)
- Understanding of Model Context Protocol (MCP)
- Basic PostgreSQL and vector search knowledge

### Installation

```bash
# Clone repository
git clone https://github.com/aws-samples/sample-dat309-agentic-workflows-aurora-mcp
cd sample-dat309-agentic-workflows-aurora-mcp/agentstride

# Run automated setup
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials and region

# Verify installation
python scripts/verify_installation.py
```

### Database Setup

```bash
# Option 1: Create Aurora cluster via script
./scripts/create_cluster.sh

# Option 2: Use existing cluster - update .env with your cluster details

# Initialize database schema (creates tables, pgvector extension, HNSW index)
python scripts/init_aurora_schema.py

# Seed product data with Cohere Embed v4 embeddings (30 products, 6 categories)
python scripts/seed_data.py

# Verify semantic search is working
python scripts/test_semantic_search.py
```

### Environment Configuration

```bash
# .env file structure
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# Bedrock Configuration
BEDROCK_MODEL_ID=global.anthropic.claude-opus-4-7-v1
BEDROCK_REGION=us-east-1

# Embedding Configuration (Cohere Embed v4)
EMBEDDING_MODEL=global.cohere.embed-v4
EMBEDDING_DIMENSION=1024

# Aurora PostgreSQL Configuration
AURORA_CLUSTER_ARN=your_aurora_cluster_arn
AURORA_SECRET_ARN=your_secret_arn
AURORA_CLUSTER_IDENTIFIER=your_cluster_identifier
AURORA_CLUSTER_ENDPOINT=your_cluster_endpoint
AURORA_DATABASE=agentstride
```

---

## Web Application

The project includes a full-stack web application for interactive demos:

### Backend (FastAPI)

```bash
cd agentstride
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**API Endpoints:**

- `POST /api/chat` - Send message to agent
- `GET /api/products` - Get product catalog
- `WebSocket /ws/activity` - Real-time activity stream

### Frontend (React + Vite)

```bash
cd agentstride/frontend
npm install
npm run dev
```

Open http://localhost:5173 to view the application.

**Features:**

- Phase selector (1, 2, 3) to switch architectures
- Real-time activity panel showing agent operations
- Mock mode for offline demos
- Semantic search powered by Cohere Embed v4 (Phase 3)

---

## Demo Script

See [DEMO_SCRIPT.md](agentstride/DEMO_SCRIPT.md) for a complete 60-minute walkthrough with talking points, representative queries, and code highlights.

- HNSW vector indexing for similarity search

---

## Project Structure

```
agentstride/
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── DEMO_SCRIPT.md                 # 60-minute demo walkthrough
│
├── backend/                       # FastAPI backend
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Centralized configuration
│   ├── search_utils.py           # Shared search utilities
│   ├── agents/                   # Agent implementations
│   │   ├── phase1/agent.py       # Single agent (direct RDS)
│   │   ├── phase2/agent.py       # MCP integration
│   │   └── phase3/               # Multi-agent system
│   │       ├── supervisor.py     # Supervisor agent (orchestration)
│   │       ├── search_agent.py   # Semantic search
│   │       ├── product_agent.py  # Product details/inventory
│   │       └── order_agent.py    # Order processing
│   ├── db/                       # Database utilities
│   │   ├── rds_data_client.py    # RDS Data API client
│   │   ├── mcp_client.py         # MCP client
│   │   └── embedding_service.py  # Cohere embeddings
│   ├── routers/                  # API route handlers
│   └── tools/                    # Shared agent tools
│
├── frontend/                      # React frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── hooks/                # Custom React hooks
│   │   ├── sections/             # Page sections
│   │   └── types/                # TypeScript types
│   └── package.json
│
├── scripts/                       # Automation scripts
│   ├── setup.sh                  # Environment setup
│   ├── create_cluster.sh         # Aurora cluster provisioning
│   ├── delete_cluster.sh         # Cluster cleanup
│   ├── init_aurora_schema.py     # Database schema initialization
│   ├── seed_data.py              # Product data with embeddings
│   └── test_semantic_search.py   # Search verification
│
├── lib/                           # Core library modules
│   └── aurora_db.py              # Database operations
│
├── tests/                         # Test suite
│   └── test_embedding_properties.py  # Property-based tests
│
├── data/                          # Static data
│   └── products.json             # Product catalog
│
└── sample-images/                 # Visual search demo images
```

---

## Technical Stack

| Component           | Technology                  | Purpose                                              |
| ------------------- | --------------------------- | ---------------------------------------------------- |
| **Agent Framework** | Strands SDK                 | Agent orchestration, tool management, execution flow |
| **LLM Runtime**     | Amazon Bedrock              | Claude Opus 4.7 model hosting and inference          |
| **Database**        | Amazon Aurora PostgreSQL    | Transactional data storage with serverless v2        |
| **Vector Search**   | pgvector 0.8.0+             | Semantic search with HNSW indexing                   |
| **Embeddings**      | Cohere Embed v4             | Text embeddings, 1024 dimensions                     |
| **Protocol**        | Model Context Protocol      | Standardized tool/resource integration               |
| **MCP Server**      | awslabs.postgres-mcp-server | PostgreSQL access via RDS Data API                   |
| **Backend**         | FastAPI                     | REST API and WebSocket server                        |
| **Frontend**        | React 18 + Vite             | Interactive web application                          |
| **Styling**         | Tailwind CSS                | Utility-first CSS framework                          |
| **SDK**             | boto3                       | AWS service integration                              |
| **Language**        | Python 3.11+ / TypeScript   | Backend and frontend implementation                  |

---

## Troubleshooting

### AWS Authentication Issues

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Test Bedrock model invocation
aws bedrock-runtime invoke-model \
    --model-id global.anthropic.claude-opus-4-7-v1 \
    --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
    --region us-east-1 \
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
uvx awslabs.postgres-mcp-server@latest --help

# The MCP server connects via the connect_to_database tool
# with connection_method: "rdsapi" for RDS Data API access
# No command-line connection arguments needed - connection is established programmatically
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

### Python (Backend)

```txt
# Core Framework
python>=3.11
strands-agents>=0.1.0
boto3>=1.34.0
fastapi>=0.109.0
uvicorn>=0.27.0

# Vector Search (Phase 3)
numpy>=1.24.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
rich>=13.7.0

# Testing
pytest>=7.4.0
hypothesis>=6.100.0
```

### Node.js (Frontend)

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "framer-motion": "^11.0.0",
  "tailwindcss": "^3.4.0",
  "typescript": "^5.3.0",
  "vite": "^5.0.0"
}
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
