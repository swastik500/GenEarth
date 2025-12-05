from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ecomitra.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    _ensure_schema()


def _ensure_schema():
    """Lightweight migration: add missing columns for existing SQLite DBs.

    - Adds chat_sessions.created_at if missing
    - Adds chat_messages.created_at if missing
    """
    try:
        # Only run for SQLite
        if "sqlite" not in DATABASE_URL:
            return

        # Use a begin() block to ensure statements are committed
        with engine.begin() as conn:
            def column_exists(table: str, column: str) -> bool:
                rows = conn.exec_driver_sql(f"PRAGMA table_info('{table}')").fetchall()
                # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
                return any(row[1] == column for row in rows)

            # chat_sessions.created_at
            if not column_exists("chat_sessions", "created_at"):
                conn.exec_driver_sql("ALTER TABLE chat_sessions ADD COLUMN created_at DATETIME")
                # initialize existing rows
                conn.exec_driver_sql("UPDATE chat_sessions SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

            # chat_messages.created_at
            if not column_exists("chat_messages", "created_at"):
                conn.exec_driver_sql("ALTER TABLE chat_messages ADD COLUMN created_at DATETIME")
                conn.exec_driver_sql("UPDATE chat_messages SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    except Exception as e:
        # Do not fail app startup if migration fails; just log to console
        print(f"⚠️ Schema ensure skipped due to error: {e}")
