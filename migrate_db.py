#!/usr/bin/env python3
"""Database migration script to add missing columns"""

from app.models.database import SessionLocal, engine
from sqlalchemy import text

def migrate_database():
    """Add missing columns to existing database"""
    db = SessionLocal()
    
    try:
        # Check if assigned_to column exists
        result = db.execute(text("PRAGMA table_info(tickets)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'assigned_to' not in columns:
            print("Adding assigned_to column to tickets table...")
            db.execute(text("ALTER TABLE tickets ADD COLUMN assigned_to TEXT"))
            db.commit()
            print("✅ Added assigned_to column")
        else:
            print("✅ assigned_to column already exists")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()