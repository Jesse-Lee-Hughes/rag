from typing import List, Dict, Any, Optional
from .base import WorkflowProvider
from .knowledge_provider import KnowledgeBaseWorkflowProvider


class WorkflowManager:
    """Manages different workflow providers"""

    def __init__(self):
        self.providers: List[WorkflowProvider] = []
        self.fallback_provider: Optional[WorkflowProvider] = None

    def register_provider(self, provider: WorkflowProvider, is_fallback: bool = False):
        """Register a workflow provider"""
        if is_fallback:
            self.fallback_provider = provider
        else:
            self.providers.append(provider)

    async def get_provider(self, query: str) -> WorkflowProvider:
        """Get the appropriate provider for the query"""
        if not self.providers and not self.fallback_provider:
            raise ValueError("No providers registered")

        # First try the KnowledgeBase provider if it exists
        knowledge_provider = next(
            (p for p in self.providers if isinstance(p, KnowledgeBaseWorkflowProvider)),
            None,
        )
        if knowledge_provider:
            # Check if KnowledgeBase can handle with high relevance
            if await knowledge_provider.can_handle(query):
                return knowledge_provider

        # Then try other providers
        for provider in self.providers:
            if not isinstance(provider, KnowledgeBaseWorkflowProvider):
                if await provider.can_handle(query):
                    return provider

        # If no provider matches, use fallback
        if self.fallback_provider:
            return self.fallback_provider

        raise ValueError("No provider available for query")

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all providers"""
        capabilities = []
        for provider in self.providers:
            capabilities.append(provider.get_capabilities())
        if self.fallback_provider:
            capabilities.append(self.fallback_provider.get_capabilities())
        return {"providers": capabilities}

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
