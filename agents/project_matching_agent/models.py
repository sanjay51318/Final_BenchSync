from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ProjectOpportunityRequest(BaseModel):
    """Request model for creating project opportunity"""
    project_name: str = Field(..., description="Name of the project")
    client_name: str = Field(..., description="Client company name")
    project_description: str = Field(..., description="Project description")
    required_skills: List[str] = Field(..., description="Required technical skills")
    required_experience_years: float = Field(..., description="Required years of experience")
    start_date: str = Field(..., description="Project start date (ISO format)")
    duration_months: float = Field(..., description="Project duration in months")
    hourly_rate: Optional[float] = Field(None, description="Hourly rate")
    location: Optional[str] = Field(None, description="Project location")
    remote_allowed: bool = Field(default=True, description="Remote work allowed")

class ProjectOpportunityResponse(BaseModel):
    """Response model for project opportunity creation"""
    success: bool
    project_id: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None

class ConsultantMatchData(BaseModel):
    """Model for consultant match data"""
    consultant_id: int
    name: str
    employee_id: str
    email: str
    overall_score: float
    skill_score: float
    experience_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    recommendation: str  # strong, good, moderate, weak
    reasoning: str

class ProjectMatchRequest(BaseModel):
    """Request model for project matching"""
    project_id: int = Field(..., description="Project ID to match consultants to")
    top_n: int = Field(default=10, description="Number of top matches to return")

class ProjectMatchResponse(BaseModel):
    """Response model for project matching"""
    success: bool
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    total_consultants_evaluated: int = 0
    qualified_matches: int = 0
    top_matches: List[ConsultantMatchData] = Field(default_factory=list)
    error: Optional[str] = None

class ProjectListRequest(BaseModel):
    """Request model for getting project list"""
    status: str = Field(default="open", description="Project status filter")
    client_name: Optional[str] = Field(None, description="Client name filter")

class ProjectData(BaseModel):
    """Model for project data"""
    id: int
    project_name: str
    client_name: str
    required_skills: List[str]
    required_experience_years: float
    duration_months: float
    start_date: Optional[str]
    location: Optional[str]
    remote_allowed: bool
    hourly_rate: Optional[float]
    status: str
    priority: str
    created_at: str

class ProjectListResponse(BaseModel):
    """Response model for project list"""
    success: bool
    total_projects: int = 0
    projects: List[ProjectData] = Field(default_factory=list)
    error: Optional[str] = None

class SkillRecommendationRequest(BaseModel):
    """Request model for skill-based consultant recommendations"""
    required_skills: List[str] = Field(..., description="Required skills")
    min_experience: float = Field(default=0.0, description="Minimum experience years")
    limit: int = Field(default=10, description="Number of recommendations to return")

class ConsultantRecommendationData(BaseModel):
    """Model for consultant recommendation data"""
    consultant_id: int
    name: str
    employee_id: str
    technical_skills: List[str]
    years_of_experience: float
    matching_skills: List[str]
    skill_match_rate: float
    total_skills: int

class SkillRecommendationResponse(BaseModel):
    """Response model for skill-based recommendations"""
    success: bool
    required_skills: List[str] = Field(default_factory=list)
    min_experience: float = 0.0
    total_found: int = 0
    recommendations: List[ConsultantRecommendationData] = Field(default_factory=list)
    error: Optional[str] = None
