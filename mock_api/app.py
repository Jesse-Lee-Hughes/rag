from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional

app = FastAPI(title="Mock SD-WAN Controller API")

# Mock data structure
MOCK_DATA = {
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
                        {"name": "GigE0/0", "ip": "192.168.1.1/24", "status": "up"},
                        {"name": "GigE0/1", "ip": "10.0.1.1/24", "status": "up"},
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
                        {"name": "GigE0/0", "ip": "192.168.2.1/24", "status": "up"}
                    ],
                },
            },
            {
                "name": "BRANCH2-EDGE-01",
                "model": "vEdge-1000",
                "status": "active",
                "config": {
                    "vlans": [
                        {"id": 100, "name": "Data", "ip": "10.102.0.1/24"},
                        {"id": 200, "name": "Voice", "ip": "10.202.0.1/24"},
                    ],
                    "interfaces": [
                        {"name": "GigE0/0", "ip": "192.168.3.1/24", "status": "up"}
                    ],
                },
            },
            {
                "name": "BRANCH3-EDGE-01",
                "model": "vEdge-1000",
                "status": "down",
                "config": {
                    "vlans": [
                        {"id": 100, "name": "Data", "ip": "10.103.0.1/24"},
                        {"id": 200, "name": "Voice", "ip": "10.203.0.1/24"},
                    ],
                    "interfaces": [
                        {"name": "GigE0/0", "ip": "192.168.4.1/24", "status": "down"}
                    ],
                },
            },
            {
                "name": "BRANCH4-EDGE-01",
                "model": "vEdge-1000",
                "status": "active",
                "config": {
                    "vlans": [
                        {"id": 100, "name": "Data", "ip": "10.104.0.1/24"},
                        {"id": 200, "name": "Voice", "ip": "10.204.0.1/24"},
                    ],
                    "interfaces": [
                        {"name": "GigE0/0", "ip": "192.168.5.1/24", "status": "up"}
                    ],
                },
            },
        ],
    }
}


@app.get("/organization/config")
async def get_organization_config():
    return MOCK_DATA
