#!/usr/bin/env python3
"""Entry point for the NeuroVet backend application."""
import sys
import os
import time
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import app
from src.infrastructure.database import database


async def wait_for_database():
    """Wait for database to be ready."""
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            async with database.get_session() as session:
                await session.execute("SELECT 1")
            print("✅ Database connection established")
            return True
        except Exception as e:
            retry_count += 1
            print(f"⏳ Waiting for database... ({retry_count}/{max_retries})")
            await asyncio.sleep(2)
    
    print("❌ Failed to connect to database after maximum retries")
    return False


async def main():
    """Main async function."""
    print("🧠 Starting NeuroVet Backend...")
    
    # Wait for database
    if not await wait_for_database():
        sys.exit(1)
    
    print("✅ Database ready")
    
    # Start the application
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(main())