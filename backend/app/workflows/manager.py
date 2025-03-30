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
