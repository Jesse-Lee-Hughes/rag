from typing import Dict, Type
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .azure_provider import AzureOpenAIProvider


class LLMFactory:
    """Factory class for creating LLM providers."""

    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "azure": AzureOpenAIProvider,
        # Add more providers here as they are implemented
    }

    @classmethod
    def create_provider(cls, provider_name: str, **kwargs) -> LLMProvider:
        """
        Create an instance of the specified LLM provider.

        Args:
            provider_name: Name of the provider to create (e.g., "openai", "azure")
            **kwargs: Additional arguments to pass to the provider's constructor

        Returns:
            LLMProvider: An instance of the specified provider

        Raises:
            ValueError: If the provider is not found
        """
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(
                f"Provider '{provider_name}' not found. Available providers: {list(cls._providers.keys())}"
            )

        return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """
        Register a new LLM provider.

        Args:
            name: Name of the provider
            provider_class: The provider class to register
        """
        cls._providers[name.lower()] = provider_class
