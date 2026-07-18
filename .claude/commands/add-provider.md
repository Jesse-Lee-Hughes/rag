---
description: Add a new LLM or workflow provider following this repo's pattern
---

Add a provider to the backend. Delegate to the `provider-builder` subagent, or follow
its checklist directly. Target: **$ARGUMENTS**

1. Determine family: **LLM provider** (`backend/app/llm/`) or **workflow provider**
   (`backend/app/workflows/`). If unclear, ask.
2. Implement against the family's `base.py` interface, mirroring the closest existing
   provider.
3. Wire it up:
   - LLM: register in `factory.py::_providers`; select via `LLM_PROVIDER` env.
   - Workflow: register with `WorkflowManager.register_provider(...)`.
4. Handle missing credentials gracefully (raise `ValueError` → factory falls back to mock).
5. `black` + `isort` the changes, add a smoke test, and report how you verified it.
6. Do not commit unless asked.
