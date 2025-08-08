#!/usr/bin/env python3
"""
Simple script to add new tables to existing database
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables for database connection
os.environ['DATABASE_URL'] = 'postgresql://user:password@localhost:5432/consultant_bench_db'

import asyncio
import sqlalchemy
from sqlalchemy import text
from database.professional_connection import engine, SessionLocal
from database.models.resume_data import ResumeData, ConsultantSkill

def add_new_tables():
    """Add new tables to existing database"""
    try:
        # First check if we can connect to the database
        db = SessionLocal()
        
        # Check if tables already exist
        inspector = sqlalchemy.inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"Existing tables: {existing_tables}")
        
        # Check if our new tables exist
        if 'resume_data' not in existing_tables:
            print("Adding resume_data table...")
            # Create the resume_data table
            ResumeData.__table__.create(engine, checkfirst=True)
            print("✅ resume_data table created")
        else:
            print("✅ resume_data table already exists")
            
        if 'consultant_skills' not in existing_tables:
            print("Adding consultant_skills table...")
            # Create the consultant_skills table
            ConsultantSkill.__table__.create(engine, checkfirst=True)
            print("✅ consultant_skills table created")
        else:
            print("✅ consultant_skills table already exists")
            
        db.close()
        print("✅ Database tables verified/created successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("This is expected if the new models aren't compatible with existing schema")
        print("The system will work with existing tables for now")

if __name__ == "__main__":
    add_new_tables()
