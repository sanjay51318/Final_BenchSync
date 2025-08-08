from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ResumeData(Base):
    __tablename__ = "resume_data"
    
    id = Column(Integer, primary_key=True, index=True)
    consultant_id = Column(Integer, ForeignKey("consultants.id"), nullable=False)
    
    # Resume Information
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Extracted Data from Resume
    extracted_skills = Column(JSON)  # Skills extracted from resume
    extracted_experience = Column(JSON)  # Work experience details
    extracted_education = Column(JSON)  # Education information
    extracted_certifications = Column(JSON)  # Certifications found
    extracted_projects = Column(JSON)  # Projects mentioned
    
    # Analysis Results
    skill_analysis = Column(Text)  # AI analysis of skills
    experience_summary = Column(Text)  # Experience summary
    recommendations = Column(Text)  # AI recommendations
    
    # Processing Status
    processing_status = Column(String, default="pending")  # pending, processed, error
    processing_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant = relationship("Consultant", back_populates="resume_data")


class ConsultantSkill(Base):
    __tablename__ = "consultant_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    consultant_id = Column(Integer, ForeignKey("consultants.id"), nullable=False)
    
    # Skill Details
    skill_name = Column(String, nullable=False)
    skill_category = Column(String)  # technical, soft, certification, tool
    proficiency_level = Column(String)  # beginner, intermediate, advanced, expert
    years_experience = Column(Integer)
    
    # Source Information
    source = Column(String, default="manual")  # manual, resume, project, assessment
    confidence_score = Column(Integer, default=100)  # 0-100, for AI extracted skills
    
    # Status
    is_active = Column(String, default="active")  # active, inactive, deprecated
    verified = Column(String, default="unverified")  # verified, unverified, disputed
    
    # Metadata
    added_date = Column(DateTime, default=datetime.utcnow)
    last_used_date = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant = relationship("Consultant", back_populates="skills")
