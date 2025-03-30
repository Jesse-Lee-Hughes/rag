from typing import Dict, Any, List
from .base import WorkflowProvider
from ..services.sdwan import SDWANService
from ..schemas import SourceLink


class SDWANWorkflowProvider(WorkflowProvider):
    """Provider for SD-WAN related queries"""

    def __init__(self):
        self.sdwan_service = SDWANService()
        self.keywords = [
            "sdwan",
            "network",
            "vlan",
            "device",
            "interface",
            "organization",
            "config",
            "status",
            "ip",
            "address",
        ]

    async def can_handle(self, query: str) -> bool:
        """Check if query is related to SD-WAN"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)

    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get SD-WAN configuration context"""
        config = await self.sdwan_service.get_organization_config()

        # Create source links for each device
        source_links = []
        for device in config.get("organization", {}).get("devices", []):
            source_links.append(
                SourceLink(
                    provider="SDWAN",
                    link=f"/network/devices/{device['name']}",
                    metadata={
                        "device_name": device["name"],
                        "model": device["model"],
                        "status": device["status"],
                    },
                )
            )

        return {"config": config, "source_links": source_links}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get SD-WAN provider capabilities"""
        return {
            "name": "SD-WAN Provider",
            "description": "Handles queries about network configuration and status",
            "capabilities": [
                "Network device status",
                "VLAN configuration",
                "IP addressing",
                "Interface status",
                "Organization details",
            ],
            "limitations": [
                "Cannot modify configurations",
                "Read-only access",
                "Limited to organization scope",
            ],
        }
