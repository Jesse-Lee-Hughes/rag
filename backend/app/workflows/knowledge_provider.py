from typing import Dict, Any, List
from .base import WorkflowProvider
from ..database import E5Embedding
from ..utils import LlamaVectorizer
from llama_index.core import Document
from sqlalchemy.orm import Session
from ..schemas import SourceLink


class KnowledgeBaseWorkflowProvider(WorkflowProvider):
    """Provider for knowledge base document queries"""

    def __init__(self, db: Session, vectorizer: LlamaVectorizer):
        self.db = db
        self.vectorizer = LlamaVectorizer()
        self.keywords = [
            "document",
            "knowledge",
            "search",
            "find",
            "look up",
            "information",
            "content",
            "text",
            "file",
            "pdf",
        ]

    async def can_handle(self, query: str) -> bool:
        """Check if query is related to knowledge base search"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)

    async def get_context(self) -> Dict[str, Any]:
        """Get relevant documents from vector store"""
        # Create document from query
        doc = Document(text=query.lower())
        nodes = self.vectorizer.parser.get_nodes_from_documents([doc])
        query_vector = self.vectorizer.embed_model.get_text_embedding(nodes[0].text)

        # Search vector store
        results = (
            self.db.query(
                E5Embedding,
                (1 - E5Embedding.vector.cosine_distance(query_vector)).label(
                    "similarity"
                ),
            )
            .order_by(E5Embedding.vector.cosine_distance(query_vector))
            .limit(5)
            .all()
        )

        # Format results and create source links
        formatted_results = []
        source_links = []
        for result in results:
            if float(result.similarity) > 0.8:
                formatted_results.append(
                    {
                        "text": result.E5Embedding.text,
                        "source": result.E5Embedding.source_document,
                        "similarity": float(result.similarity),
                        "metadata": result.E5Embedding.get_metadata() or {},
                    }
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

        return {
            "documents": formatted_results,
            "query": query,
            "total_results": len(formatted_results),
            "source_links": source_links,
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get knowledge base provider capabilities"""
        return {
            "name": "Knowledge Base Provider",
            "description": "Handles queries about documents and knowledge base content",
            "capabilities": [
                "Document search",
                "Content retrieval",
                "Similarity-based search",
                "Metadata filtering",
                "Source tracking",
            ],
            "limitations": [
                "Requires pre-indexed documents",
                "Limited to text content",
                "Similarity threshold > 0.8",
                "Maximum 5 results per query",
            ],
        }
