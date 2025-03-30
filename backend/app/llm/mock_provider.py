from typing import List
from .base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for development and testing"""

    async def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Generate a mock response based on the query type"""
        if context and any("organization" in str(c) for c in context):
            return (
                "Based on the network configuration data:\n\n"
                "Organization: Big Data Org (UID: 1234)\n"
                "Total Devices: 5\n"
                "Active Devices: 4\n"
                "VLANs: Data (VLAN 100), Voice (VLAN 200)\n"
                "IP Scheme: 10.x.0.0/24 for each branch"
            )
        else:
            return (
                "I've analyzed the available documents and found:\n\n"
                "This is a mock response for testing purposes.\n"
                f"Query: {query}\n"
                f"Context length: {len(context)} chunks"
            )

    async def health_check(self) -> bool:
        """Mock health check always returns True"""
        return True
