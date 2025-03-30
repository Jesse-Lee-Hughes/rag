import requests
from typing import Dict, Any


class SDWANService:
    """Service to interact with the mock SD-WAN API"""

    def __init__(self, base_url: str = "http://mock_sdwan:8080"):
        self.base_url = base_url

    async def get_organization_config(self) -> Dict[str, Any]:
        """Fetch organization configuration from SD-WAN controller"""
        try:
            response = requests.get(f"{self.base_url}/organization/config")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # For development, return mock data if API is not available
            return {
                "organization": {
                    "name": "Big Data Org",
                    "uid": "1234",
                    "devices": [
                        {
                            "name": "DC-EDGE-01",
                            "model": "vEdge-2000",
                            "status": "active",
                            "config": {
                                "vlans": [
                                    {"id": 100, "name": "Data", "ip": "10.100.0.1/24"},
                                    {"id": 200, "name": "Voice", "ip": "10.200.0.1/24"},
                                ],
                                "interfaces": [
                                    {
                                        "name": "GigE0/0",
                                        "ip": "192.168.1.1/24",
                                        "status": "up",
                                    },
                                    {
                                        "name": "GigE0/1",
                                        "ip": "10.0.1.1/24",
                                        "status": "up",
                                    },
                                ],
                            },
                        },
                        {
                            "name": "BRANCH1-EDGE-01",
                            "model": "vEdge-1000",
                            "status": "active",
                            "config": {
                                "vlans": [
                                    {"id": 100, "name": "Data", "ip": "10.101.0.1/24"},
                                    {"id": 200, "name": "Voice", "ip": "10.201.0.1/24"},
                                ],
                                "interfaces": [
                                    {
                                        "name": "GigE0/0",
                                        "ip": "192.168.2.1/24",
                                        "status": "up",
                                    }
                                ],
                            },
                        },
                    ],
                }
            }
