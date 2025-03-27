import numpy as np
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils import LlamaVectorizer
from app.database import engine, Base, get_db, E5Embedding
from app.schemas import EmbeddingResponse, VectorSearchRequest, EmbeddingListResponse, TextSearchRequest
from llama_index.core import Document
import os
from sqlalchemy import text


# Initialize FastAPI app
app = FastAPI(title="RAG Vector Search API")

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize LlamaVectorizer once at startup
vectorizer = LlamaVectorizer()

@app.post("/ingest/pdf", response_model=EmbeddingListResponse)
def upload_pdf_and_store_embeddings(
        url: str, db: Session = Depends(get_db)
):
    try:
        # Use the global vectorizer
        text_content = vectorizer.convert_pdf_to_text(url)
        results = vectorizer.process_document(text_content, db)

        formatted_results = [
            EmbeddingResponse(
                id=result.id,
                text=result.text,
                vector=result.vector,
                metadata=result.get_metadata()
            )
            for result in results
        ]

        return EmbeddingListResponse(embeddings=formatted_results)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")


# Search endpoint remains the same
@app.post("/search/", response_model=EmbeddingListResponse)
def vector_search(
        search_request: VectorSearchRequest,
        db: Session = Depends(get_db)
):
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
            metadata=result.get_metadata()
        )
        for result in results
    ]

    return EmbeddingListResponse(embeddings=formatted_results)

@app.post("/search/text/", response_model=EmbeddingListResponse)
def text_search(
        search_request: TextSearchRequest,
        db: Session = Depends(get_db)
):
    try:
        # Use the global vectorizer
        doc = Document(text=search_request.query_text)
        nodes = vectorizer.parser.get_nodes_from_documents([doc])
        query_vector = vectorizer.embed_model.get_text_embedding(nodes[0].text)

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
                metadata=result.get_metadata()
            )
            for result in results
        ]

        return EmbeddingListResponse(embeddings=formatted_results)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")

@app.get("/admin/table-counts")
def get_table_counts(db: Session = Depends(get_db)):
    """Get count of records in all tables."""
    try:
        counts = [
            {
                "table": "embeddings",
                "count": db.query(E5Embedding).count()
            }
        ]
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
