from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import Base  # for typing

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])

# Use a simple in-memory store for now; can be swapped to DB later
ITEMS: List[dict] = []

@router.get("/items")
def list_items(category: Optional[str] = None):
    if category:
        return [i for i in ITEMS if i.get("category") == category]
    return ITEMS

@router.post("/items")
def post_item(
    title: str = Body(...),
    category: str = Body(..., description="e.g., cardboard, scrap, clothing, electronics"),
    description: Optional[str] = Body(None),
    contact: Optional[str] = Body(None),
):
    if not title or not category:
        raise HTTPException(status_code=400, detail="title and category are required")
    item = {
        "id": len(ITEMS) + 1,
        "title": title.strip(),
        "category": category.strip().lower(),
        "description": (description or "").strip(),
        "contact": (contact or "").strip(),
        "created_at": datetime.utcnow().isoformat()
    }
    ITEMS.append(item)
    return item
