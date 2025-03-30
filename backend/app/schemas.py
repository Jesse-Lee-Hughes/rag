from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np


class EmbeddingCreate(BaseModel):
    text: str
    vector: List[float]
    metadata: Optional[dict] = None


class EmbeddingResponse(BaseModel):
    id: int
    text: str
    vector: List[float]
    source_document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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
    conversation_id: Optional[str] = None
    memory_window: int = 5  # Number of previous turns to include in context


class SourceLink(BaseModel):
    provider: str
    link: str
    metadata: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    answer: str
    sources: List[EmbeddingResponse]
    context_chunks: List[str]
    conversation_id: Optional[str] = None
    provider: Optional[str] = None
    source_links: Optional[List[SourceLink]] = None


class ConversationTurn(BaseModel):
    query: str
    response: str
    context_chunks: Optional[List[str]] = None
    similarity_scores: Optional[List[float]] = None
    timestamp: str
    conversation_id: str
    metadata: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    turns: List[ConversationTurn]
    total_turns: int


class ConversationListItem(BaseModel):
    id: str
    last_query: str
    last_response: str
    timestamp: str


class ConversationListResponse(BaseModel):
    conversations: List[ConversationListItem]


class NetworkQueryRequest(BaseModel):
    query: str
    org_id: Optional[str] = None
    include_config: bool = False


class NetworkResponse(BaseModel):
    answer: str
    config_snapshot: Optional[Dict[str, Any]] = None
    timestamp: str
