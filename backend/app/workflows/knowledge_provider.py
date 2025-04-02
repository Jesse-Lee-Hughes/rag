from typing import Dict, Any, List, Optional
from .base import WorkflowProvider
from ..database import E5Embedding
from ..utils import LlamaVectorizer
from llama_index.core import Document
from sqlalchemy.orm import Session
from ..schemas import SourceLink
from ..memory import ConversationMemory


class KnowledgeBaseWorkflowProvider(WorkflowProvider):
    """Provider for knowledge base document queries with LLM fallback"""

    def __init__(self, db: Session, vectorizer: LlamaVectorizer):
        self.db = db
        self.vectorizer = vectorizer
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
        """This provider can handle any query, either with vector search or LLM fallback"""
        return True

    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get context from knowledge base documents"""
        doc = Document(text=query)
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

        # Filter results by relevance threshold
        relevant_results = [
            result for result in results if float(result.similarity) > 0.8
        ]

        if not relevant_results:
            return {
                "context_chunks": [],
                "source_links": [],
                "metadata": {
                    "provider": "Knowledge Base",
                    "reason": "No high relevance documents found",
                    "fallback": True,
                },
            }

        # Extract context and source links from vector search results
        context_chunks = []
        source_links = []
        for result, similarity in relevant_results:
            context_chunks.append(result.text)
            source_links.append(
                SourceLink(
                    provider="Knowledge Base",
                    link=result.source_document,
                    metadata={
                        "text": result.text[:100] + "...",
                        "relevance": float(similarity),
                    },
                )
            )

        return {
            "context_chunks": context_chunks,
            "source_links": source_links,
            "metadata": {
                "provider": "Knowledge Base",
                "relevance_threshold": 0.8,
                "num_results": len(relevant_results),
                "fallback": False,
            },
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get knowledge base provider capabilities"""
        return {
            "name": "Knowledge Base Provider",
            "description": "Provider for knowledge base document queries with LLM fallback",
            "capabilities": [
                "Vector-based document search",
                "High relevance matching (>80%)",
                "Source document linking",
                "Context chunking",
                "LLM fallback for unmatched queries",
            ],
            "limitations": [
                "Requires document ingestion",
                "Limited to ingested content",
                "High relevance threshold",
            ],
        }

    async def handle_query(
        self,
        query: str,
        memory: Optional[ConversationMemory] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle the query with optional memory support and fallback handling"""
        context = await self.get_context(query)

        # Get conversation history if memory is available
        history_text = ""
        if memory and conversation_id:
            history = memory.get_recent_history(conversation_id)
            history_text = memory.format_memory_for_prompt(history)

        # Build the system prompt based on provider capabilities and context
        capabilities = self.get_capabilities()
        prompt = f"""You are a specialized assistant for {capabilities['name']}.
        Analyze the provided context to answer questions about {', '.join(capabilities['capabilities'])}.
        Be specific and reference actual configuration details.

        Provider Limitations:
        {', '.join(capabilities['limitations'])}

        Previous conversation:
        {history_text}"""

        # Add fallback handling if no relevant documents found
        if context.get("metadata", {}).get("fallback", False):
            prompt += """
            No relevant documents were found in the knowledge base.
            Please provide a helpful response based on your general knowledge.
            When answering:
            1. Be clear and concise
            2. Provide relevant historical context when appropriate
            3. If you're not certain about something, acknowledge the uncertainty
            4. Focus on factual information rather than speculation"""

        return {"context": context, "prompt": prompt, "history": history_text}
