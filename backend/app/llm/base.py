from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a response based on the query and context.

        Args:
            query: The user's question
            context: List of relevant text chunks from the vector store
            system_prompt: Optional system prompt to guide the model's behavior
            temperature: Controls randomness in the output (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            str: The generated response
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM provider is healthy and accessible.

        Returns:
            bool: True if the provider is healthy, False otherwise
        """
        pass
