# Mook

**Disclaimer this is a proof of concept and in no way intended to be run as production code.** 

Mook is a powerful RAG (retrieval augmented generation) system that combines document retrieval with large language models to provide accurate, context-aware responses. The system features a FastAPI backend for document processing and vector search, and a Streamlit frontend for an intuitive user interface.

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

### Frontend (Streamlit)
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

- Python 3.8+
- PostgreSQL with pgvector extension
- Azure OpenAI API access (or OpenAI API)
- Docker (optional, for containerized deployment)

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/rag_db

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_MODEL=gpt-35-turbo
```

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
- Streamlit frontend

3. Access the application:
- Frontend: http://localhost:8501
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
./dev.sh rebuild [service]  # service can be: backend, ui, or db

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
The Streamlit interface can be customized by modifying `ui/app.py`. The interface supports:
- Custom styling
- Additional widgets
- New interaction patterns

## Acknowledgments

- FastAPI for the backend framework
- Streamlit for the frontend framework
- LlamaIndex for document processing
- Azure OpenAI for language model capabilities
- PostgreSQL and pgvector for vector storage 
