"""
Opportunity Agent Models
Database models for opportunity management and AI-powered matching
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Opportunity(Base):
    """Enhanced Opportunity model with AI capabilities"""
    __tablename__ = 'opportunities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    client_name = Column(String(100), nullable=False)
    required_skills = Column(JSON, nullable=False)  # List of required skills
    experience_level = Column(String(50), default='mid')  # junior, mid, senior, architect
    project_duration = Column(String(100))
    budget_range = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default='open')  # open, in_progress, filled, cancelled, on_hold
    
    # AI-enhanced fields
    skill_vector = Column(JSON)  # Embedding vector for skill matching
    ai_score = Column(Float, default=0.5)  # AI-calculated opportunity score
    ai_recommendations = Column(Text)  # AI-generated recommendations
    match_threshold = Column(Float, default=0.3)  # Minimum match score for consultant suggestions
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))  # Admin who created the opportunity
    
    # Relationships
    applications = relationship("OpportunityApplication", back_populates="opportunity")
    assessments = relationship("OpportunityAssessment", back_populates="opportunity")

class OpportunityApplication(Base):
    """Consultant applications for opportunities"""
    __tablename__ = 'opportunity_applications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    consultant_id = Column(Integer, ForeignKey('consultants.id'), nullable=False)
    consultant_email = Column(String(100), nullable=False)
    
    # Application details
    application_status = Column(String(50), default='applied')  # applied, under_review, accepted, rejected
    cover_letter = Column(Text)
    proposed_rate = Column(String(50))
    availability_start = Column(DateTime)
    
    # AI matching data
    match_score = Column(Float)  # AI-calculated match score
    ai_analysis = Column(Text)  # AI analysis of the match
    recommendation_level = Column(String(50))  # Excellent, Good, Fair, Potential
    
    # Metadata
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="applications")
    consultant = relationship("Consultant", back_populates="applications")

class OpportunityAssessment(Base):
    """AI-powered opportunity assessments"""
    __tablename__ = 'opportunity_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # Assessment details
    assessment_type = Column(String(50), default='ai_analysis')  # ai_analysis, manual_review
    assessment_score = Column(Float)  # Overall assessment score
    technical_score = Column(Float)  # Technical requirements score
    market_score = Column(Float)  # Market demand score
    urgency_score = Column(Float)  # Project urgency score
    
    # AI analysis results
    skill_analysis = Column(JSON)  # Detailed skill requirement analysis
    market_demand = Column(JSON)  # Market demand for required skills
    consultant_pool = Column(JSON)  # Available consultant pool analysis
    recommendations = Column(Text)  # AI recommendations for the opportunity
    
    # Predicted outcomes
    estimated_fill_time = Column(Integer)  # Days to fill the position
    predicted_success_rate = Column(Float)  # Success probability
    risk_factors = Column(JSON)  # Identified risk factors
    
    # Metadata
    assessed_at = Column(DateTime, default=datetime.utcnow)
    assessed_by = Column(String(100))  # System or admin
    
    # Relationships
    opportunity = relationship("Opportunity", back_populates="assessments")

class ConsultantOpportunityMatch(Base):
    """AI-generated matches between consultants and opportunities"""
    __tablename__ = 'consultant_opportunity_matches'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultants.id'), nullable=False)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False)
    
    # Match analysis
    overall_match_score = Column(Float, nullable=False)
    skill_match_score = Column(Float)
    experience_match_score = Column(Float)
    availability_match_score = Column(Float)
    cultural_fit_score = Column(Float)
    
    # AI insights
    match_reasoning = Column(Text)  # AI explanation of the match
    strengths = Column(JSON)  # Consultant strengths for this opportunity
    potential_gaps = Column(JSON)  # Areas where consultant might need support
    ai_confidence = Column(Float)  # AI confidence in the match
    
    # Match status
    match_status = Column(String(50), default='suggested')  # suggested, viewed, applied, dismissed
    consultant_notified = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OpportunityMetrics(Base):
    """Metrics and analytics for opportunity management"""
    __tablename__ = 'opportunity_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.utcnow)
    
    # Daily metrics
    total_opportunities = Column(Integer, default=0)
    open_opportunities = Column(Integer, default=0)
    filled_opportunities = Column(Integer, default=0)
    applications_received = Column(Integer, default=0)
    
    # AI metrics
    ai_matches_generated = Column(Integer, default=0)
    ai_match_accuracy = Column(Float)
    avg_opportunity_score = Column(Float)
    avg_match_score = Column(Float)
    
    # Performance metrics
    avg_time_to_fill = Column(Float)  # Days
    fill_rate = Column(Float)  # Percentage
    consultant_satisfaction = Column(Float)
    client_satisfaction = Column(Float)
    
    # Market insights
    top_demanded_skills = Column(JSON)
    skill_supply_demand_ratio = Column(JSON)
    market_trends = Column(JSON)

# Additional model for enhanced consultant tracking
class EnhancedConsultant(Base):
    """Enhanced consultant model with opportunity-focused data"""
    __tablename__ = 'enhanced_consultants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultants.id'), nullable=False)
    
    # Opportunity preferences
    preferred_project_types = Column(JSON)
    preferred_clients = Column(JSON)
    preferred_duration = Column(String(100))
    rate_expectations = Column(String(100))
    remote_preference = Column(String(50))  # remote, hybrid, onsite, flexible
    
    # Performance tracking
    opportunities_applied = Column(Integer, default=0)
    opportunities_accepted = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_project_rating = Column(Float)
    
    # AI insights
    skill_growth_areas = Column(JSON)
    career_recommendations = Column(Text)
    market_positioning = Column(Text)
    
    # Availability tracking
    current_availability = Column(String(50))  # available, busy, partially_available
    next_available_date = Column(DateTime)
    max_concurrent_projects = Column(Integer, default=1)
    
    # Metadata
    profile_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database creation script
def create_opportunity_tables():
    """Create all opportunity-related tables"""
    from sqlalchemy import create_engine
    from database.professional_connection import get_database_url
    
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    print("Opportunity tables created successfully!")

if __name__ == "__main__":
    create_opportunity_tables()
