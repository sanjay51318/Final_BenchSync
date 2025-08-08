import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime  # ADD THIS LINE
from .models.consultant import Base
from .models.bench_status import BenchActivity, BenchUtilization  
from .models.project_opportunity import ProjectOpportunity, ConsultantProjectMatch

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/consultant_bench_db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# ADD THIS MISSING FUNCTION
def test_connection():
    """Test database connection"""
    try:
        connection = engine.connect()
        result = connection.execute("SELECT 1;")
        connection.close()
        print("Database connection successful!")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

# Dependency for getting database session
def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
def init_db():
    """Initialize database with tables"""
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
