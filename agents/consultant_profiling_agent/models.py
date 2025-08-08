from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ConsultantProfileRequest(BaseModel):
    """Request model for consultant profile analysis"""
    profile_content: str = Field(..., description="Resume/profile text or PDF content")
    consultant_name: str = Field(..., description="Full name of consultant")
    employee_id: str = Field(..., description="Unique employee identifier")
    email: str = Field(..., description="Consultant email address")

class SkillAnalysis(BaseModel):
    """Model for skill analysis results"""
    technical_skills: List[str] = Field(default_factory=list, description="Extracted technical skills")
    soft_skills: List[str] = Field(default_factory=list, description="Extracted soft skills")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    competencies: List[str] = Field(default_factory=list, description="Core competencies")
    project_experience: List[str] = Field(default_factory=list, description="Project experience keywords")

class ConsultantInsights(BaseModel):
    """Model for AI-generated consultant insights"""
    summary: str = Field(..., description="AI-generated profile summary")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    recommendations: List[str] = Field(default_factory=list, description="Development recommendations")
    suitability_areas: List[str] = Field(default_factory=list, description="Suitable project areas")

class ConsultantProfileResponse(BaseModel):
    """Response model for consultant profile analysis"""
    success: bool
    consultant_id: Optional[int] = None
    consultant_name: Optional[str] = None
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    experience_years: float = 0.0
    competencies: List[str] = Field(default_factory=list)
    project_experience: List[str] = Field(default_factory=list)
    skill_vector: List[float] = Field(default_factory=list)
    ai_summary: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    suitability_areas: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    message: Optional[str] = None

class ConsultantSearchRequest(BaseModel):
    """Request model for searching consultants by skills"""
    required_skills: List[str] = Field(..., description="Required technical skills")
    min_experience_years: float = Field(default=0.0, description="Minimum years of experience")

class ConsultantSearchResponse(BaseModel):
    """Response model for consultant search results"""
    success: bool
    total_found: int = 0
    consultants: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
