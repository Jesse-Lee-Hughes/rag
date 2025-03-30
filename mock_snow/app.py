from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

app = FastAPI(title="Mock ServiceNow API")

# Mock data structure
MOCK_CHANGES = {
    "changes": [
        {
            "sys_id": "CHG001",
            "number": "CHG0000001",
            "short_description": "Network Switch Upgrade",
            "description": "Upgrade network switches in the data center to support 100Gbps",
            "state": "new",
            "priority": "high",
            "risk": "medium",
            "impact": "high",
            "assigned_to": "John Smith",
            "requested_by": "Jane Doe",
            "start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
        {
            "sys_id": "CHG002",
            "number": "CHG0000002",
            "short_description": "Database Migration",
            "description": "Migrate production database to new hardware",
            "state": "in_progress",
            "priority": "medium",
            "risk": "high",
            "impact": "high",
            "assigned_to": "Alice Johnson",
            "requested_by": "Bob Wilson",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    ]
}


class ChangeRequest(BaseModel):
    short_description: str
    description: str
    priority: str
    risk: str
    impact: str
    assigned_to: str
    requested_by: str
    start_date: str
    end_date: str


class ChangeUpdate(BaseModel):
    short_description: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    priority: Optional[str] = None
    risk: Optional[str] = None
    impact: Optional[str] = None
    assigned_to: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@app.get("/api/now/table/change_request")
async def get_changes(
    sysparm_query: Optional[str] = None,
    sysparm_limit: Optional[int] = 10,
    sysparm_offset: Optional[int] = 0,
):
    """Get change requests with optional filtering"""
    changes = MOCK_CHANGES["changes"]

    # Apply query filter if provided
    if sysparm_query:
        # Simple keyword search for demo purposes
        changes = [
            change
            for change in changes
            if any(
                keyword.lower() in str(value).lower()
                for keyword in sysparm_query.split()
                for value in change.values()
            )
        ]

    # Apply pagination
    total_count = len(changes)
    start_idx = sysparm_offset
    end_idx = start_idx + sysparm_limit
    paginated_changes = changes[start_idx:end_idx]

    return {
        "result": paginated_changes,
        "count": total_count,
        "limit": sysparm_limit,
        "offset": sysparm_offset,
    }


@app.post("/api/now/table/change_request")
async def create_change(change: ChangeRequest):
    """Create a new change request"""
    new_change = {
        "sys_id": f"CHG{len(MOCK_CHANGES['changes']) + 1:03d}",
        "number": f"CHG{len(MOCK_CHANGES['changes']) + 1:07d}",
        "state": "new",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        **change.dict(),
    }

    MOCK_CHANGES["changes"].append(new_change)
    return {"result": new_change}


@app.patch("/api/now/table/change_request/{sys_id}")
async def update_change(sys_id: str, change_update: ChangeUpdate):
    """Update an existing change request"""
    # Find the change request
    change = next((c for c in MOCK_CHANGES["changes"] if c["sys_id"] == sys_id), None)

    if not change:
        raise HTTPException(status_code=404, detail="Change request not found")

    # Update only provided fields
    update_data = change_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        change[field] = value

    change["updated_at"] = datetime.now().isoformat()

    return {"result": change}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
