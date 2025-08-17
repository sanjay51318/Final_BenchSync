#!/usr/bin/env python3
"""
Enhanced Professional Models for Resume Analysis Integration
Includes models for storing resume analysis data and consultant skills
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False, default='password123')  # Default password
    role = Column(String(50), nullable=False)  # 'consultant' | 'admin'
    department = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to consultant profile
    consultant_profile = relationship("ConsultantProfile", back_populates="user", uselist=False)
    attendance_records = relationship("AttendanceRecord", back_populates="user")
    
class ConsultantProfile(Base):
    __tablename__ = 'consultant_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    primary_skill = Column(String(100))
    experience_years = Column(Integer, default=0)
    resume_status = Column(String(50), default='pending')  # 'updated' | 'pending' | 'outdated'
    attendance_rate = Column(Float, default=0.0)
    training_status = Column(String(50), default='not-started')  # 'completed' | 'in-progress' | 'not-started' | 'overdue'
    opportunities_count = Column(Integer, default=0)
    bench_start_date = Column(String(50))
    current_status = Column(String(50), default='available')  # 'available' | 'on_project' | 'in_training'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="consultant_profile")
    resume_analyses = relationship("ResumeAnalysis", back_populates="consultant")
    skills = relationship("ConsultantSkill", back_populates="consultant")
    feedbacks = relationship("ResumeFeedback", back_populates="consultant")
    applications = relationship("OpportunityApplication", back_populates="consultant")

class AttendanceRecord(Base):
    __tablename__ = 'attendance_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    date = Column(String(20), nullable=False)  # YYYY-MM-DD format
    status = Column(String(20), nullable=False)  # 'present' | 'absent' | 'half_day' | 'leave' | 'holiday'
    check_in_time = Column(String(10))  # HH:MM format
    check_out_time = Column(String(10))  # HH:MM format
    hours_worked = Column(Float, default=8.0)
    notes = Column(Text)
    location = Column(String(100), default='office')  # 'office' | 'remote' | 'client_site'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="attendance_records")

class AdminNotification(Base):
    __tablename__ = 'admin_notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # 'consultant_update', 'skill_change', 'resume_upload'
    user_id = Column(String, ForeignKey('users.id'), nullable=True)
    is_read = Column(Boolean, default=False)
    data = Column(JSON, nullable=True)  # Store additional notification data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User")

class ResumeAnalysis(Base):
    __tablename__ = 'resume_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    extracted_text = Column(Text)
    
    # AI Analysis Results
    extracted_skills = Column(JSON)  # List of skills found
    extracted_competencies = Column(JSON)  # List of competencies
    identified_roles = Column(JSON)  # List of potential roles
    skill_vector = Column(JSON)  # Embedding vector as JSON
    
    # AI Generated Insights
    ai_summary = Column(Text)
    ai_feedback = Column(Text)
    ai_suggestions = Column(Text)
    
    # Analysis Metadata
    analysis_version = Column(String(50), default='1.0')
    processing_time = Column(Float)  # Time taken for analysis
    confidence_score = Column(Float)  # Overall confidence in analysis
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant = relationship("ConsultantProfile", back_populates="resume_analyses")

class ConsultantSkill(Base):
    __tablename__ = 'consultant_skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    skill_name = Column(String(100), nullable=False)
    skill_category = Column(String(50))  # 'technical' | 'soft' | 'domain'
    proficiency_level = Column(String(20))  # 'beginner' | 'intermediate' | 'advanced' | 'expert'
    years_experience = Column(Float, default=0.0)
    is_primary = Column(Boolean, default=False)
    source = Column(String(50), default='resume')  # 'resume' | 'manual' | 'assessment'
    confidence_score = Column(Float, default=0.0)  # AI confidence in skill detection
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant = relationship("ConsultantProfile", back_populates="skills")

class ResumeFeedback(Base):
    __tablename__ = 'resume_feedbacks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    resume_analysis_id = Column(Integer, ForeignKey('resume_analyses.id'))
    
    # Feedback Content
    feedback_type = Column(String(50))  # 'skills_gap' | 'improvement' | 'recommendation' | 'achievement'
    feedback_category = Column(String(50))  # 'technical' | 'soft_skills' | 'experience' | 'format'
    feedback_title = Column(String(200))
    feedback_content = Column(Text)
    priority = Column(String(20), default='medium')  # 'low' | 'medium' | 'high'
    
    # Feedback Metadata
    is_automated = Column(Boolean, default=True)  # True for AI-generated, False for manual
    is_addressed = Column(Boolean, default=False)
    admin_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant = relationship("ConsultantProfile", back_populates="feedbacks")

class ProjectOpportunity(Base):
    __tablename__ = 'project_opportunities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    description = Column(Text)
    client_name = Column(String(200))
    required_skills = Column(JSON)  # List of required skills
    experience_required = Column(Integer, default=0)
    experience_level = Column(String(50))  # 'junior' | 'intermediate' | 'senior' | 'lead'
    location = Column(String(200))
    project_duration = Column(String(100))
    budget_range = Column(String(100))
    start_date = Column(String(50))
    end_date = Column(String(50))
    status = Column(String(50), default='open')  # 'open' | 'filled' | 'cancelled'
    created_date = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("OpportunityApplication", back_populates="opportunity")
    skill_gaps = relationship("OpportunitySkillGap", back_populates="opportunity")

class OpportunityApplication(Base):
    __tablename__ = 'opportunity_applications'
    
    id = Column(String(50), primary_key=True)  # Changed to String to support custom IDs like app_25_xyz
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    opportunity_id = Column(Integer, ForeignKey('project_opportunities.id'), nullable=False)
    status = Column(String(50), default='applied')  # 'applied' | 'interview' | 'selected' | 'rejected'
    cover_letter = Column(Text)
    application_data = Column(JSON)  # Store additional application information
    match_score = Column(Float, default=0.0)  # AI-calculated match score
    ai_reasoning = Column(Text)  # AI explanation for the match
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    opportunity = relationship("ProjectOpportunity", back_populates="applications")
    consultant = relationship("ConsultantProfile", back_populates="applications")

class TrainingRecord(Base):
    __tablename__ = 'training_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    training_name = Column(String(200), nullable=False)
    training_category = Column(String(100))  # 'technical' | 'soft_skills' | 'certification'
    provider = Column(String(200))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    completion_status = Column(String(50), default='enrolled')  # 'enrolled' | 'in_progress' | 'completed' | 'dropped'
    completion_percentage = Column(Float, default=0.0)
    certification_earned = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BenchMetrics(Base):
    __tablename__ = 'bench_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    metric_date = Column(String(20), nullable=False)  # YYYY-MM-DD format
    utilization_rate = Column(Float, default=0.0)
    billable_hours = Column(Float, default=0.0)
    bench_days = Column(Integer, default=0)
    training_hours = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Enhanced Training and Certification Models

class TrainingCategory(Base):
    __tablename__ = 'training_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(50))  # For UI display
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    programs = relationship("TrainingProgram", back_populates="category")

class TrainingProgram(Base):
    __tablename__ = 'training_programs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('training_categories.id'), nullable=False)
    provider = Column(String(200))
    duration_hours = Column(Integer, default=40)
    difficulty_level = Column(String(50))  # 'beginner', 'intermediate', 'advanced'
    prerequisites = Column(JSON)  # List of required skills
    learning_objectives = Column(JSON)  # List of learning goals
    cost = Column(Float, default=0.0)
    certification_available = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("TrainingCategory", back_populates="programs")
    enrollments = relationship("TrainingEnrollment", back_populates="program")

class TrainingEnrollment(Base):
    __tablename__ = 'training_enrollments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    program_id = Column(Integer, ForeignKey('training_programs.id'), nullable=False)
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    status = Column(String(50), default='enrolled')  # 'enrolled', 'in_progress', 'completed', 'dropped', 'on_hold'
    progress_percentage = Column(Float, default=0.0)
    time_spent_hours = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    program = relationship("TrainingProgram", back_populates="enrollments")
    consultant = relationship("ConsultantProfile", foreign_keys=[consultant_id])
    progress_records = relationship("TrainingProgress", back_populates="enrollment")

class TrainingProgress(Base):
    __tablename__ = 'training_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(Integer, ForeignKey('training_enrollments.id'), nullable=False)
    milestone = Column(String(200))
    progress_percentage = Column(Float, nullable=False)
    time_spent_hours = Column(Float, default=0.0)
    notes = Column(Text)
    recorded_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollment = relationship("TrainingEnrollment", back_populates="progress_records")

class TrainingRecommendation(Base):
    __tablename__ = 'training_recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    program_id = Column(Integer, ForeignKey('training_programs.id'), nullable=False)
    recommendation_reason = Column(Text)
    priority_score = Column(Float, default=0.0)  # 0-1 scale
    skill_gaps_addressed = Column(JSON)  # List of skills this training addresses
    recommended_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='pending')  # 'pending', 'accepted', 'declined', 'expired'
    
    # Relationships
    consultant = relationship("ConsultantProfile", foreign_keys=[consultant_id])
    program = relationship("TrainingProgram", foreign_keys=[program_id])

class Certification(Base):
    __tablename__ = 'certifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    name = Column(String(200), nullable=False)
    issuing_organization = Column(String(200))
    issue_date = Column(DateTime)
    expiration_date = Column(DateTime)
    credential_id = Column(String(100))
    verification_url = Column(String(500))
    skills_validated = Column(JSON)  # List of skills this certification validates
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    consultant = relationship("ConsultantProfile", foreign_keys=[consultant_id])

class SkillDevelopmentPlan(Base):
    __tablename__ = 'skill_development_plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    target_skills = Column(JSON)  # List of skills to develop
    current_skills = Column(JSON)  # Current skill levels
    recommended_trainings = Column(JSON)  # List of recommended training program IDs
    timeline_weeks = Column(Integer, default=12)
    status = Column(String(50), default='active')  # 'active', 'completed', 'on_hold', 'cancelled'
    progress_percentage = Column(Float, default=0.0)
    created_date = Column(DateTime, default=datetime.utcnow)
    target_completion_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    
    # Relationships
    consultant = relationship("ConsultantProfile", foreign_keys=[consultant_id])

class OpportunitySkillGap(Base):
    __tablename__ = 'opportunity_skill_gaps'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    opportunity_id = Column(Integer, ForeignKey('project_opportunities.id'), nullable=False)
    missing_skills = Column(JSON)  # List of skills consultant is missing for this opportunity
    skill_gap_analysis = Column(JSON)  # Detailed analysis of gaps
    viewed_at = Column(DateTime, default=datetime.utcnow)  # When consultant viewed this opportunity
    could_not_apply = Column(Boolean, default=True)  # Whether they couldn't apply due to skill gaps
    gap_severity = Column(String(20), default='medium')  # 'low', 'medium', 'high' - how many critical skills missing
    opportunity_priority = Column(String(20), default='medium')  # How attractive this opportunity was
    
    # Relationships
    consultant = relationship("ConsultantProfile", foreign_keys=[consultant_id])
    opportunity = relationship("ProjectOpportunity", foreign_keys=[opportunity_id])


class ConsultantAssignment(Base):
    __tablename__ = 'consultant_assignments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    consultant_id = Column(Integer, ForeignKey('consultant_profiles.id'), nullable=False)
    opportunity_id = Column(Integer, ForeignKey('project_opportunities.id'), nullable=False)
    status = Column(String(50), default='active')  # 'active', 'completed', 'cancelled'
    assigned_date = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant = relationship("ConsultantProfile", foreign_keys=[consultant_id])
    opportunity = relationship("ProjectOpportunity", foreign_keys=[opportunity_id])
