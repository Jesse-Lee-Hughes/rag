from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class EmbeddingCreate(BaseModel):
    text: str
    vector: List[float]
    metadata: Optional[dict] = None

class EmbeddingResponse(BaseModel):
    id: int
    text: str
    vector: List[float]
    metadata: Optional[Dict[str, Any]] = None
    source_document: Optional[str] = None

class EmbeddingListResponse(BaseModel):
    embeddings: List[EmbeddingResponse]

class VectorSearchRequest(BaseModel):
    query_vector: List[float]
    top_k: int = 5

class DocumentConversionRequest(BaseModel):
    document: str


class TextSearchRequest(BaseModel):
    query_text: str
    top_k: int = 5