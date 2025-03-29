import os
from typing import List
from openai import AsyncOpenAI
from .base import LLMProvider


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI implementation of the LLM provider."""

    def __init__(self, model: str = "gpt-35-turbo"):
        """
        Initialize the Azure OpenAI provider.

        Args:
            model: The Azure OpenAI model to use (e.g., "gpt-35-turbo", "gpt-4")
        """
        # Load configuration
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        deployment_name = os.getenv("AZURE_OPENAI_MODEL", model)  # Ensure correct deployment name

        if not all([api_key, endpoint, deployment_name]):
            raise ValueError("Missing required Azure OpenAI environment variables.")

        # Construct base URL for the specific deployment
        base_url = f"{endpoint}/openai/deployments/{deployment_name}"

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_query={"api-version": api_version},  # Corrected from default_headers
        )

        self.model = deployment_name  # Ensure model matches deployment name

    async def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a response using Azure OpenAI's API.

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

        messages.append({"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating response from Azure OpenAI: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if the Azure OpenAI API is accessible.

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
