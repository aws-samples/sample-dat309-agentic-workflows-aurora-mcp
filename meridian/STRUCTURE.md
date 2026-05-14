# Meridian repository layout

## What runs in production (the demo)

```
frontend/src/App.tsx
  → sections: Hero, Products (trips grid), HowItWorks, Vision, Agent (live chat)
  → api/client.ts → backend :8000

backend/main.py
  → routers/chat.py      # Phases 1–4 (inline search + Phase 4 concierge)
  → routers/products.py  # GET /api/packages (+ legacy /api/products)
  → routers/memory.py    # GET /api/memory/{traveler_id}
```

Phase 4 is the only path that imports Strands agent modules at runtime:

- `backend/agents/phase4/concierge.py`
- `backend/agents/phase4/memory_agent.py`

Phases 1–3 execute inside `chat.py` (`phase1_search`, `phase2_search`, `phase3_search`). The matching files under `backend/agents/phase1|2|3/` are **reference Strands implementations** cited in trace `agent_file` paths — not imported by the live API.

## Directory map

| Path | Role |
| ---- | ---- |
| `backend/db/` | RDS Data API, embeddings, `schema.sql` |
| `backend/mcp/` | Live MCP client (Phase 2) |
| `backend/memory/` | Aurora traveler memory store |
| `backend/agents/phase4/` | Live concierge + memory agents |
| `backend/agents/phase1–3/` | Reference Strands agents (workshop code samples) |
| `backend/routers/` | FastAPI routes |
| `backend/catalog_compat.py` | Maps `trip_packages` rows → legacy API `Product` shape |
| `frontend/src/sections/` | Live SPA sections |
| `frontend/src/components/` | Shared UI (nav, trace, persona, thumbs) |
| `scripts/travel_catalog.py` | Trip + traveler seed source |
| `scripts/seed_data.py` | Seeds Aurora (packages + embeddings + demo traveler) |
| `docs/design/` | Static HTML design explorations (not served by the app) |
| `tests/` | Pytest |

## Naming debt (intentional compat)

The travel pivot kept some e-commerce names in the API/UI layer:

- `Product` / `product_id` in TypeScript and `/api/products` — trips from `trip_packages`
- `ProductsSection`, `ProductThumb`, `handleAddToCart` — display trips, not SKUs

A future rename to `Package` / `Trip` would be cosmetic only if the compat layer stays.

## Cleanup history

Removed dead code: duplicate `partner_runtime.py`, unused `ShopWithAI` stack, `mockData`, legacy `lib/aurora_db.py`, `data/products.json`, unused `backend/tools/`, unused WebSocket router, stub `/api/chat/image` endpoint, and the duplicate `agentstride/` tree at the repo root. Design HTML lives in `docs/design/`. Reference agents are documented in `backend/agents/README.md`.
