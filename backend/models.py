from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.database import Base
import uuid
from datetime import datetime


class NGO(Base):
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # Waste/Energy/Water/etc.
    website = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    description = Column(Text, nullable=True)


class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    state = Column(String, nullable=False, index=True)  # "National" or state name
    category = Column(String, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)
    how_to_apply = Column(Text, nullable=False)
    official_url = Column(String, nullable=True)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    language = Column(String, default="en")  # en/hi/mr
    active_mode = Column(String, default="normal")  # normal/quiz
    quiz_index = Column(Integer, default=0)
    quiz_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" or "bot"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class User(Base):
    """User model for gamification tracking"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    
    # Gamification fields
    ecoscore = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime, nullable=True)
    
    # Badges as JSON list
    badges = Column(JSON, default=list)
    
    # Activity counters
    quiz_completed = Column(Integer, default=0)
    images_analyzed = Column(Integer, default=0)
    chat_questions = Column(Integer, default=0)
    ngos_viewed = Column(Integer, default=0)
    schemes_viewed = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")


class UserActivity(Base):
    """Track user activities for gamification"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    activity_type = Column(String, nullable=False)  # quiz, image_analysis, chat, ngo_view, scheme_view
    points_earned = Column(Integer, default=0)
    
    activity_metadata = Column(JSON, nullable=True)  # Store extra info (quiz score, image path, etc.)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="activities")
