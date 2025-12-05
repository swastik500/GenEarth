from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
import uuid


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

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" or "bot"
    message = Column(Text, nullable=False)

    session = relationship("ChatSession", back_populates="messages")
