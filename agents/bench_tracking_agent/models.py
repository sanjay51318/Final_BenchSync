from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class StatusUpdateRequest(BaseModel):
    """Request model for updating consultant status"""
    consultant_id: int = Field(..., description="Consultant ID")
    new_status: str = Field(..., description="New bench status")
    activity_description: Optional[str] = Field(None, description="Description of activity")
    is_billable: bool = Field(default=False, description="Whether activity is billable")

class StatusUpdateResponse(BaseModel):
    """Response model for status update"""
    success: bool
    consultant_id: Optional[int] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    activity_id: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None

class UtilizationReportRequest(BaseModel):
    """Request model for utilization report"""
    start_date: str = Field(..., description="Start date (ISO format)")
    end_date: str = Field(..., description="End date (ISO format)")
    consultant_ids: Optional[List[int]] = Field(None, description="Specific consultant IDs")

class ConsultantUtilizationData(BaseModel):
    """Model for individual consultant utilization data"""
    consultant_id: int
    name: str
    employee_id: str
    current_status: str
    total_hours: int
    billable_hours: int
    bench_hours: int
    training_hours: int
    utilization_rate: float
    bench_rate: float

class UtilizationReportResponse(BaseModel):
    """Response model for utilization report"""
    success: bool
    report_period: Optional[str] = None
    total_consultants: int = 0
    overall_utilization_rate: float = 0.0
    total_bench_hours: int = 0
    total_billable_hours: int = 0
    consultant_details: List[ConsultantUtilizationData] = Field(default_factory=list)
    error: Optional[str] = None

class AvailableConsultantsRequest(BaseModel):
    """Request model for getting available consultants"""
    required_skills: Optional[List[str]] = Field(None, description="Required skills filter")

class AvailableConsultantData(BaseModel):
    """Model for available consultant data"""
    id: int
    name: str
    employee_id: str
    email: str
    technical_skills: List[str]
    years_of_experience: float
    bench_duration_days: Optional[int]
    certifications: List[str]
    skill_match_count: Optional[int] = None
    matching_skills: Optional[List[str]] = None

class AvailableConsultantsResponse(BaseModel):
    """Response model for available consultants"""
    success: bool
    total_available: int = 0
    consultants: List[AvailableConsultantData] = Field(default_factory=list)
    filter_applied: str = "none"
    error: Optional[str] = None
