from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Consultant(Base):
    __tablename__ = "consultants"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    
    # Skills and Competencies (JSON format)
    technical_skills = Column(JSON)  # ["Python", "Java", "React"]
    soft_skills = Column(JSON)       # ["Leadership", "Communication"]
    certifications = Column(JSON)    # ["AWS", "PMP"]
    
    # Experience
    years_of_experience = Column(Float)
    previous_projects = Column(JSON)
    
    # Current Status
    bench_status = Column(String, default="available")  # available, on_project, training
    current_project_id = Column(String, nullable=True)
    bench_start_date = Column(DateTime, nullable=True)
    
    # Profile Analysis
    profile_analysis = Column(Text)  # AI-generated summary
    skill_vector = Column(Text)      # Embeddings for matching
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bench_activities = relationship("BenchActivity", back_populates="consultant")
    resume_data = relationship("ResumeData", back_populates="consultant")
    skills = relationship("ConsultantSkill", back_populates="consultant")
