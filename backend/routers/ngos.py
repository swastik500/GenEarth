from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel

from backend.database import get_db
from backend.models import NGO

router = APIRouter(prefix="/api", tags=["ngos"])


class NGOResponse(BaseModel):
    id: int
    name: str
    state: str
    city: str
    category: str
    website: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


@router.get("/ngos", response_model=List[NGOResponse])
async def get_ngos(
    state: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get filtered list of NGOs"""
    query = db.query(NGO)
    
    if state:
        query = query.filter(NGO.state.ilike(f"%{state}%"))
    
    if city:
        query = query.filter(NGO.city.ilike(f"%{city}%"))
    
    if category:
        query = query.filter(NGO.category.ilike(f"%{category}%"))
    
    ngos = query.all()
    return ngos


@router.get("/ngos/states")
async def get_states(db: Session = Depends(get_db)):
    """Get unique states from NGO database"""
    states = db.query(NGO.state).distinct().all()
    return {"states": [state[0] for state in states]}


@router.get("/ngos/cities")
async def get_cities(
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get unique cities, optionally filtered by state"""
    query = db.query(NGO.city).distinct()
    
    if state:
        query = query.filter(NGO.state.ilike(f"%{state}%"))
    
    cities = query.all()
    return {"cities": [city[0] for city in cities]}


@router.get("/ngos/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get unique categories from NGO database"""
    categories = db.query(NGO.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}
