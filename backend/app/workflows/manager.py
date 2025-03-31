from typing import List, Dict, Any, Optional
from .base import WorkflowProvider


class WorkflowManager:
    """Manages different workflow providers"""

    def __init__(self):
        self.providers: List[WorkflowProvider] = []

    def register_provider(self, provider: WorkflowProvider):
        """Register a new workflow provider"""
        self.providers.append(provider)

    async def get_provider(self, query: str) -> Optional[WorkflowProvider]:
        """Get appropriate provider for the query"""
        for provider in self.providers:
            if await provider.can_handle(query):
                return provider
        return None

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all registered providers"""
        return {
            "providers": [provider.get_capabilities() for provider in self.providers]
        }

    async def get_provider_with_context(self, query: str) -> Optional[WorkflowProvider]:
        # Add provider context awareness
        provider_capabilities = {
            provider.get_capabilities()["name"]: {
                "description": provider.get_capabilities()["description"],
                "capabilities": provider.get_capabilities()["capabilities"],
                "keywords": provider.keywords,
            }
            for provider in self.providers
        }

        # Let the LLM evaluate the query with full provider context
        # This would be part of the system prompt for the LLM
        provider_context = f"""
        Available providers and their capabilities:
        {provider_capabilities}
        
        Query type evaluation rules:
        1. For queries about current state/configuration, use the relevant system provider
        2. For queries about making changes/requests, use ServiceNow provider
        3. For queries about documentation/best practices, use Knowledge Base provider
        4. For complex queries requiring multiple contexts, prioritize the action provider
           (e.g., for 'create change based on current config', use ServiceNow)
        """

        # The LLM would then evaluate the query with this context
        # and return the most appropriate provider
        return await self._evaluate_provider_for_query(query, provider_context)

    async def _evaluate_provider_for_query(
        self, query: str, provider_context: str
    ) -> Optional[WorkflowProvider]:
        # Implementation of _evaluate_provider_for_query method
        # This method should return the most appropriate provider based on the query and provider_context
        # This is a placeholder and should be implemented based on your specific requirements
        return None
