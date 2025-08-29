#!/usr/bin/env python3
"""
Database initialization script for NeuroVet
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from infrastructure.database.connection import engine, Base
from infrastructure.database.models import ChatSession, ChatMessage

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    create_tables()