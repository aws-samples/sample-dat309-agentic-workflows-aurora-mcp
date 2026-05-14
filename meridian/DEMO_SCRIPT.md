# Meridian Demo Script

## Building agentic travel workflows with Aurora PostgreSQL, MCP, and Strands Agents

**Duration:** ~60 minutes  
**Format:** Live web demo + optional code walkthrough  
**Tagline:** Plan. Fly. Land.

---

## Key files

| File | Purpose |
| ---- | ------- |
| `backend/routers/chat.py` | Live chat for phases 1–4 (`phase1_search`, `phase2_search`, `phase3_search`, `phase4_search`) |
| `backend/db/schema.sql` | Travel-native Aurora schema (`trip_packages`, travelers, memory tables) |
| `backend/db/rds_data_client.py` | RDS Data API client |
| `backend/db/embedding_service.py` | Cohere Embed v4 on Bedrock (1024d) |
| `backend/mcp/mcp_client.py` | MCP client (Phase 2) |
| `backend/agents/phase3/supervisor.py` | Strands supervisor + specialist agents |
| `backend/agents/phase4/concierge.py` | `ConciergeOrchestrator` (Phase 4) |
| `backend/agents/phase4/memory_agent.py` | Strands `@tool` memory recall/persist |
| `backend/memory/store.py` | Aurora memory CRUD |
| `frontend/src/sections/AgentSection.tsx` | Live demo UI (chat + trace) |
| `frontend/src/components/TravelerPersona.tsx` | Alex & Jordan Chen persona card |
| `scripts/travel_catalog.py` | 30 trip packages + demo traveler seed |

---

## Pre-demo setup (~5 minutes before)

**Terminal 1 — backend**

```bash
cd meridian
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — frontend**

```bash
cd meridian/frontend
npm run dev
```

**Verify**

- http://localhost:5173 loads Meridian
- http://localhost:8000/health returns `healthy`
- `GET /api/memory/trv_meridian_demo` returns Alex & Jordan profile facts
- Scroll to **Live demo** — persona card and phase pills visible

**If Aurora was reset**

```bash
python scripts/init_aurora_schema.py
python scripts/seed_data.py
```

---

## Part 1 — Introduction (5 min)

### What to say

> "Meridian is an agentic **travel concierge** — not a chatbot bolted onto a search box. We climb a deliberate ladder: **filters → MCP tools → semantic search → traveler memory**. Each phase adds one capability on the same Aurora catalog."

Point to the **Architecture** section (four phase cards):

| Phase | Name | One-liner |
| ----- | ---- | --------- |
| 1 | Direct filters | SQL on `trip_packages` via RDS Data API |
| 2 | MCP tools | Same queries through postgres-mcp-server |
| 3 | Specialist agents | Hybrid pgvector + full-text; Strands supervisor |
| 4 | Personal memory | Returning traveler — profile + preferences in Aurora |

> "Phases 1–3 teach the retrieval stack. Phase 4 is the production story: the agent **remembers** Alex and Jordan before it searches."

---

## Part 2 — Phase 1 · Filters (12 min)

**Select:** `Phase 1 · Filters`

### What to say

> "Phase 1 is the lab. One Strands agent, hardcoded tools, direct RDS Data API. Fast, debuggable — but it only understands **exact filters**, not intent."

### Demo queries that work

| Query | What happens |
| ----- | ------------ |
| `City breaks` | Trip type filter on `trip_packages` |
| `Beach & Resort` | Trip type match |
| `Business travel under $1500` | Type + price filter |

**Point to the agent trace:** RDS connection → filter SQL → package rows returned.

### Demo query that breaks (on purpose)

| Query | What happens |
| ----- | ------------ |
| `Romantic week in Europe` | **0 results** — no semantic understanding |

> "The user didn't say the wrong thing — Phase 1 did. That's the hook for Phase 3."

### Optional code walkthrough

- `backend/routers/chat.py` → `phase1_search`
- `backend/search_utils.py` → `parse_search_query`, `execute_keyword_search`

---

## Part 3 — Phase 2 · MCP (12 min)

**Select:** `Phase 2 · MCP`

### What to say

> "Phase 2 changes the **interface**, not the intelligence. The agent still does filter search underneath — but the database is reached through **MCP** instead of hardcoded SQL in the agent."

### Demo queries

| Query | Notes |
| ----- | ----- |
| `Adventure & Outdoors` | Same filter logic, MCP path in trace |
| `Wellness & Luxury` | Show `MCP tools connected` span |
| `Tokyo culture trip` | May partial-match; still not true semantic search |

### Demo query that still breaks

| Query | Notes |
| ----- | ----- |
| `Beach vacation with snorkeling` | Vague intent — Phase 3 needed |

### Optional code walkthrough

- `backend/mcp/mcp_client.py`
- `backend/agents/phase2/agent.py`

> "MCP gives you portability and a standard tool surface. It does not magically add embeddings."

---

## Part 4 — Phase 3 · Intent (15 min)

**Select:** `Phase 3 · Intent`

### What to say

> "Phase 3 is where natural language works. **Cohere Embed v4** (1024 dimensions) plus PostgreSQL **pgvector** and **tsvector** — hybrid ranking. A **Strands supervisor** delegates to specialist agents in the trace."

### How search works (say while trace runs)

1. Supervisor receives query  
2. SearchAgent generates query embedding (Bedrock)  
3. Hybrid SQL: ~70% semantic + ~30% lexical  
4. Ranked `trip_packages` returned  

### Demo queries

| Query | Expected |
| ----- | -------- |
| `Romantic week in Europe` | Packages in EU / romance-themed (Phase 1 returned 0) |
| `Weekend in Paris under $2k` | Price-aware semantic match |
| `Family-friendly beach resort` | Intent-based matches |
| `Is the Maldives package available?` | Routes to ProductAgent availability path |

### The money shot — cross-phase comparison

1. Phase 1: `Romantic week in Europe` → 0 results  
2. Phase 3: same query → ranked trips  

> "Same database. Same catalog. Different retrieval architecture."

### Optional code walkthrough

- `backend/routers/chat.py` → `phase3_search`
- `backend/db/embedding_service.py` → `cohere.embed-v4:0`, `output_dimension: 1024`
- `backend/db/schema.sql` → `semantic_trip_search`, HNSW index

---

## Part 5 — Phase 4 · Personal (15 min)

**Select:** `Phase 4 · Personal` (or click **Chat as Alex & Jordan → Phase 4** on the persona card)

### What to say

> "Phase 4 is the returning traveler. Meet **Alex & Jordan Chen** from SFO — party of two, Tokyo culture trip Oct 12–19, shellfish allergy. None of that is in the prompt; it's in **Aurora** (`traveler_profiles`, `traveler_preferences`, `conversation_messages`, `trip_interactions`)."

Point to the **persona card** and trace memory spans:

- `recall_traveler_preferences`  
- `recall_session_context`  
- `recall_similar_interactions`  
- `persist_turn`  

### Demo queries

| Query | What to highlight |
| ----- | ----------------- |
| `Tokyo trip for two in October` | Tokyo packages + memory-aware greeting |
| `Beach escape under $2500 — remember my food allergies` | Budget + dietary context from profile |
| `What did we discuss last time about Iceland?` | Session / interaction recall (richer after prior turns) |

### Follow-up in same session

Run a second query without clearing chat — show `conversation_id` continuity and growing session memory.

### Optional code walkthrough

- `backend/agents/phase4/concierge.py` → `ConciergeOrchestrator.process_turn`
- `backend/agents/phase4/memory_agent.py` → `@tool` methods
- `backend/memory/store.py` → Aurora reads/writes

> "Orchestration here is **Strands Agents** + procedural routing in `chat.py` — not LangGraph."

---

## Part 6 — Booking demo (optional, 5 min)

From a trip result card, click **Book now** or send an order intent.

Trace shows booking flow spans; `bookings` / `booking_lines` tables persist the demo reservation.

```bash
curl -s -X POST http://localhost:8000/api/chat/order \
  -H 'Content-Type: application/json' \
  -d '{"product_id":"CTY-002","phase":3,"quantity":1}'
```

---

## Part 7 — Architecture summary (5 min)

### Ladder recap

```
Phase 1   Direct filters     RDS Data API → trip_packages
Phase 2   MCP tools          Agent → MCP → Aurora
Phase 3   Specialist agents  Embed v4 + hybrid search + supervisor
Phase 4   Personal memory    Concierge + Aurora memory → then search
```

### When teams use each pattern

| Phase | Good for |
| ----- | -------- |
| 1 | MVPs, internal tools, deterministic reporting |
| 2 | Standardizing DB access across agents and frameworks |
| 3 | Customer-facing natural language search at scale |
| 4 | Returning users, preferences, compliance, multi-turn planning |

### Key takeaways

1. **Aurora is the system of record** — catalog, vectors, and memory in one database  
2. **MCP standardizes tools** — it doesn't replace good retrieval  
3. **Embeddings change the UX** — intent queries work without keyword luck  
4. **Memory changes the product** — Phase 4 feels like a concierge, not a search box  

---

## Query cheat sheet

### Phase 1 — works / breaks

| Works | Breaks |
| ----- | ------ |
| City breaks | Romantic week in Europe |
| Beach & Resort | Family trip with kids who love theme parks |
| Business travel under $1500 | |

### Phase 2 — works / breaks

| Works | Breaks |
| ----- | ------ |
| Adventure & Outdoors | Beach vacation with snorkeling |
| Wellness & Luxury | Quick conference stopover in Singapore |
| Tokyo culture trip | |

### Phase 3 — suggested

- Weekend in Paris under $2k  
- Family-friendly beach resort  
- Is the Maldives package available?  
- Romantic week in Europe *(compare to Phase 1)*  

### Phase 4 — suggested (as Alex & Jordan)

- Tokyo trip for two in October  
- Beach escape under $2500 — remember my food allergies  
- What did we discuss last time about Iceland?  

---

## curl quick tests

```bash
# Health
curl -s http://localhost:8000/health | jq .

# Memory profile
curl -s http://localhost:8000/api/memory/trv_meridian_demo | jq .

# Phase 1 — filter
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"City breaks","phase":1}' | jq '.message, (.products | length)'

# Phase 3 — semantic
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Romantic week in Europe","phase":3}' | jq '.message, (.products | length)'

# Phase 4 — memory + search
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Tokyo trip for two in October","phase":4,"customer_id":"trv_meridian_demo"}' \
  | jq '.message, .conversation_id, (.products | length), (.memory_facts | length)'
```

---

## Troubleshooting

**Backend not responding**

```bash
curl -s http://localhost:8000/health
# restart
uvicorn backend.main:app --reload --port 8000
```

**Phase 3/4 slow on first query**

- First embedding call to Bedrock adds ~1–3s. Normal for cold path.

**`ValidationException: invalid model identifier` (embeddings)**

- Set `EMBEDDING_MODEL=cohere.embed-v4:0` and `EMBEDDING_DIMENSION=1024` in `.env`
- Ensure model access is enabled in Bedrock console (us-east-1)

**`expected 1024 dimensions, not 1536`**

- Cohere v4 defaults to 1536d; embedding service must pass `output_dimension: 1024` to match `vector(1024)` in schema.

**Phase 4: "error loading memory"**

- Check Aurora has seed data: `python scripts/seed_data.py`
- Verify `travelers` row `trv_meridian_demo` exists

**No trip results**

- Confirm seed ran (30 packages in `trip_packages`)
- Try Phase 3 with a simpler query: `Tokyo culture`

**Frontend shows Offline**

- Backend must be on port 8000; CORS allows localhost:5173

---

## Demo traveler reference

| Field | Value |
| ----- | ----- |
| ID | `trv_meridian_demo` |
| Name | Alex & Jordan Chen |
| Home | SFO |
| Party | 2 |
| Goal | Tokyo culture trip — Oct 12–19 |
| Dietary | Shellfish allergy |
| Budget | ~$2k–3.5k per person |

---

## Resources

- [README.md](README.md) — setup and architecture  
- [backend/db/schema.sql](backend/db/schema.sql) — full DDL  
- [Strands Agents](https://github.com/strands-agents/sdk-python)  
- [Amazon Bedrock — Cohere Embed v4](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-embed-v4.html)  
- [Model Context Protocol](https://modelcontextprotocol.io/)
