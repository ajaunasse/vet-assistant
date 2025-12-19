"""Database setup and configuration."""
import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Integer, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, relationship

logger = logging.getLogger(__name__)

# Load environment variables FIRST
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://neuro_user:NeuroVet2024!@localhost:3306/neurolocalizer")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base model
Base = declarative_base()


class Database:
    """Database manager class."""

    def __init__(self, database_url: str = DATABASE_URL):
        self.engine = create_async_engine(
            database_url,
            echo=os.getenv("SQL_ECHO", "false").lower() == "true",
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self, max_retries: int = 10, retry_delay: int = 2) -> None:
        """Create all database tables with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})...")
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Successfully connected to database and created tables")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to connect to database: {e}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to database after {max_retries} attempts")
                    raise

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# Database models
class UserModel(Base):
    """SQLAlchemy model for users."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    clinic_name = Column(String(255), nullable=True)
    order_number = Column(String(100), nullable=True)
    specialty = Column(String(100), nullable=True)
    is_student = Column(Boolean, default=False, nullable=False)
    school_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True, index=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshTokenModel", back_populates="user", cascade="all, delete-orphan")


class RefreshTokenModel(Base):
    """SQLAlchemy model for refresh tokens."""
    __tablename__ = "refresh_tokens"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="refresh_tokens")


class SessionModel(Base):
    """SQLAlchemy model for chat sessions."""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    slug = Column(String(100), nullable=True, unique=True, index=True)
    current_assessment = Column(JSON, nullable=True)
    openai_thread_id = Column(String(255), nullable=True)
    patient_data = Column(JSON, nullable=True)
    is_collecting_data = Column(Boolean, default=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan")
    user = relationship("UserModel", back_populates="sessions")


class MessageModel(Base):
    """SQLAlchemy model for chat messages."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), nullable=True)  # "processed" or "completed" for assistant messages
    follow_up_question = Column(Text, nullable=True)  # Question de suivi for assistant messages

    # Relationships
    session = relationship("SessionModel", back_populates="messages")


class DogBreedModel(Base):
    """SQLAlchemy model for dog breeds."""
    __tablename__ = "dog_breeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConsultationReasonModel(Base):
    """SQLAlchemy model for consultation reasons."""
    __tablename__ = "consultation_reasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Global database instance
database = Database()


# Dependency for FastAPI
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with database.get_session() as session:
        yield session