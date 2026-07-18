# CLAUDE.md

Guidance for Claude Code (and other AI dev tools) working in this repo. This is
the **canonical** AI-rules file — keep instructions here, not scattered elsewhere.

## What this is

**Mook** — a RAG (retrieval-augmented generation) proof-of-concept. FastAPI backend
does document ingestion, pgvector similarity search, and LLM answer generation over
retrieved context. A React (Vite) UI talks to it. Mock SD-WAN / ServiceNow APIs back
the infrastructure workflow providers.

> Proof of concept, not production code.

## Architecture

```
react-ui (Vite, :5173) ──HTTP──> backend (FastAPI, :8000) ──> Postgres + pgvector (:5432)
                                        │
                                        ├── LLM providers  (app/llm/*)        answer generation
                                        └── Workflow providers (app/workflows/*) query routing + context
mock_sdwan (:8081) / mock_servicenow (:8082) back the infra workflow providers
```

Key backend paths:
- `backend/app/main.py` — FastAPI app + routes; `/search/text/` is the main RAG flow.
- `backend/app/llm/` — LLM providers behind `LLMFactory` (`factory.py`). Interface: `base.py`.
- `backend/app/workflows/` — workflow providers behind `WorkflowManager` (`manager.py`). Interface: `base.py`.
- `backend/app/memory.py` — conversation persistence.

## Running

```bash
./dev.sh start                 # bring up the whole stack via docker compose
./dev.sh logs [service]        # tail logs
./dev.sh rebuild [backend|react-ui|db]
./dev.sh stop
```
- Backend API: http://localhost:8000  (docs at `/docs`)
- React UI: http://localhost:5173
- Mock SD-WAN: :8081 · Mock ServiceNow: :8082

## LLM providers — how they work

Providers implement `LLMProvider` (`backend/app/llm/base.py`): `generate_response()`
and `health_check()`. `LLMFactory.create_provider(name)` builds one; the active
provider is chosen by the `LLM_PROVIDER` env var (default `claude`).

- **`claude`** (default) — `ClaudeProvider` shells out to the `claude -p` CLI and uses
  the **Claude subscription** (no API key). This project has no API token bucket, so
  this is the intended default. Config: `CLAUDE_BIN`, `CLAUDE_MODEL`, `CLAUDE_TIMEOUT`.
- `azure` / `openai` — API-key providers (need the keys in `.env`).
- `mock` — deterministic, offline. Providers needing missing creds fall back to `mock`.

**Adding a provider:** implement `LLMProvider`, register it in `factory.py`'s
`_providers`, then select it via `LLM_PROVIDER`. See `/add-provider`.

## Conventions

- Python: `black` (line-length 88) + `isort` (profile=black) — see `backend/pyproject.toml`.
- Match existing style; keep the provider interfaces stable.
- Pin dependency versions in `requirements.txt`.

## Working agreements

- **Plan then execute.** Non-trivial work starts in plan mode (this repo defaults to
  it). Get the plan approved before editing.
- **Commit only when asked.** Branch off `master`; never commit/push unprompted.
- **Use `claude -p` for automation**, not the API — subscription auth, no token bucket.
- The Streamlit `ui/` is being retired in favor of `react-ui/`; don't add to it.
