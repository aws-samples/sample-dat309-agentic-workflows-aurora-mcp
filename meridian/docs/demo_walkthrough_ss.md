# Demo walkthrough — presenter talking points

Concise script for the three live code areas: **Retrieval → Production → Workflow**.
Order matches the deck. Spine query: *"a romantic slow week somewhere with great wine."*
Memory beat: *"what did we discuss last time?"* Seeded traveler: **Alex Morgan** (`trv_meridian_demo`).

---

## 1. Retrieval — supervised hybrid search

**Files:** `agents/retrieval_03/supervisor.py`, `agents/retrieval_03/search_agent.py`

**Show the supervisor first.**
- `RetrievalAgent` has no DB access — its three `@tool`s (`_delegate_to_search/_package/_booking`) are thin delegation wrappers; Bedrock picks which specialist per turn.
- Point: one router, three specialists. Search owns discovery, Package owns details/availability, Booking owns holds/totals.

**Then open `search_agent.py` → `hybrid_search()`.** Walk the pipeline top-to-bottom:
1. **Embed** — Cohere Embed v4, 1024-dim.
2. **Arm 1 (semantic / meaning)** — `semantic_trip_search()` pgvector cosine, HNSW. *It's semantic-only; "hybrid" is assembled in Python.*
3. **Arm 2 (lexical / exact terms)** — `tsvector` + `websearch_to_tsquery` + `ts_rank`.
4. **Merge + dedup** by `package_id` — the "fusion" step. No weighted blend; reranker owns order.
5. **Rerank** — Cohere Rerank 3.5 cross-encoder reorders to top K. Falls back to hybrid order if unavailable.
- Note `candidate_limit = max(limit*5, 25)` — wide pool in (recall), reranker tightens (precision).

**One tool, whole pipeline.** The agent only sees `hybrid_search_tool`; everything above is hidden inside it.

**Likely Q:** *Why not just embeddings?* → cosine blurs exact terms (destination, operator); cross-encoder reads query+doc together. *Candidate count?* → ~25 default.

---

## 2. Production — AgentCore + Aurora RLS

**Files:** `agents/production_04/concierge.py`, `agents/production_04/memory_agent.py`

**Open `concierge.py → process_turn()`** (docstring maps the 6 steps):
1. **AgentCore Identity** — IAM/workload envelope (security span).
2. **Aurora RLS** — one transaction; `SET LOCAL app.current_traveler_id` pins per-traveler isolation. *Postgres enforces it, not app code.*
3. **AgentCore Runtime** — session envelope, microVM isolation.
4. **AgentCore Memory** — `list_recent_turns` + `semantic_recall` (session reads).
5. **AgentCore Gateway** — managed MCP `tools/list` + `tools/call`.
6. **persist_turn** — Aurora write + AgentCore Memory mirror.

**Then `memory_agent.py` — tiered memory.** Four `@tool`s, all read/write **Aurora**:
- `recall_session_context` → `conversation_messages`
- `recall_traveler_preferences` → `traveler_preferences`
- `recall_similar_interactions` → `trip_interactions` (pgvector)
- `persist_turn` → writes both Aurora **and** mirrors to AgentCore Memory
- **Split:** AgentCore = managed session layer; Aurora = durable system of record.

**Demo beat:** ask *"what did we discuss last time?"* → recalls the Tokyo thread, grounded in Alex's seeded prefs (shellfish allergy, boutique over chain) — **none in the prompt; all in Aurora**.

**Likely Q:** *AgentCore Memory and Aurora — redundant?* → No: managed session vs. durable record; `persist_turn` bridges them. *Need AgentCore for RLS?* → No, RLS is just Postgres.

---

## 3. Workflow — LangGraph StateGraph

**File:** `agents/orchestration_05/workflow.py`

**Show `_build_graph()`** — explicit `StateGraph(WorkflowState)`:
- Entry → `classify` → conditional fan-out by intent: `search` / `availability` / `memory_recall`.
- **The trick:** edge OUT of `search` is conditional — `if intent=="plan"` → `availability` (two sequential steps); else → `synthesize`.
- `availability`/`memory_recall` → `synthesize` → `END`.

**Durability.** `compile(checkpointer=PostgresSaver.from_conn_string(dsn))` → Aurora `langgraph_checkpoints`. State serializes after **every** node (all three workers emit `PostgresSaver.put`). Pause Tuesday, resume Thursday — identical state. Falls back to in-process `MemorySaver` if no DSN.

**The "plan" payoff:** *"plan a Tokyo trip and check the dates"* → `search → availability`, each checkpointed. That composition is what an explicit graph makes visible and resumable — a single tool call can't.

**Likely Q:** *LangGraph vs. Strands?* → Strands routes tools in a turn; LangGraph owns explicit, branchable, checkpointed flow across turns. They compose — Strands can run inside a node. *No Postgres?* → MemorySaver fallback; demo runs, durability lost.

---

### Dry-run checklist
- [ ] Spine query fails in Phase 1/2, lands in Phase 3 (Tuscany/Amalfi/Douro + scores)
- [ ] "What did we discuss last time?" fails in Phase 3, recalls in Phase 4
- [ ] Phase 4 trace shows RLS span + AgentCore Memory + audit row
- [ ] Phase 5 "plan" prompt shows search→availability + two checkpoints
- [ ] Tool name reads `hybrid_search_tool` everywhere (no stale `semantic_search_tool`)
