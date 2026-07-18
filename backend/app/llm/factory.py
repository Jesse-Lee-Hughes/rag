import os
from typing import Any, Dict, Type

from .azure_provider import AzureOpenAIProvider
from .base import LLMProvider
from .claude_provider import ClaudeProvider
from .mock_provider import MockLLMProvider
from .openai_provider import OpenAIProvider


class LLMFactory:
    """Factory class for creating LLM providers."""

    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "azure": AzureOpenAIProvider,
        "claude": ClaudeProvider,
        # Add more providers here as they are implemented
    }

    @classmethod
    def create_provider(cls, provider_type: str = "claude", **kwargs) -> LLMProvider:
        """
        Create an instance of the specified LLM provider.

        Providers that need credentials (azure, claude) fall back to the mock
        provider if those credentials are missing, so the app always starts.

        Args:
            provider_type: Type of the provider to create
                ("openai", "azure", "claude", or "mock")
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            LLMProvider: An instance of the specified provider

        Raises:
            ValueError: If the provider is not found
        """
        if provider_type == "mock":
            return MockLLMProvider()

        if provider_type in ("azure", "claude"):
            provider_class = cls._providers[provider_type]
            try:
                return provider_class(**kwargs)
            except ValueError:
                print(
                    f"Warning: {provider_type} provider unavailable "
                    "(missing credentials/CLI), using mock provider"
                )
                return MockLLMProvider()

        if provider_type == "openai":
            return OpenAIProvider(**kwargs)

        raise ValueError(f"Unknown provider type: {provider_type}")

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """
        Register a new LLM provider.

        Args:
            name: Name of the provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class
