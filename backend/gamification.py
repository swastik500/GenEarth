"""
Gamification engine for EcoMitra
Handles scoring, badges, streaks, and achievements
"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from backend.models import User, UserActivity
import logging


# ============= SCORING RULES =============
POINTS = {
    "quiz_complete": 10,
    "image_analysis": 5,
    "chat_question": 3,  # Cap: first 5 per day
    "ngo_view": 5,
    "scheme_view": 5,
    "daily_streak_bonus": 10
}

DAILY_CHAT_LIMIT = 5  # Max chat questions that earn points per day


# ============= BADGE DEFINITIONS =============
BADGES = {
    "waste_warrior": {
        "name": "Waste Warrior",
        "description": "Upload 3+ waste images for analysis",
        "icon": "🗑️",
        "condition": lambda user: user.images_analyzed >= 3
    },
    "energy_saver": {
        "name": "Energy Saver",
        "description": "Ask 5+ energy-related questions",
        "icon": "⚡",
        "condition": lambda user: user.chat_questions >= 5  # Simplified: count all chats
    },
    "scheme_explorer": {
        "name": "Scheme Explorer",
        "description": "View 3+ government schemes",
        "icon": "🏛️",
        "condition": lambda user: user.schemes_viewed >= 3
    },
    "ngo_connector": {
        "name": "NGO Connector",
        "description": "Explore NGOs 3+ times",
        "icon": "🤝",
        "condition": lambda user: user.ngos_viewed >= 3
    },
    "quiz_champ": {
        "name": "Quiz Champ",
        "description": "Score ≥ 4/5 on quiz",
        "icon": "🏆",
        "condition": lambda user: user.quiz_completed >= 1  # Simplified: completed any quiz
    },
    "streak_starter": {
        "name": "Streak Starter",
        "description": "Maintain at least 3-day streak",
        "icon": "🔥",
        "condition": lambda user: user.current_streak >= 3
    }
}


def get_or_create_user(db: Session, username: str, email: Optional[str] = None) -> User:
    """Get existing user or create new one"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = User(username=username, email=email, badges=[])
        db.add(user)
        db.commit()
        db.refresh(user)
        logging.info(f"Created new user: {username}")
    return user


def update_streak(user: User, db: Session) -> Dict:
    """Update user's streak based on activity"""
    today = date.today()
    
    if user.last_active_date is None:
        # First activity ever
        user.current_streak = 1
        user.longest_streak = 1
        user.last_active_date = datetime.combine(today, datetime.min.time())
        bonus_points = 0
    else:
        last_active = user.last_active_date.date()
        days_diff = (today - last_active).days
        
        if days_diff == 0:
            # Same day activity - no streak change
            bonus_points = 0
        elif days_diff == 1:
            # Consecutive day - increment streak
            user.current_streak += 1
            user.last_active_date = datetime.combine(today, datetime.min.time())
            
            if user.current_streak > user.longest_streak:
                user.longest_streak = user.current_streak
            
            # Award streak bonus
            bonus_points = POINTS["daily_streak_bonus"]
            user.ecoscore += bonus_points
            
            logging.info(f"User {user.username} streak: {user.current_streak} days (+{bonus_points} points)")
        else:
            # Streak broken - reset
            user.current_streak = 1
            user.last_active_date = datetime.combine(today, datetime.min.time())
            bonus_points = 0
            logging.info(f"User {user.username} streak reset")
    
    db.commit()
    
    return {
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "bonus_points": bonus_points
    }


def award_points(
    db: Session,
    username: str,
    activity_type: str,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Award points for an activity and update counters
    Returns: dict with points earned, new total, streak info, new badges
    """
    user = get_or_create_user(db, username)
    
    # Update streak
    streak_info = update_streak(user, db)
    
    # Check daily chat limit
    if activity_type == "chat_question":
        today = date.today()
        chat_count_today = db.query(UserActivity).filter(
            UserActivity.user_id == user.id,
            UserActivity.activity_type == "chat_question",
            UserActivity.created_at >= datetime.combine(today, datetime.min.time())
        ).count()
        
        if chat_count_today >= DAILY_CHAT_LIMIT:
            # No points for exceeding daily limit
            return {
                "points_earned": 0,
                "total_ecoscore": user.ecoscore,
                "message": f"Daily chat limit reached ({DAILY_CHAT_LIMIT} questions)",
                "streak": streak_info,
                "new_badges": []
            }
    
    # Calculate points
    points = POINTS.get(activity_type, 0)
    
    # Update user stats
    user.ecoscore += points
    
    # Update activity counters
    if activity_type == "quiz_complete":
        user.quiz_completed += 1
    elif activity_type == "image_analysis":
        user.images_analyzed += 1
    elif activity_type == "chat_question":
        user.chat_questions += 1
    elif activity_type == "ngo_view":
        user.ngos_viewed += 1
    elif activity_type == "scheme_view":
        user.schemes_viewed += 1
    
    # Record activity
    activity = UserActivity(
        user_id=user.id,
        activity_type=activity_type,
        points_earned=points,
        activity_metadata=metadata or {}
    )
    db.add(activity)
    
    # Check for new badges
    old_badges = set(user.badges or [])
    new_badges_earned = check_badges(user)
    user.badges = list(new_badges_earned)
    
    newly_earned = new_badges_earned - old_badges
    
    db.commit()
    db.refresh(user)
    
    return {
        "points_earned": points,
        "total_ecoscore": user.ecoscore,
        "activity_type": activity_type,
        "streak": streak_info,
        "new_badges": [
            {
                "id": badge_id,
                "name": BADGES[badge_id]["name"],
                "icon": BADGES[badge_id]["icon"]
            }
            for badge_id in newly_earned
        ]
    }


def check_badges(user: User) -> set:
    """Check which badges user has earned"""
    earned = set()
    
    for badge_id, badge_data in BADGES.items():
        if badge_data["condition"](user):
            earned.add(badge_id)
    
    return earned


def get_user_profile(db: Session, username: str) -> Dict:
    """Get complete user profile with gamification stats"""
    user = get_or_create_user(db, username)
    
    earned_badges = check_badges(user)
    
    return {
        "username": user.username,
        "ecoscore": user.ecoscore,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "badges": [
            {
                "id": badge_id,
                "name": BADGES[badge_id]["name"],
                "description": BADGES[badge_id]["description"],
                "icon": BADGES[badge_id]["icon"],
                "earned": badge_id in earned_badges
            }
            for badge_id in BADGES.keys()
        ],
        "stats": {
            "quiz_completed": user.quiz_completed,
            "images_analyzed": user.images_analyzed,
            "chat_questions": user.chat_questions,
            "ngos_viewed": user.ngos_viewed,
            "schemes_viewed": user.schemes_viewed
        }
    }


def get_leaderboard(db: Session, limit: int = 10) -> List[Dict]:
    """Get top users by EcoScore"""
    top_users = db.query(User).order_by(User.ecoscore.desc()).limit(limit).all()
    
    return [
        {
            "rank": idx + 1,
            "username": user.username,
            "ecoscore": user.ecoscore,
            "current_streak": user.current_streak,
            "badge_count": len(user.badges or [])
        }
        for idx, user in enumerate(top_users)
    ]
