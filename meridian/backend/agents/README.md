# Reference Strands agents (Phases 1–3)

These modules are **workshop code samples** cited in trace `agent_file` paths. They are **not imported** by the live API.

Live routing runs in `backend/routers/chat.py` (`phase1_search`, `phase2_search`, `phase3_search`). Phase 4 uses `phase4/concierge.py` and `phase4/memory_agent.py` at runtime.

SQL, prompts, and tools in `phase1/`, `phase2/`, and `phase3/` are aligned with the **travel schema** (`trip_packages`, `bookings`, `travelers`). Class names like `ProductAgent` are kept for trace-path compatibility with the live demo UI.
