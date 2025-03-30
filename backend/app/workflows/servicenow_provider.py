from typing import Dict, Any, List
from .base import WorkflowProvider
from ..services.servicenow import ServiceNowService
from ..schemas import SourceLink


class ServiceNowWorkflowProvider(WorkflowProvider):
    """Provider for ServiceNow change management queries"""

    def __init__(self):
        self.servicenow_service = ServiceNowService()
        self.keywords = [
            "change",
            "change request",
            "servicenow",
            "change management",
            "change control",
            "change ticket",
            "change window",
            "change schedule",
            "change approval",
            "change risk",
        ]

    async def can_handle(self, query: str) -> bool:
        """Check if query is related to change management"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)

    async def get_context(self, query: str) -> Dict[str, Any]:
        """Get change management context"""
        # Get changes from ServiceNow
        changes = await self.servicenow_service.get_changes(query=query)

        # Format context chunks from changes
        context_chunks = []
        for change in changes.get("result", []):
            change_context = f"Change Request: {change['number']}\n"
            change_context += f"Description: {change['short_description']}\n"
            change_context += f"State: {change['state']}\n"
            change_context += f"Priority: {change['priority']}\n"
            change_context += f"Risk: {change['risk']}\n"
            change_context += f"Impact: {change['impact']}\n"
            change_context += f"Assigned to: {change['assigned_to']}\n"
            change_context += f"Requested by: {change['requested_by']}\n"
            change_context += f"Start: {change['start_date']}\n"
            change_context += f"End: {change['end_date']}\n"
            if change.get("description"):
                change_context += f"Detailed Description:\n{change['description']}\n"
            context_chunks.append(change_context)

        # Create source links for each change
        source_links = []
        for change in changes.get("result", []):
            source_links.append(
                SourceLink(
                    provider="ServiceNow",
                    link=f"/change_request/{change['sys_id']}",
                    metadata={
                        "change_number": change["number"],
                        "state": change["state"],
                        "priority": change["priority"],
                        "risk": change["risk"],
                        "impact": change["impact"],
                    },
                )
            )

        # Format the full context for the LLM
        full_context = {
            "changes": changes.get("result", []),
            "context_chunks": context_chunks,
            "source_links": source_links,
            "summary": f"Found {len(changes.get('result', []))} change requests matching the query.",
        }

        return full_context

    def get_capabilities(self) -> Dict[str, Any]:
        """Get ServiceNow provider capabilities"""
        return {
            "name": "ServiceNow Provider",
            "description": "Handles queries about change management and change requests",
            "capabilities": [
                "Change request status",
                "Change request details",
                "Change scheduling",
                "Change risk assessment",
                "Change approval status",
            ],
            "limitations": [
                "Read-only access to changes",
                "Limited to change request scope",
                "No change creation/modification",
            ],
        }
