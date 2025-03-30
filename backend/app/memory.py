from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import Conversation
from app.schemas import ConversationTurn


class ConversationMemory:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        return str(uuid.uuid4())

    def add_interaction(
        self,
        conversation_id: str,
        query: str,
        response: str,
        context_chunks: Optional[List[str]] = None,
        similarity_scores: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConversationTurn:
        """Add a new interaction to the conversation"""
        timestamp = datetime.utcnow().isoformat()

        conversation = Conversation(
            conversation_id=conversation_id,
            query=query,
            response=response,
            context_chunks=context_chunks,
            similarity_scores=similarity_scores,
            timestamp=timestamp,
            metadata=metadata,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return ConversationTurn(
            query=conversation.query,
            response=conversation.response,
            context_chunks=conversation.context_chunks,
            similarity_scores=conversation.similarity_scores,
            timestamp=conversation.timestamp,
            conversation_id=conversation.conversation_id,
            metadata=conversation.get_metadata(),
        )

    def get_recent_history(
        self, conversation_id: str, window_size: int = 5
    ) -> List[ConversationTurn]:
        """Get recent conversation history"""
        turns = (
            self.db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .order_by(Conversation.timestamp.desc())
            .limit(window_size)
            .all()
        )

        return [
            ConversationTurn(
                query=turn.query,
                response=turn.response,
                context_chunks=turn.context_chunks,
                similarity_scores=turn.similarity_scores,
                timestamp=turn.timestamp,
                conversation_id=turn.conversation_id,
                metadata=turn.get_metadata(),
            )
            for turn in reversed(turns)
        ]

    def format_memory_for_prompt(self, history: List[ConversationTurn]) -> str:
        """Format conversation history for LLM prompt"""
        if not history:
            return ""

        formatted_history = []
        for turn in history:
            formatted_history.append(f"User: {turn.query}")
            formatted_history.append(f"Assistant: {turn.response}")
            formatted_history.append("---")  # Add separator between turns

        return "\n".join(formatted_history)

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete all turns of a conversation"""
        self.db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).delete()
        self.db.commit()
