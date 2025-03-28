import numpy as np
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.utils import LlamaVectorizer
from app.database import engine, Base, get_db, E5Embedding
from app.schemas import EmbeddingResponse, VectorSearchRequest, EmbeddingListResponse, TextSearchRequest
from llama_index.core import Document
import os
from sqlalchemy import text
import tempfile


# Initialize FastAPI app
app = FastAPI(title="RAG Vector Search API")

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize LlamaVectorizer once at startup
vectorizer = LlamaVectorizer()

@app.post("/ingest/pdf_url", response_model=EmbeddingListResponse)
def upload_pdf_and_store_embeddings(
        url: str, db: Session = Depends(get_db)
):
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
                metadata=result.get_metadata() or {}
            )
            for result in results
        ]

        return EmbeddingListResponse(embeddings=formatted_results)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")

@app.post("/ingest/file", response_model=EmbeddingListResponse)
async def upload_file_and_store_embeddings(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Verify file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Create temporary file to store upload
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        try:
            # Process the PDF file
            text_content = vectorizer.convert_pdf_to_text(tmp_path)
            # Use filename as source document identifier
            results = vectorizer.process_document(text_content, db, source_document=file.filename)

            formatted_results = [
                EmbeddingResponse(
                    id=result.id,
                    text=result.text,
                    vector=result.vector,
                    source_document=result.source_document,
                    metadata=result.get_metadata() or {}
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
        doc = Document(text=search_request.query_text.lower())
        nodes = vectorizer.parser.get_nodes_from_documents([doc])
        query_vector = vectorizer.embed_model.get_text_embedding(nodes[0].text)

        # Add cosine similarity score to the query
        results = (
            db.query(
                E5Embedding,
                # Calculate cosine similarity (1 - distance)
                (1 - E5Embedding.vector.cosine_distance(query_vector)).label('similarity')
            )
            .order_by(E5Embedding.vector.cosine_distance(query_vector))
            .limit(search_request.top_k)
            .all()
        )

        formatted_results = [
            EmbeddingResponse(
                id=result.E5Embedding.id,
                text=result.E5Embedding.text,
                vector=result.E5Embedding.vector,
                source_document=result.E5Embedding.source_document,
                metadata={
                    **(result.E5Embedding.get_metadata() or {}),
                    "similarity_score": float(result.similarity)  # Add similarity score to metadata
                }
            )
            for result in results
            if float(result.similarity) > 0.5  # Only include results with >50% similarity
        ]

        return EmbeddingListResponse(embeddings=formatted_results)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")
    
    
@app.post("/ingest/excel/")
async def ingest_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
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
                metadata={
                    "source_type": "excel",
                    "filename": file.filename
                }
            )
            embeddings.append(embedding)

        # Bulk insert embeddings
        db.bulk_save_objects(embeddings)
        db.commit()

        return {"message": f"Successfully processed Excel file and stored {len(embeddings)} embeddings"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")


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
