from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from backend.database import get_db
from backend.models import GovernmentScheme

router = APIRouter(prefix="/api/government", tags=["government"]) 


class GovernmentSchemeResponse(BaseModel):
    id: int
    name: str
    state: str
    category: str
    summary: str
    eligibility: str
    how_to_apply: str
    official_url: Optional[str]

    class Config:
        from_attributes = True


def _apply_filters(query, state: Optional[str], category: Optional[str], level: Optional[str], search: Optional[str]):
    if state:
        query = query.filter(GovernmentScheme.state.ilike(f"%{state}%"))
    if category:
        query = query.filter(GovernmentScheme.category.ilike(f"%{category}%"))
    if level:
        if level.lower() == "national":
            query = query.filter(GovernmentScheme.state == "National")
        elif level.lower() == "state":
            query = query.filter(GovernmentScheme.state != "National")
    if search:
        like = f"%{search}%"
        query = query.filter(
            (GovernmentScheme.name.ilike(like)) |
            (GovernmentScheme.summary.ilike(like)) |
            (GovernmentScheme.eligibility.ilike(like))
        )
    return query


@router.get("/schemes", response_model=List[GovernmentSchemeResponse])
async def get_schemes(
    state: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    level: Optional[str] = Query(None, description="national or state"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get filtered list of government schemes"""
    query = db.query(GovernmentScheme)
    query = _apply_filters(query, state, category, level, search)
    return query.all()


@router.get("/states")
async def get_states(db: Session = Depends(get_db)):
    states = db.query(GovernmentScheme.state).distinct().all()
    return {"states": [s[0] for s in states]}


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(GovernmentScheme.category).distinct().all()
    return {"categories": [c[0] for c in categories]}


@router.get("/levels")
async def get_levels():
    return {"levels": ["National", "State"]}
