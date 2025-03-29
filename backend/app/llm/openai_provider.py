import os
from typing import List
from openai import AsyncOpenAI
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of the LLM provider."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI provider.

        Args:
            model: The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4")
        """
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    async def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a response using OpenAI's API.

        Args:
            query: The user's question
            context: List of relevant text chunks from the vector store
            system_prompt: Optional system prompt to guide the model's behavior
            temperature: Controls randomness in the output (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            str: The generated response
        """
        # Combine context into a single string
        context_text = "\n\n".join(context)

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add context and query
        messages.extend(
            [
                {
                    "role": "user",
                    "content": f"Context:\n{context_text}\n\nQuestion: {query}",
                }
            ]
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response from OpenAI: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if the OpenAI API is accessible.

        Returns:
            bool: True if the API is accessible, False otherwise
        """
        try:
            # Try a simple completion to check API access
            await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return True
        except Exception:
            return False
