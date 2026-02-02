# ClickShop Demo - Web Application

A modern web application demonstrating AI-powered e-commerce with three architectural approaches.

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

## Mock Mode

The frontend includes a mock mode toggle for offline demos. When enabled:

- No backend connection required
- 30 mock products across 6 categories
- Simulated agent responses with phase-appropriate delays
- Generated activity entries

## Architecture

### Phase 1: Direct Database Access

- Single Strands agent with Claude Sonnet 4.5 (cross-region inference)
- RDS Data API for Aurora PostgreSQL access
- Custom tools: lookup_product, search_products, check_inventory, calculate_total, process_order

### Phase 2: MCP Abstraction

- Strands agent with MCP client integration
- awslabs.postgres-mcp-server for RDS Data API
- Auto-discovered tools from MCP server

### Phase 3: Multi-Agent System

- Supervisor agent orchestrating specialized agents (no direct tools)
- Search Agent with Amazon Nova Multimodal Embeddings - 1024 dimensions
- Product Agent for inventory and details
- Order Agent for processing
- Visual search capability with image upload (same embedding model for cross-modal search)
- pgvector HNSW index for semantic similarity search

## Project Structure

```
clickshop-demo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── routers/             # API endpoints
│   ├── agents/              # Phase 1, 2, 3 agents
│   ├── tools/               # Agent tools
│   └── db/                  # Database utilities
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
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
└── data/
    └── products.json
```

## API Endpoints

- `POST /api/chat` - Send message to agent
- `POST /api/chat/image` - Upload image for visual search (Phase 3)
- `GET /api/products` - Get product catalog
- `WebSocket /ws/activity` - Real-time activity stream

## Tech Stack

- **Frontend**: React 18, Tailwind CSS, Framer Motion, TypeScript
- **Backend**: FastAPI, Strands SDK, RDS Data API
- **Database**: Aurora PostgreSQL Serverless v2, pgvector 0.8.0
- **AI Models**: Amazon Bedrock (Claude Sonnet 4.5), Amazon Nova Multimodal Embeddings
- **Protocol**: Model Context Protocol (MCP)
