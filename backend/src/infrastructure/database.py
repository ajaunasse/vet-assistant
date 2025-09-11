"""Database setup and configuration."""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Integer, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, relationship


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

    async def create_tables(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

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

    # Relationships
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan")


class MessageModel(Base):
    """SQLAlchemy model for chat messages."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

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