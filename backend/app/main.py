import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.utils import LlamaVectorizer
from app.database import engine, Base, get_db, E5Embedding, Conversation
from app.schemas import (
    EmbeddingResponse,
    EmbeddingListResponse,
    TextSearchRequest,
    LLMResponse,
    ConversationHistory,
    ConversationListResponse
)
from llama_index.core import Document
import os
import tempfile
from app.llm.factory import LLMFactory
from app.memory import ConversationMemory
from app.workflows.manager import WorkflowManager
from app.workflows.sdwan_provider import SDWANWorkflowProvider
from app.workflows.knowledge_provider import KnowledgeBaseWorkflowProvider
from app.workflows.servicenow_provider import ServiceNowWorkflowProvider


app = FastAPI(title="RAG Vector Search API")

Base.metadata.create_all(bind=engine)

vectorizer = LlamaVectorizer()

llm_provider = LLMFactory.create_provider("azure")


workflow_manager = WorkflowManager()
workflow_manager.register_provider(ServiceNowWorkflowProvider())
workflow_manager.register_provider(SDWANWorkflowProvider())
workflow_manager.register_provider(
    KnowledgeBaseWorkflowProvider(next(get_db()), vectorizer),
    is_fallback=True,
)


@app.post("/ingest/pdf_url", response_model=EmbeddingListResponse)
def upload_pdf_and_store_embeddings(url: str, db: Session = Depends(get_db)):
    try:
        # Use the global vectorizer
        text_content = vectorizer.convert_pdf_to_text(url)
        results = vectorizer.process_document(text_content, db, source_document=url)

        formatted_results = [
            EmbeddingResponse(
                id=result.id,
                text=result.text,
                vector=result.vector,
                source_document=result.source_document,
                metadata=result.get_metadata() or {},
            )
            for result in results
        ]

        return EmbeddingListResponse(embeddings=formatted_results)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")


@app.post("/ingest/file", response_model=EmbeddingListResponse)
async def upload_file_and_store_embeddings(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    try:
        # Verify file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Create temporary file to store upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process the PDF file
            text_content = vectorizer.convert_pdf_to_text(tmp_path)
            # Use filename as source document identifier
            results = vectorizer.process_document(
                text_content, db, source_document=file.filename
            )

            formatted_results = [
                EmbeddingResponse(
                    id=result.id,
                    text=result.text,
                    vector=result.vector,
                    source_document=result.source_document,
                    metadata=result.get_metadata() or {},
                )
                for result in results
            ]

            return EmbeddingListResponse(embeddings=formatted_results)

        finally:
            # Clean up temporary file
            os.unlink(tmp_path)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@app.post("/search/text/", response_model=LLMResponse)
async def text_search(search_request: TextSearchRequest, db: Session = Depends(get_db)):
    """Handle text queries with workflow routing"""
    try:
        memory = ConversationMemory(db)
        conversation_id = search_request.conversation_id or memory.create_conversation()

        # Get appropriate provider (will always return a provider due to fallback)
        provider = await workflow_manager.get_provider(search_request.query_text)
        print("Type of provider:", type(provider))

        # Handle query with memory support
        result = await provider.handle_query(
            search_request.query_text,
            memory=memory,
            conversation_id=conversation_id,
        )
        # Generate response using LLM
        response = await llm_provider.generate_response(
            query=search_request.query_text,
            context=[str(result["context"])],
            system_prompt=result["prompt"],
            temperature=0.5,
        )

        # Store the interaction in memory
        memory.add_interaction(
            conversation_id=conversation_id,
            query=search_request.query_text,
            response=response,
            context_chunks=result["context"].get(
                "context_chunks", [str(result["context"])]
            ),
            metadata={"provider": provider.get_capabilities()["name"]},
        )

        # Extract source links from context if available
        source_links = result.get("context", {}).get("source_links", [])
        if isinstance(result.get("context"), dict):
            if "config" in result["context"]:
                # For SDWAN provider, use the config context
                context_text = str(result["context"]["config"])
            elif "context_chunks" in result["context"]:
                # For Knowledge Base provider, use the context chunks
                context_text = "\n".join(result["context"]["context_chunks"])
            else:
                context_text = str(result["context"])
        else:
            context_text = str(result["context"])

        return LLMResponse(
            answer=response,
            sources=[],  # No document sources for API data
            context_chunks=[context_text],
            conversation_id=conversation_id,
            provider=provider.get_capabilities()["name"],
            source_links=source_links,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")


@app.post("/ingest/excel/")
async def ingest_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Ingest an Excel file, process its contents, and store embeddings.
    """
    try:
        # Read Excel file
        df = pd.read_excel(file.file)

        # Convert DataFrame to text, concatenating all non-null values
        text_content = " ".join(
            df.astype(str)
            .apply(lambda x: " ".join(x.dropna().astype(str)), axis=1)
            .tolist()
        )

        # Create document and get nodes
        doc = Document(text=text_content)
        nodes = vectorizer.parser.get_nodes_from_documents([doc])

        # Get embeddings for each node
        embeddings = []
        for node in nodes:
            vector = vectorizer.embed_model.get_text_embedding(node.text)

            embedding = E5Embedding(
                text=node.text,
                vector=vector,
                source_document=file.filename,
                metadata={"source_type": "excel", "filename": file.filename},
            )
            embeddings.append(embedding)

        # Bulk insert embeddings
        db.bulk_save_objects(embeddings)
        db.commit()

        return {
            "message": f"Successfully processed Excel file and stored {len(embeddings)} embeddings"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Error processing Excel file: {str(e)}"
        )


@app.get("/admin/table-counts")
def get_table_counts(db: Session = Depends(get_db)):
    """Get count of records in all tables."""
    try:
        counts = [{"table": "embeddings", "count": db.query(E5Embedding).count()}]
        return {"table_counts": counts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.delete("/admin/embeddings")
def delete_embeddings(db: Session = Depends(get_db)):
    """Delete all records from embeddings tables."""
    try:
        db.query(E5Embedding).delete()
        db.commit()
        return {"message": "Successfully deleted all embedding records"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/conversations/{conversation_id}", response_model=ConversationHistory)
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """Get the full history of a conversation."""
    try:
        memory = ConversationMemory(db)
        turns = memory.get_recent_history(
            conversation_id, window_size=100
        )  # Get up to 100 turns
        return ConversationHistory(turns=turns, total_turns=len(turns))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error retrieving conversation history: {str(e)}"
        )


@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete a conversation and all its turns."""
    try:
        db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).delete()
        db.commit()
        return {"message": f"Successfully deleted conversation {conversation_id}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Error deleting conversation: {str(e)}"
        )


@app.delete("/conversations")
def delete_all_conversations(db: Session = Depends(get_db)):
    """Delete all conversations and their turns."""
    try:
        db.query(Conversation).delete()
        db.commit()
        return {"message": "Successfully deleted all conversations"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, detail=f"Error deleting all conversations: {str(e)}"
        )


@app.get("/conversations", response_model=ConversationListResponse)
def list_conversations(db: Session = Depends(get_db)):
    """List all conversations with their latest interaction."""
    try:
        # Get the latest turn for each conversation
        latest_turns = (
            db.query(Conversation)
            .distinct(Conversation.conversation_id)
            .order_by(Conversation.conversation_id, Conversation.timestamp.desc())
            .all()
        )

        return ConversationListResponse(
            conversations=[
                {
                    "id": turn.conversation_id,
                    "last_query": turn.query,
                    "last_response": turn.response,
                    "timestamp": turn.timestamp,
                }
                for turn in latest_turns
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error listing conversations: {str(e)}"
        )


@app.get("/workflows/capabilities")
async def get_workflow_capabilities():
    """Get available workflow capabilities"""
    return await workflow_manager.get_capabilities()
