from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .consultant import Base
from datetime import datetime

class ProjectOpportunity(Base):
    __tablename__ = "project_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Project Details
    project_name = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    project_description = Column(Text)
    
    # Requirements
    required_skills = Column(JSON)           # ["Python", "AWS", "Leadership"]
    required_experience_years = Column(Float)
    team_size = Column(Integer)
    
    # Project Timeline
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration_months = Column(Float)
    
    # Commercial
    budget_range = Column(String)
    hourly_rate = Column(Float)
    
    # Status
    status = Column(String, default="open")  # open, in_progress, closed
    priority = Column(String, default="medium")  # high, medium, low
    
    # Location
    location = Column(String)
    remote_allowed = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConsultantProjectMatch(Base):
    __tablename__ = "consultant_project_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    consultant_id = Column(Integer, ForeignKey("consultants.id"))
    project_opportunity_id = Column(Integer, ForeignKey("project_opportunities.id"))
    
    # Match Analysis
    match_score = Column(Float)              # 0.0 to 1.0
    skill_match_details = Column(JSON)       # Detailed skill alignment
    experience_match = Column(Float)         # Experience level match
    availability_match = Column(Boolean)     # Available for project timeline
    
    # AI Analysis
    match_reasoning = Column(Text)           # AI explanation of match
    recommendation = Column(String)          # strong, good, weak, not_suitable
    
    # Status
    status = Column(String, default="pending")  # pending, reviewed, shortlisted, rejected
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    consultant = relationship("Consultant")
    project_opportunity = relationship("ProjectOpportunity")
