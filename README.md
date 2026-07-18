# Mook

**Disclaimer this is a proof of concept and in no way intended to be run as production code.** 

Mook is a powerful RAG (retrieval augmented generation) system that combines document retrieval with large language models to provide accurate, context-aware responses. The system features a FastAPI backend for document processing and vector search, and a React (Vite) frontend for an intuitive user interface.

By default the backend answers using your **Claude subscription** via the `claude -p` CLI (no API key / token bucket required). Azure OpenAI, OpenAI, and an offline mock provider are also supported — see [Environment Variables](#environment-variables).

[![Watch the video](https://img.youtube.com/vi/DdN5RWkfXo4/0.jpg)](https://www.youtube.com/watch?v=DdN5RWkfXo4)

## Features

- **Document Processing**
  - PDF document ingestion and processing
  - Excel file support
  - URL-based document ingestion
  - Automatic text chunking and embedding generation

- **Vector Search**
  - Efficient similarity-based document retrieval
  - Configurable similarity thresholds
  - Support for multiple document types

- **Conversation Management**
  - Persistent conversation history
  - Context-aware responses
  - Memory window for maintaining context

- **Multiple Workflow Providers**
  - Knowledge Base Provider for document queries
  - Infrastructure Configuration Provider for network configuration queries
  - Extensible provider architecture

- **User Interface**
  - Clean, intuitive Streamlit interface
  - Real-time chat interactions
  - Document upload and management
  - Conversation history viewing

## System Architecture

### Backend (FastAPI)
- Document processing and embedding generation
- Vector search and retrieval
- Conversation management
- Multiple workflow providers
- RESTful API endpoints

### Frontend (React + Vite)
- Interactive chat interface
- Document upload and management
- Conversation history viewing
- Real-time response display

### Database (PostgreSQL)
- Vector-enabled PostgreSQL database
- Efficient storage and retrieval of embeddings
- Conversation history persistence
- Automatic pgvector extension setup

### Mock API
- Simulated infrastructure controller API
- Mock network configuration data
- Device status and configuration simulation
- Integration testing environment

## Prerequisites

- Python 3.12
- PostgreSQL with pgvector extension
- An LLM provider — one of:
  - **Claude subscription** with the [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) installed and logged in (default; no API key)
  - Azure OpenAI or OpenAI API access
- Docker (recommended, for containerized deployment)

## Environment Variables

Copy `.env.example` to `.env` and fill it in. Key settings:

```env
# Database
DATABASE_URL=postgresql://user:password@db:5432/rag_db

# LLM provider: claude (default) | azure | openai | mock
LLM_PROVIDER=claude

# Claude provider (uses the `claude -p` CLI + your subscription; no API key)
CLAUDE_MODEL=            # optional model alias, e.g. claude-sonnet-5

# Azure OpenAI (only if LLM_PROVIDER=azure)
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_MODEL=gpt-35-turbo
```

### Claude provider in Docker

The backend container runs `claude -p` to reach your subscription. `docker-compose.dev.yml`
installs the CLI in the image and mounts your host credentials read-only
(`${HOME}/.claude:/root/.claude:ro`), so you must have run `claude` (logged in) on the
host first. Prefer not to mount credentials? Run the backend natively with `uvicorn`
where `claude` is already authenticated, or set `LLM_PROVIDER=mock` for offline use.

## Running the System

The project includes a `dev.sh` script that manages the development environment using Docker Compose. This is the recommended way to run the system in development.

1. Make the script executable:
```bash
chmod +x dev.sh
```

2. Start the development environment:
```bash
./dev.sh start
```

This will start all services:
- PostgreSQL database with pgvector
- Mock SD-WAN API
- Mock Change Request API
- Backend API
- React frontend

3. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Mock SD-WAN API: http://localhost:8081
- Mock Change Request API: http://localhost:8082

### Development Script Commands

The `dev.sh` script provides several useful commands:

```bash
# Start all services
./dev.sh start

# Stop all services
./dev.sh stop

# Rebuild a specific service
./dev.sh rebuild [service]  # service can be: backend, react-ui, or db

# View logs
./dev.sh logs [service]     # service is optional
```

## API Endpoints

### Document Management
- `POST /ingest/pdf_url`: Ingest PDF from URL
- `POST /ingest/file`: Upload and process PDF file
- `POST /ingest/excel`: Process Excel files

### Search and Query
- `POST /search/`: Vector-based similarity search
- `POST /search/text/`: Natural language text search

### Conversation Management
- `GET /conversations`: List all conversations
- `GET /conversations/{conversation_id}`: Get conversation history
- `DELETE /conversations/{conversation_id}`: Delete specific conversation
- `DELETE /conversations`: Delete all conversations

### Administration
- `GET /admin/table-counts`: Get database statistics
- `DELETE /admin/embeddings`: Clear all embeddings
- `GET /workflows/capabilities`: List available workflow providers

## Development

### Adding New Workflow Providers
1. Create a new provider class inheriting from `WorkflowProvider`
2. Implement required methods: `can_handle`, `get_context`, `get_capabilities`
3. Register the provider in `main.py`

### Customizing the UI
The React interface lives in `react-ui/` (Vite + MUI). Components are under
`react-ui/src/components/` (Chat, Search, Sidebar) and the API client in
`react-ui/src/services/api.ts`.

## Acknowledgments

- FastAPI for the backend framework
- React + Vite for the frontend framework
- LlamaIndex for document processing
- Claude (via the Claude Code CLI), with Azure OpenAI / OpenAI as alternatives, for language model capabilities
- PostgreSQL and pgvector for vector storage 
