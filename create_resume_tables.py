#!/usr/bin/env python3
"""
Database migration script to add new resume data and skills tables
"""
import sys
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.professional_connection import engine
from database.models.resume_data import Base as ResumeBase
from database.models.consultant import Base as ConsultantBase

def create_tables():
    """Create the new tables"""
    try:
        # Create all tables from both base classes
        ResumeBase.metadata.create_all(bind=engine)
        ConsultantBase.metadata.create_all(bind=engine)
        print("✅ Successfully created resume_data and consultant_skills tables")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
