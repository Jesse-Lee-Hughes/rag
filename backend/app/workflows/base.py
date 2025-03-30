from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.memory import ConversationMemory


class WorkflowProvider(ABC):
    """Base class for workflow providers"""

    @abstractmethod
    async def can_handle(self, query: str) -> bool:
        """Determine if this provider can handle the query"""
        pass

    @abstractmethod
    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context for the query"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities and limitations"""
        pass

    async def handle_query(
        self,
        query: str,
        memory: Optional[ConversationMemory] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle the query with optional memory support"""
        context = await self.get_context(query)

        # Get conversation history if memory is available
        history_text = ""
        if memory and conversation_id:
            history = memory.get_recent_history(conversation_id)
            history_text = memory.format_memory_for_prompt(history)

        # Use provider-specific prompt
        prompt = f"""You are a specialized assistant for {self.get_capabilities()['name']}.
        Analyze the provided context to answer questions about {', '.join(self.get_capabilities()['capabilities'])}.
        Be specific and reference actual configuration details.
        
        Previous conversation:
        {history_text}"""

        return {"context": context, "prompt": prompt, "history": history_text}
