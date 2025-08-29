#!/usr/bin/env python3
"""Database initialization script."""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.infrastructure.database import database
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


async def init_database():
    """Initialize the database by creating all tables."""
    print("🔄 Initializing database...")
    
    try:
        await database.create_tables()
        print("✅ Database tables created successfully!")
        
        # Test connection
        from sqlalchemy import text
        async with database.get_session() as session:
            await session.execute(text("SELECT 1"))
        print("✅ Database connection test passed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    finally:
        await database.close()
    
    return True


async def check_database():
    """Check database status."""
    print("🔍 Checking database status...")
    
    try:
        async with database.get_session() as session:
            from sqlalchemy import text
            result = await session.execute(text("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = DATABASE()"))
            table_count = result.scalar()
            print(f"📊 Found {table_count} tables in database")
            
            # List tables  
            result = await session.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            if tables:
                print("📋 Tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("📋 No tables found")
                
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    finally:
        await database.close()
    
    return True


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "init"
    
    if command == "init":
        success = asyncio.run(init_database())
    elif command == "check":
        success = asyncio.run(check_database())
    else:
        print(f"Unknown command: {command}")
        print("Usage: python init_db.py [init|check]")
        success = False
    
    sys.exit(0 if success else 1)