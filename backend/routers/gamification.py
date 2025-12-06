from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from backend.database import get_db
from backend.gamification import award_points, get_user_profile, get_leaderboard

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


class ActivityRequest(BaseModel):
    username: str
    activity_type: str  # quiz_complete, image_analysis, chat_question, ngo_view, scheme_view
    metadata: Optional[dict] = None


class ActivityResponse(BaseModel):
    points_earned: int
    total_ecoscore: int
    activity_type: str
    streak: dict
    new_badges: list
    message: Optional[str] = None


@router.post("/activity", response_model=ActivityResponse)
async def track_activity(request: ActivityRequest, db: Session = Depends(get_db)):
    """
    Track user activity and award points
    
    Activity types:
    - quiz_complete: +10 points
    - image_analysis: +5 points
    - chat_question: +3 points (first 5/day)
    - ngo_view: +5 points
    - scheme_view: +5 points
    """
    result = award_points(
        db=db,
        username=request.username,
        activity_type=request.activity_type,
        metadata=request.metadata
    )
    return result


@router.get("/profile/{username}")
async def get_profile(username: str, db: Session = Depends(get_db)):
    """Get user profile with EcoScore, badges, streaks, and stats"""
    return get_user_profile(db, username)


@router.get("/leaderboard")
async def get_top_users(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get top users by EcoScore"""
    return {
        "leaderboard": get_leaderboard(db, limit)
    }


@router.get("/badges")
async def list_badges():
    """List all available badges"""
    from backend.gamification import BADGES
    
    return {
        "badges": [
            {
                "id": badge_id,
                "name": badge_data["name"],
                "description": badge_data["description"],
                "icon": badge_data["icon"]
            }
            for badge_id, badge_data in BADGES.items()
        ]
    }
