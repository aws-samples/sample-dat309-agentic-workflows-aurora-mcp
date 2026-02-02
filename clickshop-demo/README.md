# ClickShop Demo - Agentic e-Commerce Application

A modern web application demonstrating agentic e-commerce with three architectural approaches: from simple prototypes to production-ready multi-agent systems.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS credentials configured
- Aurora PostgreSQL cluster (or use mock mode)

### Backend Setup

```bash
cd clickshop-demo

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials

# Initialize database (if using Aurora)
python scripts/init_aurora_schema.py
python scripts/seed_data.py

# Start backend server
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd clickshop-demo/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:5173 to view the application.

## Three Phases of Evolution

### Phase 1: Direct Database Access (~100ms)

**The Prototype** - Perfect for MVPs and getting started quickly.

- Single agent with direct RDS Data API connection
- Keyword-based search with category matching
- Simple, fast to build, easy to debug

**Example queries that work:** `running shoes`, `Nike`, `fitness equipment`

**Limitation:** Semantic queries like `gear for my first marathon` return 0 results.

### Phase 2: MCP Abstraction (~100ms)

**The Standard** - Production-ready pattern with portability.

- Agent uses Model Context Protocol for database abstraction
- Same keyword search, but standardized interface
- Auto-discovered tools from MCP server
- Portable across different AI frameworks

**Same search capabilities as Phase 1**, but with better architecture.

### Phase 3: Multi-Agent Orchestration (~350ms)

**Production** - Scale and intelligence for real-world applications.

- **SupervisorAgent** orchestrates specialized agents
- **SearchAgent** handles semantic search with Nova Multimodal Embeddings
- Hybrid search: pgvector (semantic) + tsvector/tsrank (lexical)
- 70% semantic + 30% lexical scoring

**Example queries that now work:** `gear for my first marathon`, `help with muscle recovery`, `comfortable shoes for long runs`

The multi-agent flow:

1. SupervisorAgent receives request
2. SupervisorAgent delegates to SearchAgent
3. SearchAgent generates 1024-dim embedding
4. SearchAgent runs hybrid search
5. SearchAgent returns ranked results to Supervisor

## Mock Mode

The frontend includes a mock mode toggle for offline demos. When enabled:

- No backend connection required
- 30 mock products across 6 categories
- Simulated agent responses with phase-appropriate delays
- Generated activity entries

## Project Structure

```
clickshop-demo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Centralized configuration
│   ├── routers/             # API endpoints
│   ├── agents/              # Phase 1, 2, 3 agents
│   │   ├── phase1/          # Direct RDS agent
│   │   ├── phase2/          # MCP agent
│   │   └── phase3/          # Multi-agent system
│   │       ├── supervisor.py
│   │       ├── search_agent.py
│   │       ├── product_agent.py
│   │       └── order_agent.py
│   ├── tools/               # Agent tools
│   ├── db/                  # Database utilities
│   └── mcp/                 # MCP client
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── sections/        # Page sections
│   │   ├── hooks/           # Custom hooks
│   │   ├── mock/            # Mock data
│   │   └── types/           # TypeScript types
│   └── package.json
├── scripts/
│   ├── create_cluster.sh    # Aurora provisioning
│   ├── delete_cluster.sh    # Cluster cleanup
│   ├── init_aurora_schema.py
│   └── seed_data.py
├── tests/
│   └── test_embedding_properties.py
├── DEMO_SCRIPT.md           # 60-minute demo walkthrough
└── data/
    └── products.json
```

## API Endpoints

- `POST /api/chat` - Send message to agent (supports phase 1, 2, 3)
- `POST /api/chat/image` - Upload image for visual search (Phase 3)
- `GET /api/products` - Get product catalog
- `WebSocket /ws/activity` - Real-time activity stream

## Tech Stack

| Component         | Technology                            | Purpose                     |
| ----------------- | ------------------------------------- | --------------------------- |
| **Frontend**      | React 18, Tailwind CSS, Framer Motion | Modern UI with animations   |
| **Backend**       | FastAPI, Python 3.11+                 | API server                  |
| **Database**      | Aurora PostgreSQL Serverless v2       | Transactional data          |
| **Vector Search** | pgvector 0.8.0, HNSW index            | Semantic similarity         |
| **Embeddings**    | Amazon Nova Multimodal                | 1024-dim text/image vectors |
| **LLM**           | Claude Sonnet 4.5 (Bedrock)           | Agent reasoning             |
| **Protocol**      | Model Context Protocol (MCP)          | Standardized tool interface |

## Demo Script

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for a complete 60-minute walkthrough with talking points, representative queries, and code highlights.
