#!/usr/bin/env python3
"""
Complete Database Recreation Script
Drops and recreates the entire database with new schema
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "2005"
DB_NAME = "consultant_bench_db"

def recreate_database():
    """Drop and recreate the database"""
    try:
        # Connect to PostgreSQL server (not to the specific database)
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminate all connections to the target database
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid()
        """)
        
        # Drop the database if it exists
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        print(f"✅ Dropped database {DB_NAME}")
        
        # Create the database
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"✅ Created database {DB_NAME}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ Recreating PostgreSQL database...")
    if recreate_database():
        print("✅ Database recreation completed!")
    else:
        print("❌ Database recreation failed!")
