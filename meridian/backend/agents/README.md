# Reference Strands agents (Phases 1–3)

These modules are **workshop code samples** cited in trace `agent_file` paths. They are **not imported** by the live API.

Live routing runs in `backend/routers/chat.py` (`phase1_search`, `phase2_search`, `phase3_search`). Phase 4 uses `phase4/concierge.py` and `phase4/memory_agent.py` at runtime.

## Important

- SQL and prompts in `phase1/`, `phase2/`, and `phase3/` still reflect the **pre-travel e-commerce pivot** in places.
- Imports use legacy paths (`from db.rds_data_client`) and will not run without adjustment.
- Do not treat these files as production code — read them alongside `chat.py` and `STRUCTURE.md`.
