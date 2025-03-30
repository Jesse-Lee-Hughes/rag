import requests
from typing import Dict, Any, List, Optional
from datetime import datetime


class ServiceNowService:
    """Service to interact with the ServiceNow API"""

    def __init__(self, base_url: str = "http://mock_servicenow:8082"):
        self.base_url = base_url

    async def get_changes(
        self, query: Optional[str] = None, limit: int = 10, offset: int = 0
    ) -> Dict[str, Any]:
        """Fetch change requests from ServiceNow"""
        try:
            params = {
                "sysparm_limit": limit,
                "sysparm_offset": offset,
            }
            if query:
                params["sysparm_query"] = query

            response = requests.get(
                f"{self.base_url}/api/now/table/change_request", params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # For development, return mock data if API is not available
            return {
                "result": [
                    {
                        "sys_id": "CHG001",
                        "number": "CHG0000001",
                        "short_description": "Network Switch Upgrade",
                        "description": "Upgrade network switches in the data center",
                        "state": "new",
                        "priority": "high",
                        "risk": "medium",
                        "impact": "high",
                        "assigned_to": "John Smith",
                        "requested_by": "Jane Doe",
                        "start_date": datetime.now().isoformat(),
                        "end_date": (datetime.now() + timedelta(days=1)).isoformat(),
                    }
                ],
                "count": 1,
                "limit": limit,
                "offset": offset,
            }

    async def create_change(self, change_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new change request"""
        try:
            response = requests.post(
                f"{self.base_url}/api/now/table/change_request", json=change_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error creating change request: {str(e)}")

    async def update_change(
        self, sys_id: str, change_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing change request"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/now/table/change_request/{sys_id}",
                json=change_data,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error updating change request: {str(e)}")
