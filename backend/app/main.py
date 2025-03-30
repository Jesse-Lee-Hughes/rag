import numpy as np
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.utils import LlamaVectorizer
from app.database import engine, Base, get_db, E5Embedding, Conversation
from app.schemas import (
    EmbeddingResponse,
    VectorSearchRequest,
    EmbeddingListResponse,
    TextSearchRequest,
    LLMResponse,
    ConversationHistory,
    ConversationListResponse,
    NetworkResponse,
    NetworkQueryRequest,
    SourceLink,
)
from llama_index.core import Document
import os
from sqlalchemy import text
import tempfile
from app.llm.factory import LLMFactory
from app.memory import ConversationMemory
from datetime import datetime
from app.services.sdwan import SDWANService
from app.workflows.manager import WorkflowManager
from app.workflows.sdwan_provider import SDWANWorkflowProvider
from app.workflows.knowledge_provider import KnowledgeBaseWorkflowProvider


# Initialize FastAPI app
app = FastAPI(title="RAG Vector Search API")

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize LlamaVectorizer once at startup
vectorizer = LlamaVectorizer()

# Initialize LLM provider
llm_provider = LLMFactory.create_provider("azure")
sdwan_service = SDWANService(base_url="http://mock_sdwan:8080")

# Initialize workflow manager
workflow_manager = WorkflowManager()
workflow_manager.register_provider(SDWANWorkflowProvider())
workflow_manager.register_provider(
    KnowledgeBaseWorkflowProvider(next(get_db()), vectorizer)
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


# Search endpoint remains the same
@app.post("/search/", response_model=EmbeddingListResponse)
def vector_search(search_request: VectorSearchRequest, db: Session = Depends(get_db)):
    query_vector = np.array(search_request.query_vector)

    results = (
        db.query(E5Embedding)
        .order_by(E5Embedding.vector.cosine_distance(query_vector))
        .limit(search_request.top_k)
        .all()
    )

    formatted_results = [
        EmbeddingResponse(
            id=result.id,
            text=result.text,
            vector=result.vector,
            metadata=result.get_metadata(),
        )
        for result in results
    ]

    return EmbeddingListResponse(embeddings=formatted_results)


@app.post("/search/text/", response_model=LLMResponse)
async def text_search(search_request: TextSearchRequest, db: Session = Depends(get_db)):
    """Handle text queries with workflow routing"""
    try:
        # Initialize memory manager first
        memory = ConversationMemory(db)
        conversation_id = search_request.conversation_id or memory.create_conversation()

        # Check for workflow provider
        provider = await workflow_manager.get_provider(search_request.query_text)

        if provider:
            # Handle query with memory support
            result = await provider.handle_query(
                search_request.query_text,
                memory=memory,
                conversation_id=conversation_id,
            )

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
                context_chunks=[str(result["context"])],
                metadata={"provider": provider.get_capabilities()["name"]},
            )

            # Extract source links from context if available
            source_links = result.get("context", {}).get("source_links", [])
            if (
                isinstance(result.get("context"), dict)
                and "config" in result["context"]
            ):
                # For SDWAN provider, use the config context
                context_text = str(result["context"]["config"])
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

        # Fall back to RAG for document-based queries
        # Get relevant documents using vector search
        doc = Document(text=search_request.query_text.lower())
        nodes = vectorizer.parser.get_nodes_from_documents([doc])
        query_vector = vectorizer.embed_model.get_text_embedding(nodes[0].text)

        # Add cosine similarity score to the query
        results = (
            db.query(
                E5Embedding,
                # Calculate cosine similarity (1 - distance)
                (1 - E5Embedding.vector.cosine_distance(query_vector)).label(
                    "similarity"
                ),
            )
            .order_by(E5Embedding.vector.cosine_distance(query_vector))
            .limit(search_request.top_k)
            .all()
        )

        # Format results and filter by similarity
        formatted_results = []
        source_links = []
        for result in results:
            if float(result.similarity) > 0.8:
                formatted_results.append(
                    EmbeddingResponse(
                        id=result.E5Embedding.id,
                        text=result.E5Embedding.text,
                        vector=result.E5Embedding.vector,
                        source_document=result.E5Embedding.source_document,
                        metadata={
                            **(result.E5Embedding.get_metadata() or {}),
                            "similarity_score": float(result.similarity),
                        },
                    )
                )

                # Create source link for each document
                source_links.append(
                    SourceLink(
                        provider="Knowledge Base",
                        link=result.E5Embedding.source_document,
                        metadata={
                            "similarity": float(result.similarity),
                            "document_type": (
                                result.E5Embedding.get_metadata().get("type", "unknown")
                                if result.E5Embedding.get_metadata()
                                else "unknown"
                            ),
                        },
                    )
                )

        # Extract text and similarity scores from results for LLM context
        context = [result.text for result in formatted_results]
        similarity_scores = [
            float(result.metadata["similarity_score"]) for result in formatted_results
        ]

        # Get conversation history
        history = memory.get_recent_history(
            conversation_id, window_size=search_request.memory_window
        )
        history_text = memory.format_memory_for_prompt(history)

        # Prepare system prompt with context and history
        if context:
            prompt = f"""You are a helpful assistant called Mook that answers questions based on the provided context and conversation history.
            Use the context to provide accurate, specific answers. If the context doesn't contain enough information 
            to fully answer the question, acknowledge what you know from the context and indicate what's missing.
            
            Previous conversation:
            {history_text}
            
            Current context:
            {' '.join(context)}"""
        else:
            prompt = f"""You are a helpful assistant called Mook. Since no relevant context was found in the knowledge base 
            (similarity < 80%), I'll answer based on my general knowledge and conversation history.
            
            Previous conversation:
            {history_text}
            
            I'll explicitly acknowledge this and provide the best information I can, while being clear about the source of my information."""

        # Generate response using LLM
        response = await llm_provider.generate_response(
            query=search_request.query_text,
            context=context,
            system_prompt=prompt,
            temperature=0.7,
        )

        # Store the interaction in memory
        memory.add_interaction(
            conversation_id=conversation_id,
            query=search_request.query_text,
            response=response,
            context_chunks=context,
            similarity_scores=similarity_scores,
            metadata={"timestamp": datetime.utcnow().isoformat()},
        )

        return LLMResponse(
            answer=response,
            sources=formatted_results,
            context_chunks=context,
            conversation_id=conversation_id,
            provider="Knowledge Base",
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


@app.post("/network/query", response_model=NetworkResponse)
async def network_query(request: NetworkQueryRequest, db: Session = Depends(get_db)):
    """Network configuration specific queries"""
    try:
        config = await sdwan_service.get_organization_config()

        prompt = """You are a network configuration assistant. Analyze the provided 
        network state and configuration to answer questions about VLANs, IP addressing,
        and device status. Be specific and reference actual configuration details."""

        response = await llm_provider.generate_response(
            query=request.query,
            context=[str(config)],
            system_prompt=prompt,
            temperature=0.5,
        )

        return NetworkResponse(
            answer=response,
            config_snapshot=config if request.include_config else None,
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error processing network query: {str(e)}"
        )


@app.get("/workflows/capabilities")
async def get_workflow_capabilities():
    """Get available workflow capabilities"""
    return await workflow_manager.get_capabilities()
