from typing import Dict, Type, Any
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .azure_provider import AzureOpenAIProvider
from .mock_provider import MockLLMProvider
import os


class LLMFactory:
    """Factory class for creating LLM providers."""

    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "azure": AzureOpenAIProvider,
        # Add more providers here as they are implemented
    }

    @classmethod
    def create_provider(cls, provider_type: str = "azure", **kwargs) -> LLMProvider:
        """
        Create an instance of the specified LLM provider.

        Args:
            provider_type: Type of the provider to create (e.g., "openai", "azure", "mock")
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            LLMProvider: An instance of the specified provider

        Raises:
            ValueError: If the provider is not found
        """
        if provider_type == "azure":
            try:
                return AzureOpenAIProvider(**kwargs)
            except ValueError as e:
                print(
                    "Warning: Azure OpenAI credentials not found, using mock provider"
                )
                return MockLLMProvider()
        elif provider_type == "mock":
            return MockLLMProvider()
        else:
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
