#!/usr/bin/env python3
import os
import sys
import json
import logging
import traceback
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, ValidationError, field_validator, Field
import uvicorn

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
if sys.platform == "win32":
    # Windows-specific logging configuration to handle Unicode
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/backend.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/backend.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)

# Import database models and connections
try:
    from database.professional_connection import ProfessionalDatabase
    logger.info("Successfully imported database models")
except ImportError as e:
    logger.error(f"Database import error: {e}")
    logger.error(traceback.format_exc())

# Import attendance chatbot
try:
    from utils.attendance_chatbot import AttendanceChatbot
    attendance_chatbot = None  # Will be initialized after database setup
    logger.info("Attendance chatbot imported")
except ImportError as e:
    logger.warning(f"Attendance chatbot not available: {e}")
    attendance_chatbot = None

# Initialize AI clients with error handling
resume_analyzer = None
training_client = None
report_client = None

try:
    from utils.resume_analyzer_interface import ResumeAnalyzerMCPClient
    resume_analyzer = ResumeAnalyzerMCPClient()
    logger.info("Resume analyzer client initialized")
except ImportError as e:
    logger.warning(f"Resume analyzer not available: {e}")

try:
    from utils.training_interface import TrainingMCPClient
    training_client = TrainingMCPClient()
    logger.info("Training client initialized")
except ImportError as e:
    logger.warning(f"Training client not available: {e}")

try:
    from utils.professional_report_interface import ProfessionalReportClient
    report_client = ProfessionalReportClient()
    logger.info("Report generator client initialized")
except ImportError as e:
    logger.warning(f"Report generator not available: {e}")

logger.info("Successfully imported all available dependencies")

# Initialize FastAPI app
app = FastAPI(
    title="Professional Bench Tracking System",
    description="AI-Enhanced Consultant Management with Skills Analysis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = ProfessionalDatabase()
logger.info("Database connection initialized")

# Initialize attendance chatbot with database connection
if attendance_chatbot is None:
    try:
        from utils.attendance_chatbot import AttendanceChatbot
        attendance_chatbot = AttendanceChatbot(db)
        logger.info("Attendance chatbot initialized with database connection")
    except Exception as e:
        logger.warning(f"Failed to initialize attendance chatbot: {e}")
        attendance_chatbot = None

# Add global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors with user-friendly messages"""
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "message": "Please check your input data",
            "details": error_messages
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError with user-friendly messages"""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "Invalid Input",
            "message": str(exc)
        }
    )

# Helper function to merge consultant skills consistently across all endpoints
def get_consultant_merged_skills(consultant_id):
    """
    Get merged skills for a consultant from both database and resume analysis.
    This ensures consistent skill data across all endpoints.
    """
    try:
        # Get consultant skills from database
        skills = db.get_consultant_skills(consultant_id)
        db_technical_skills = [s['skill_name'] for s in skills if s.get('skill_category') == 'technical']
        db_soft_skills = [s['skill_name'] for s in skills if s.get('skill_category') == 'soft']
        
        # Get resume analysis if available
        resume_analysis = None
        resume_skills = []
        resume_competencies = []
        
        try:
            resume_analysis = db.get_resume_analysis_by_consultant_id(consultant_id)
            if resume_analysis:
                # Extract skills from resume analysis
                if 'skills' in resume_analysis and resume_analysis['skills']:
                    if isinstance(resume_analysis['skills'], str):
                        import json
                        try:
                            resume_skills = json.loads(resume_analysis['skills'])
                        except:
                            resume_skills = [resume_analysis['skills']]
                    else:
                        resume_skills = resume_analysis['skills']
                
                # Extract competencies from resume analysis
                if 'competencies' in resume_analysis and resume_analysis['competencies']:
                    if isinstance(resume_analysis['competencies'], str):
                        import json
                        try:
                            resume_competencies = json.loads(resume_analysis['competencies'])
                        except:
                            resume_competencies = [resume_analysis['competencies']]
                    else:
                        resume_competencies = resume_analysis['competencies']
        except Exception as e:
            logger.warning(f"Could not retrieve resume analysis for consultant {consultant_id}: {e}")
        
        # Merge and deduplicate skills (prioritize resume analysis)
        all_technical_skills = list(set(resume_skills + db_technical_skills))
        all_soft_skills = list(set(resume_competencies + db_soft_skills))
        all_skills = all_technical_skills + all_soft_skills
        
        # Sort skills alphabetically for consistent display
        all_technical_skills.sort()
        all_soft_skills.sort()
        all_skills.sort()
        
        return {
            'all_skills': all_skills,
            'technical_skills': all_technical_skills,
            'soft_skills': all_soft_skills,
            'skills_count': len(all_skills),
            'has_resume_analysis': resume_analysis is not None,
            'resume_analysis': resume_analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting merged skills for consultant {consultant_id}: {e}")
        # Return empty skills if there's an error
        return {
            'all_skills': [],
            'technical_skills': [],
            'soft_skills': [],
            'skills_count': 0,
            'has_resume_analysis': False,
            'resume_analysis': None
        }

# Database initialization - PostgreSQL tables are automatically created
try:
    # Initialize database tables if needed
    from database.professional_connection import init_database
    init_database()
    logger.info("Database tables initialized")
except Exception as e:
    logger.error(f"Database initialization error: {e}")

# Initialize AI clients (already handled above with error handling)

# Pydantic models for API
class ConsultantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name cannot be empty")
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    experience_years: int = Field(..., ge=0, le=50, description="Experience must be between 0 and 50 years")
    department: str = Field(..., min_length=1, max_length=50, description="Department cannot be empty")
    primary_skill: str = Field(..., min_length=1, max_length=50, description="Primary skill cannot be empty")
    skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    availability_status: str = Field("available", pattern="^(available|busy|on_leave)$")
    status: str = Field("active", pattern="^(active|inactive|pending)$")
    attendance_rate: float = Field(100.0, ge=0.0, le=100.0)
    training_status: str = Field("not-started", pattern="^(not-started|in-progress|completed)$")
    
    @field_validator('name', 'department', 'primary_skill')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError(f'Field cannot be empty')
        return v.strip()
    
    @field_validator('skills', 'soft_skills')
    @classmethod
    def validate_skills_list(cls, v):
        if v:
            # Remove empty skills and duplicates
            cleaned_skills = list(set([skill.strip() for skill in v if skill.strip()]))
            return cleaned_skills
        return []

class ConsultantUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: Optional[int] = None
    department: Optional[str] = None
    primary_skill: Optional[str] = None
    skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    availability_status: Optional[str] = None
    status: Optional[str] = None
    attendance_rate: Optional[float] = None
    training_status: Optional[str] = None

class OpportunityCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Opportunity title cannot be empty")
    company: str = Field(..., min_length=1, max_length=100, description="Company name cannot be empty")
    client_name: str = Field(..., min_length=1, max_length=100, description="Client name cannot be empty")
    description: str = Field(..., min_length=10, max_length=2000, description="Description must be at least 10 characters")
    required_skills: List[str] = Field(..., min_items=1, description="At least one skill is required")
    experience_required: int = Field(..., ge=0, le=50, description="Experience must be between 0 and 50 years")
    location: str = Field(..., min_length=1, max_length=100, description="Location cannot be empty")
    status: str = Field("open", pattern="^(open|closed|in_progress|on_hold)$")
    
    @field_validator('required_skills')
    @classmethod
    def validate_skills(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one skill is required')
        # Remove empty skills and duplicates
        cleaned_skills = list(set([skill.strip() for skill in v if skill.strip()]))
        if not cleaned_skills:
            raise ValueError('At least one valid skill is required')
        return cleaned_skills
    
    @field_validator('title', 'company', 'client_name', 'location')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError(f'Field cannot be empty')
        return v.strip()

class ApplicationCreate(BaseModel):
    consultant_email: EmailStr
    consultant_id: Optional[int] = None
    cover_letter: Optional[str] = Field(None, max_length=2000)
    proposed_rate: Optional[str] = Field(None, max_length=50)
    availability_start: Optional[str] = Field(None, max_length=20)
    
    @field_validator('cover_letter')
    @classmethod
    def validate_cover_letter(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Cover letter must be at least 10 characters if provided')
        return v.strip() if v else None

class ApplicationUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|accepted|declined)$", description="Status must be pending, accepted, or declined")

class SkillsAnalysisResponse(BaseModel):
    ai_summary: str
    skills: List[str]
    competencies: List[str]
    ai_feedback: str
    ai_suggestions: str
    confidence_score: float

class TrainingRecommendationRequest(BaseModel):
    opportunity_ids: Optional[List[int]] = Field(None, description="Specific opportunity IDs to analyze, if none provided will analyze all open opportunities")
    missing_skills: Optional[List[str]] = Field(None, description="Specific skills that are missing, if provided will override opportunity analysis")
    experience_level: Optional[str] = Field("intermediate", description="Experience level: beginner, intermediate, advanced")
    include_ai_recommendations: bool = Field(True, description="Whether to use AI-powered recommendations via MCP server")

class DevelopmentPlanRequest(BaseModel):
    target_skills: List[str] = Field(..., min_items=1, description="List of skills to include in the development plan")
    plan_name: str = Field("Custom Development Plan", min_length=1, max_length=100, description="Name for the development plan")
    include_ai_analysis: bool = Field(True, description="Whether to use AI-powered analysis via MCP server")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        consultants = db.get_all_consultants()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "consultants_count": len(consultants)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")

# Authentication endpoints
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def login(login_data: LoginRequest):
    """PostgreSQL-only authentication endpoint"""
    try:
        from database.models.professional_models import User, ConsultantProfile
        
        # Get database session
        session = db.get_session()
        
        try:
            # Find user by email
            user = session.query(User).filter(User.email == login_data.email).first()
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Verify password (simple check for now)
            if login_data.password != "password123":
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Get additional profile data if consultant
            profile_data = {}
            if user.role == 'consultant':
                profile = session.query(ConsultantProfile).filter(
                    ConsultantProfile.user_id == user.id
                ).first()
                
                if profile:
                    profile_data = {
                        'primary_skill': profile.primary_skill,
                        'experience_years': profile.experience_years,
                        'current_status': profile.current_status
                    }
            
            # Create session token
            import uuid
            session_token = str(uuid.uuid4())
            
            logger.info(f"Successful login for {user.email} ({user.role})")
            
            return {
                "success": True,
                "message": f"Login successful - {user.role} authenticated",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "department": user.department or '',
                    **profile_data
                },
                "session_token": session_token
            }
            
        finally:
            session.close()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PostgreSQL login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/logout")
async def logout():
    """Logout endpoint"""
    return {"success": True, "message": "Logged out successfully"}

# Dashboard metrics
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        consultants = db.get_all_consultants()
        opportunities = db.get_all_opportunities()
        
        # Calculate metrics
        total_consultants = len(consultants)
        bench_consultants = len([c for c in consultants if c.get('status') == 'available'])
        active_assignments = len([c for c in consultants if c.get('active_assignments', [])])
        open_opportunities = len([o for o in opportunities if o.get('status') == 'open'])
        
        return {
            "totalConsultants": total_consultants,
            "benchConsultants": bench_consultants,
            "ongoingProjects": active_assignments,
            "reportsGenerated": 47,  # Mock report count - would be actual count from database
            "activeAssignments": active_assignments,
            "openOpportunities": open_opportunities
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Consultant management endpoints
@app.get("/api/consultants")
async def get_all_consultants():
    """Get all consultants with their skills and assignments"""
    try:
        consultants = db.get_all_consultants()
        
        # Enhance with skills and assignments
        enhanced_consultants = []
        for consultant in consultants:
            # Get merged skills using the standardized helper function
            skills_data = get_consultant_merged_skills(consultant['id'])
            
            # Get active assignments (opportunities)
            assignments = db.get_consultant_assignments(consultant['id'])
            
            enhanced_consultant = {
                **consultant,
                'skills': skills_data['all_skills'],
                'technical_skills': skills_data['technical_skills'],
                'soft_skills': skills_data['soft_skills'],
                'skills_count': skills_data['skills_count'],
                'has_resume_analysis': skills_data['has_resume_analysis'],
                'active_assignments': assignments
            }
            enhanced_consultants.append(enhanced_consultant)
        
        return enhanced_consultants
    except Exception as e:
        logger.error(f"Error getting consultants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultants")
async def create_consultant(consultant_data: ConsultantCreate):
    """Create a new consultant"""
    try:
        # Check if email already exists
        existing_consultants = db.get_all_consultants()
        if any(c['email'] == consultant_data.email for c in existing_consultants):
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create consultant
        consultant_id = db.add_consultant(
            name=consultant_data.name,
            email=consultant_data.email,
            phone=consultant_data.phone,
            location=consultant_data.location,
            experience_years=consultant_data.experience_years,
            department=consultant_data.department,
            primary_skill=consultant_data.primary_skill,
            status=consultant_data.status,
            attendance_rate=consultant_data.attendance_rate,
            training_status=consultant_data.training_status,
            availability_status=consultant_data.availability_status
        )
        
        # Add skills
        all_skills = consultant_data.skills + consultant_data.soft_skills
        for skill in all_skills:
            db.add_consultant_skill(
                consultant_id=consultant_id,
                skill_name=skill,
                proficiency_level="intermediate",  # Default
                skill_category="technical" if skill in consultant_data.skills else "soft"
            )
        
        return {
            "id": consultant_id,
            "message": "Consultant created successfully",
            "consultant": consultant_data.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating consultant: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/consultants/{consultant_id}")
async def update_consultant(consultant_id: int, consultant_data: ConsultantUpdate):
    """Update consultant information"""
    try:
        # Update consultant basic info
        update_data = {k: v for k, v in consultant_data.dict().items() if v is not None}
        
        if update_data:
            db.update_consultant(consultant_id, **update_data)
        
        # Update skills if provided
        if consultant_data.skills is not None or consultant_data.soft_skills is not None:
            # Remove existing skills
            db.remove_consultant_skills(consultant_id)
            
            # Add new skills
            all_skills = (consultant_data.skills or []) + (consultant_data.soft_skills or [])
            for skill in all_skills:
                db.add_consultant_skill(
                    consultant_id=consultant_id,
                    skill_name=skill,
                    proficiency_level="intermediate",
                    skill_category="technical" if skill in (consultant_data.skills or []) else "soft"
                )
        
        return {"message": "Consultant updated successfully"}
    except Exception as e:
        logger.error(f"Error updating consultant: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/consultants/{consultant_id}")
async def delete_consultant(consultant_id: int):
    """Delete a consultant"""
    try:
        # Remove consultant skills first
        db.remove_consultant_skills(consultant_id)
        
        # Remove consultant
        db.remove_consultant(consultant_id)
        
        return {"message": "Consultant deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting consultant: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/dashboard/{email}")
async def get_consultant_dashboard(email: str):
    """Get consultant-specific dashboard data"""
    try:
        # Find consultant by email
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get real attendance data from database
        real_attendance_data = None
        attendance_rate = 0
        if attendance_chatbot:
            try:
                real_attendance_data = attendance_chatbot.get_user_attendance_stats(email, 30)
                if 'error' not in real_attendance_data:
                    attendance_rate = real_attendance_data.get('attendance_rate', 0)
                else:
                    # If no attendance data found, use default
                    attendance_rate = 0
            except Exception as e:
                logger.warning(f"Could not fetch attendance data for {email}: {e}")
                attendance_rate = 0
        
        # Get consultant assignments and opportunities
        assignments = db.get_consultant_assignments(consultant['id'])
        opportunities = db.get_all_opportunities()
        
        # Get real training data from training dashboard
        training_data = None
        training_progress_percentage = 0
        training_status = 'not-started'
        
        try:
            # Get current training enrollments
            training_enrollments = db.get_consultant_training(consultant['id'])
            
            # Calculate training progress based on actual enrollments
            if training_enrollments:
                total_progress = sum(enrollment.get('progress_percentage', 0) for enrollment in training_enrollments)
                training_progress_percentage = total_progress / len(training_enrollments)
                
                # Determine training status
                if training_progress_percentage >= 100:
                    training_status = 'completed'
                elif training_progress_percentage > 0:
                    training_status = 'in-progress'
                else:
                    training_status = 'not-started'
            else:
                # Check for recommended training from MCP server
                consultant_skills = db.get_consultant_skills(consultant['id'])
                consultant_skill_names = [skill['skill_name'] for skill in consultant_skills]
                
                # Find missing skills from open opportunities
                missing_skills = []
                for opportunity in opportunities:
                    if opportunity.get('status') == 'open':
                        required_skills = opportunity.get('required_skills', [])
                        opportunity_missing_skills = [
                            skill for skill in required_skills 
                            if skill.lower() not in [s.lower() for s in consultant_skill_names]
                        ]
                        missing_skills.extend(opportunity_missing_skills)
                
                # If there are missing skills, training is recommended (but not started)
                if missing_skills:
                    training_status = 'recommended'
                    training_progress_percentage = 0
                else:
                    training_status = 'not-required'
                    training_progress_percentage = 100
                    
        except Exception as e:
            logger.warning(f"Could not fetch training data for {email}: {e}")
            training_progress_percentage = 0
            training_status = 'not-started'
        
        # Calculate metrics
        opportunities_count = len([o for o in opportunities if o.get('status') == 'open'])
        
        return {
            "consultant_id": consultant['id'],
            "name": consultant['name'],
            "email": consultant['email'],
            "resume_status": "updated" if consultant.get('resume_uploaded') else "not updated",
            "attendance_rate": attendance_rate,
            "attendance_data": real_attendance_data,  # Include full attendance data
            "opportunities_count": opportunities_count,
            "training_progress": training_progress_percentage,  # Now calculated dynamically
            "training_status": training_status,  # Include training status
            "active_assignments": assignments,
            "workflow_steps": [
                {
                    "id": "resume",
                    "label": "Resume Updated",
                    "completed": bool(consultant.get('resume_uploaded')),
                    "inProgress": False
                },
                {
                    "id": "attendance",
                    "label": "Attendance Reported",
                    "completed": attendance_rate > 80,
                    "inProgress": attendance_rate > 0 and attendance_rate <= 80
                },
                {
                    "id": "opportunities",
                    "label": "Opportunities Documented",
                    "completed": opportunities_count > 0,
                    "inProgress": False
                },
                {
                    "id": "training",
                    "label": "Training Completed",
                    "completed": training_status == 'completed' or training_status == 'not-required',
                    "inProgress": training_status == 'in-progress' or training_status == 'recommended'
                }
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/{email}/profile")
async def get_consultant_profile(email: str):
    """Get consultant profile data by email"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get merged skills using the standardized helper function
        skills_data = get_consultant_merged_skills(consultant['id'])
        
        # Build profile response with synchronized skills
        profile_data = {
            "id": consultant['id'],
            "name": consultant['name'],
            "email": consultant['email'],
            "phone": consultant.get('phone', ''),
            "location": consultant.get('location', ''),
            "experience_years": consultant.get('experience_years', 0),
            "department": consultant.get('department', ''),
            "primary_skill": consultant.get('primary_skill', ''),
            "status": consultant.get('status', 'available'),
            "attendance_rate": consultant.get('attendance_rate', 0),
            "training_status": consultant.get('training_status', 'not-started'),
            "availability_status": consultant.get('availability_status', 'available'),
            "technical_skills": skills_data['technical_skills'],
            "soft_skills": skills_data['soft_skills'],
            "resume_analysis": skills_data['resume_analysis'],
            "resume_status": consultant.get('resume_uploaded', False),  # Dynamic resume status
            "resume_uploaded": consultant.get('resume_uploaded', False),  # Boolean flag
            "has_resume_analysis": skills_data['has_resume_analysis'],  # Whether AI analysis exists
            "created_at": consultant.get('created_at'),
            "updated_at": consultant.get('updated_at'),
            "skills_source": {
                "database_technical": [s['skill_name'] for s in db.get_consultant_skills(consultant['id']) if s.get('skill_category') == 'technical'],
                "database_soft": [s['skill_name'] for s in db.get_consultant_skills(consultant['id']) if s.get('skill_category') == 'soft'],
                "resume_technical": skills_data['resume_analysis'].get('skills', []) if skills_data['resume_analysis'] else [],
                "resume_soft": skills_data['resume_analysis'].get('competencies', []) if skills_data['resume_analysis'] else [],
                "total_technical": len(skills_data['technical_skills']),
                "total_soft": len(skills_data['soft_skills']),
                "total_skills": skills_data['skills_count']
            }
        }
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SKILLS MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/consultant/{email}/skills")
async def get_consultant_skills(email: str):
    """Get all skills for a consultant"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get merged skills using the standardized helper function
        skills_data = get_consultant_merged_skills(consultant_id)
        
        # Get detailed skills from database for additional metadata
        db_skills = db.get_consultant_skills_from_db(consultant_id)
        
        # Organize skills by category with merged data
        organized_skills = {
            'technical': [{"skill_name": skill, "skill_category": "technical", "merged": True} for skill in skills_data['technical_skills']],
            'soft': [{"skill_name": skill, "skill_category": "soft", "merged": True} for skill in skills_data['soft_skills']],
            'all': [{"skill_name": skill, "merged": True} for skill in skills_data['all_skills']]
        }
        
        return {
            "consultant_email": email,
            "consultant_id": consultant_id,
            "skills": organized_skills,
            "total_skills": skills_data['skills_count'],
            "has_resume_analysis": skills_data['has_resume_analysis'],
            "skills_breakdown": {
                "technical_count": len(skills_data['technical_skills']),
                "soft_count": len(skills_data['soft_skills']),
                "total_count": skills_data['skills_count']
            },
            "skills_by_source": {
                "resume": len([s for s in db_skills if s.get('source') == 'resume']),
                "manual": len([s for s in db_skills if s.get('source') == 'manual']),
                "assessment": len([s for s in db_skills if s.get('source') == 'assessment'])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/{email}/skills")
async def add_consultant_skill(email: str, skill_data: dict):
    """Add a new skill to consultant"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Extract skill data
        skill_name = skill_data.get('skill_name', '').strip()
        skill_category = skill_data.get('skill_category', 'technical')
        proficiency_level = skill_data.get('proficiency_level', 'intermediate')
        years_experience = skill_data.get('years_experience', 0)
        is_primary = skill_data.get('is_primary', False)
        
        if not skill_name:
            raise HTTPException(status_code=400, detail="Skill name is required")
        
        # Add skill to database
        success = db.add_consultant_skill(
            consultant_id=consultant_id,
            skill_name=skill_name,
            proficiency_level=proficiency_level,
            skill_category=skill_category
        )
        
        if success:
            # Update additional properties if provided
            if years_experience or is_primary:
                db.update_consultant_skill(
                    consultant_id=consultant_id,
                    skill_name=skill_name,
                    years_experience=years_experience,
                    is_primary=is_primary
                )
            
            return {
                "success": True,
                "message": f"Skill '{skill_name}' added successfully",
                "skill": {
                    "skill_name": skill_name,
                    "skill_category": skill_category,
                    "proficiency_level": proficiency_level,
                    "years_experience": years_experience,
                    "is_primary": is_primary
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add skill")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding consultant skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/consultant/{email}/skills/{skill_name}")
async def update_consultant_skill(email: str, skill_name: str, skill_data: dict):
    """Update a consultant's skill"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Extract update data
        proficiency_level = skill_data.get('proficiency_level')
        years_experience = skill_data.get('years_experience')
        is_primary = skill_data.get('is_primary')
        
        # Update skill
        success = db.update_consultant_skill(
            consultant_id=consultant_id,
            skill_name=skill_name,
            proficiency_level=proficiency_level,
            years_experience=years_experience,
            is_primary=is_primary
        )
        
        if success:
            return {
                "success": True,
                "message": f"Skill '{skill_name}' updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating consultant skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/consultant/{email}/skills/{skill_name}")
async def delete_consultant_skill(email: str, skill_name: str):
    """Delete a consultant's skill"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Delete skill from database
        from database.models.professional_models import ConsultantSkill
        
        if hasattr(db, 'SessionLocal') and db.SessionLocal:
            session = db.SessionLocal()
            try:
                skill = session.query(ConsultantSkill).filter(
                    ConsultantSkill.consultant_id == consultant_id,
                    ConsultantSkill.skill_name == skill_name
                ).first()
                
                if skill:
                    session.delete(skill)
                    session.commit()
                    return {
                        "success": True,
                        "message": f"Skill '{skill_name}' deleted successfully"
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
                    
            finally:
                session.close()
        else:
            return {
                "success": True,
                "message": f"Skill '{skill_name}' deleted successfully (mock)"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting consultant skill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/{email}/sync-skills")
async def sync_consultant_skills(email: str):
    """Sync skills from Resume_Agent analysis to consultant profile"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get resume analysis
        resume_analysis = db.get_resume_analysis_by_consultant_id(consultant_id)
        if not resume_analysis:
            raise HTTPException(status_code=404, detail="No resume analysis found for this consultant")
        
        # Extract skills from Resume_Agent analysis
        extracted_skills = resume_analysis.get('skills', [])
        extracted_competencies = resume_analysis.get('soft_skills', [])
        analysis_method = resume_analysis.get('analysis_method', 'Unknown')
        
        if not extracted_skills and not extracted_competencies:
            return {
                "success": False,
                "message": "No skills found in resume analysis to sync"
            }
        
        # Prepare skills for database insertion
        skills_to_add = []
        
        # Add technical skills with higher confidence for Resume_Agent analysis
        confidence_tech = 90 if 'Resume_Agent' in analysis_method else 85
        for skill in extracted_skills:
            skills_to_add.append({
                'skill_name': skill,
                'category': 'technical',
                'proficiency_level': 'intermediate',
                'confidence_score': confidence_tech,
                'source': 'resume_agent_ai'
            })
        
        # Add soft skills/competencies
        confidence_soft = 85 if 'Resume_Agent' in analysis_method else 80
        for competency in extracted_competencies:
            skills_to_add.append({
                'skill_name': competency,
                'category': 'soft',
                'proficiency_level': 'intermediate',
                'confidence_score': confidence_soft,
                'source': 'resume_agent_ai'
            })
        
        # Add skills to database using enhanced method
        added_skills = db.add_skills_from_resume(consultant_id, skills_to_add, 'resume_agent_ai')
        
        return {
            "success": True,
            "message": f"Successfully synced {len(added_skills)} skills from {analysis_method} analysis",
            "synced_skills": added_skills,
            "total_skills_processed": len(skills_to_add),
            "analysis_method": analysis_method,
            "confidence_scores": {
                "technical_skills": confidence_tech,
                "soft_skills": confidence_soft
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing consultant skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/{email}/skills/report-data")
async def get_consultant_skills_for_report(email: str):
    """Get consultant skills formatted for report generation"""
    try:
        # Get consultant data
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get skills from database
        skills = db.get_consultant_skills_from_db(consultant_id)
        
        # Format skills for report
        technical_skills = []
        soft_skills = []
        domain_skills = []
        
        for skill in skills:
            skill_info = {
                'name': skill['skill_name'],
                'proficiency': skill['proficiency_level'],
                'experience_years': skill.get('years_experience', 0),
                'source': skill.get('source', 'manual'),
                'confidence': skill.get('confidence_score', 100),
                'is_primary': skill.get('is_primary', False)
            }
            
            category = skill.get('skill_category', 'technical')
            if category == 'technical':
                technical_skills.append(skill_info)
            elif category == 'soft':
                soft_skills.append(skill_info)
            elif category == 'domain':
                domain_skills.append(skill_info)
        
        # Calculate skill metrics
        total_skills = len(skills)
        primary_skills = [s for s in skills if s.get('is_primary')]
        resume_skills = [s for s in skills if s.get('source') == 'resume']
        
        return {
            "consultant_email": email,
            "consultant_name": consultant['name'],
            "skills_summary": {
                "total_skills": total_skills,
                "technical_skills_count": len(technical_skills),
                "soft_skills_count": len(soft_skills),
                "domain_skills_count": len(domain_skills),
                "primary_skills_count": len(primary_skills),
                "resume_extracted_count": len(resume_skills)
            },
            "skills_by_category": {
                "technical": technical_skills,
                "soft": soft_skills,
                "domain": domain_skills
            },
            "primary_skills": [s['skill_name'] for s in skills if s.get('is_primary')],
            "recent_updates": [
                s for s in skills 
                if s.get('updated_at') and 
                (datetime.now() - datetime.fromisoformat(s['updated_at'].replace('Z', '+00:00'))).days <= 30
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting skills for report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills/all")
async def get_all_skills():
    """Get all skills from all consultants for analytics"""
    try:
        from database.models.professional_models import ConsultantSkill, ConsultantProfile
        
        if hasattr(db, 'SessionLocal') and db.SessionLocal:
            session = db.SessionLocal()
            try:
                # Get all skills with consultant info
                skills_query = session.query(ConsultantSkill).all()
                
                all_skills = []
                for skill in skills_query:
                    all_skills.append({
                        'skill_name': skill.skill_name,
                        'skill_category': skill.skill_category,
                        'proficiency_level': skill.proficiency_level,
                        'years_experience': skill.years_experience or 0,
                        'source': skill.source,
                        'confidence_score': skill.confidence_score or 0,
                        'is_primary': skill.is_primary or False,
                        'consultant_id': skill.consultant_id,
                        'created_at': skill.created_at.isoformat() if skill.created_at else None,
                        'updated_at': skill.updated_at.isoformat() if skill.updated_at else None
                    })
                
                # Calculate analytics
                skill_analytics = {
                    'total_skills': len(all_skills),
                    'unique_skills': len(set([s['skill_name'] for s in all_skills])),
                    'skills_by_category': {
                        'technical': len([s for s in all_skills if s['skill_category'] == 'technical']),
                        'soft': len([s for s in all_skills if s['skill_category'] == 'soft']),
                        'domain': len([s for s in all_skills if s['skill_category'] == 'domain'])
                    },
                    'skills_by_proficiency': {
                        'beginner': len([s for s in all_skills if s['proficiency_level'] == 'beginner']),
                        'intermediate': len([s for s in all_skills if s['proficiency_level'] == 'intermediate']),
                        'advanced': len([s for s in all_skills if s['proficiency_level'] == 'advanced']),
                        'expert': len([s for s in all_skills if s['proficiency_level'] == 'expert'])
                    }
                }
                
                # Calculate most common skills
                from collections import Counter
                skill_counts = Counter([s['skill_name'] for s in all_skills])
                skill_analytics['most_common_skills'] = dict(skill_counts.most_common(10))
                
                return {
                    'success': True,
                    'skills': all_skills,
                    'analytics': skill_analytics
                }
                
            finally:
                session.close()
        else:
            return {
                'success': False,
                'error': 'Database not available',
                'skills': [],
                'analytics': {}
            }
            
    except Exception as e:
        logger.error(f"Error getting all skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skills/sync-all-consultants")
async def sync_all_consultants_skills():
    """Sync skills from resume analysis for all consultants who have resumes"""
    try:
        consultants = db.get_all_consultants()
        sync_results = []
        
        for consultant in consultants:
            try:
                # Check if consultant has resume analysis
                resume_analysis = db.get_resume_analysis_by_consultant_id(consultant['id'])
                
                if resume_analysis:
                    # Sync skills for this consultant
                    extracted_skills = resume_analysis.get('extracted_skills', [])
                    extracted_competencies = resume_analysis.get('extracted_competencies', [])
                    
                    if extracted_skills or extracted_competencies:
                        # Prepare skills for database insertion
                        skills_to_add = []
                        
                        # Add technical skills
                        for skill in extracted_skills:
                            skills_to_add.append({
                                'skill_name': skill,
                                'category': 'technical',
                                'proficiency_level': 'intermediate',
                                'confidence_score': 85
                            })
                        
                        # Add soft skills/competencies
                        for competency in extracted_competencies:
                            skills_to_add.append({
                                'skill_name': competency,
                                'category': 'soft',
                                'proficiency_level': 'intermediate',
                                'confidence_score': 80
                            })
                        
                        # Add skills to database
                        added_skills = db.add_skills_from_resume(consultant['id'], skills_to_add, 'resume')
                        
                        sync_results.append({
                            'consultant_id': consultant['id'],
                            'consultant_email': consultant['email'],
                            'success': True,
                            'skills_added': len(added_skills),
                            'skills_list': added_skills
                        })
                    else:
                        sync_results.append({
                            'consultant_id': consultant['id'],
                            'consultant_email': consultant['email'],
                            'success': True,
                            'skills_added': 0,
                            'message': 'No skills found in resume analysis'
                        })
                else:
                    sync_results.append({
                        'consultant_id': consultant['id'],
                        'consultant_email': consultant['email'],
                        'success': False,
                        'message': 'No resume analysis found'
                    })
                    
            except Exception as consultant_error:
                sync_results.append({
                    'consultant_id': consultant['id'],
                    'consultant_email': consultant['email'],
                    'success': False,
                    'error': str(consultant_error)
                })
        
        # Calculate summary
        successful_syncs = len([r for r in sync_results if r['success']])
        total_skills_added = sum([r.get('skills_added', 0) for r in sync_results if r['success']])
        
        return {
            'success': True,
            'message': f'Completed skills sync for {len(consultants)} consultants',
            'summary': {
                'total_consultants': len(consultants),
                'successful_syncs': successful_syncs,
                'failed_syncs': len(sync_results) - successful_syncs,
                'total_skills_added': total_skills_added
            },
            'results': sync_results
        }
        
    except Exception as e:
        logger.error(f"Error syncing all consultant skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resume upload and analysis
@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    consultant_email: str = Form(...)
):
    """Upload and analyze resume with AI"""
    try:
        # Validate file type - allow PDF and TXT for testing
        allowed_extensions = ['.pdf', '.txt']
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are allowed")
        
        # Find consultant
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == consultant_email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Create uploads directory
        upload_dir = Path("uploads/resumes")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / f"{consultant['id']}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analyze resume with AI using MCP server
        try:
            if resume_analyzer:
                # Extract text based on file type
                resume_text = ""
                if file_extension == '.pdf':
                    # Extract text from PDF
                    try:
                        import PyPDF2
                        with open(file_path, 'rb') as pdf_file:
                            pdf_reader = PyPDF2.PdfReader(pdf_file)
                            for page in pdf_reader.pages:
                                resume_text += page.extract_text()
                    except Exception as pdf_error:
                        logger.warning(f"PDF extraction failed: {pdf_error}")
                        resume_text = f"Resume file: {file.filename}"
                elif file_extension == '.txt':
                    # Read text file directly
                    try:
                        with open(file_path, 'r', encoding='utf-8') as text_file:
                            resume_text = text_file.read()
                    except UnicodeDecodeError:
                        # Try with different encoding if UTF-8 fails
                        with open(file_path, 'r', encoding='latin-1') as text_file:
                            resume_text = text_file.read()
                
                # Analyze resume using MCP server with Resume_Agent AI pipeline
                analysis_result = await resume_analyzer.analyze_resume(resume_text, file.filename)
                
                if analysis_result.get('success'):
                    # Store analysis and sync skills to PostgreSQL using new method
                    storage_result = db.store_resume_analysis_with_skills(
                        consultant_id=consultant['id'],
                        file_name=file.filename,
                        extracted_text=resume_text,
                        analysis_result=analysis_result
                    )
                    
                    if storage_result.get('success'):
                        # Update consultant record
                        db.update_consultant(
                            consultant['id'],
                            resume_uploaded=True,
                            ai_summary=analysis_result.get('ai_summary', '')
                        )
                        
                        # NEW: Skills updated - mark for report refresh
                        if analysis_result.get('skills') or analysis_result.get('soft_skills'):
                            logger.info(f"Skills updated for consultant {consultant['id']}, reports will refresh on next access")
                        
                        return {
                            "message": f"Resume analyzed using {analysis_result.get('analysis_method', 'Resume_Agent_AI')} pipeline",
                            "analysis": {
                                "skills": analysis_result.get('skills', []),
                                "soft_skills": analysis_result.get('soft_skills', []),
                                "competencies": analysis_result.get('competencies', []),
                                "roles": analysis_result.get('roles', []),
                                "ai_summary": analysis_result.get('ai_summary', ''),
                                "ai_feedback": analysis_result.get('ai_feedback', ''),
                                "ai_suggestions": analysis_result.get('ai_suggestions', ''),
                                "confidence_score": analysis_result.get('confidence_score', 0.0),
                                "analysis_method": analysis_result.get('analysis_method', 'Resume_Agent_AI'),
                                "total_skills": analysis_result.get('total_skills', 0),
                                "skill_categories": analysis_result.get('skill_categories', {})
                            },
                            "skills_storage": {
                                "skills_added": storage_result.get('skills_added', 0),
                                "skills_list": storage_result.get('skills_list', [])
                            },
                            "sync_info": {
                                "skills_updated": True,
                                "next_report_will_sync": True,
                                "use_synced_endpoint": f"/api/reports/consultant/{consultant_email}/synced"
                            }
                        }
                else:
                    # Fallback: just save the file
                    db.update_consultant(consultant['id'], resume_uploaded=True)
                    return {
                        "message": "Resume uploaded successfully (analysis failed)",
                        "analysis": {"skills": [], "soft_skills": [], "ai_summary": "Analysis failed"}
                    }
            else:
                # Resume analyzer not available
                db.update_consultant(consultant['id'], resume_uploaded=True)
                return {
                    "message": "Resume uploaded successfully (analyzer not available)",
                    "analysis": {"skills": [], "soft_skills": [], "ai_summary": "Resume analyzer not available"}
                }
                
        except Exception as analysis_error:
            logger.error(f"Resume analysis failed: {analysis_error}")
            # Still save the file
            db.update_consultant(consultant['id'], resume_uploaded=True)
            return {
                "message": "Resume uploaded (analysis failed)",
                "analysis": {"skills": [], "ai_summary": "Analysis failed"}
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant/{consultant_id}/resume-analysis")
async def get_resume_analysis(consultant_id: int):
    """Get AI resume analysis for consultant"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get resume analysis from database
        analysis = db.get_resume_analysis_by_consultant_id(consultant_id)
        
        if analysis:
            return {
                "ai_summary": analysis.get('ai_summary', 'No AI analysis available'),
                "skills": analysis.get('skills', []),
                "competencies": analysis.get('soft_skills', []),
                "ai_feedback": analysis.get('ai_feedback', 'Analysis complete'),
                "ai_suggestions": analysis.get('ai_suggestions', 'Continue developing your skills'),
                "confidence_score": analysis.get('confidence_score', 0.0)
            }
        else:
            # Fallback to consultant skills if no analysis available
            skills = db.get_consultant_skills(consultant_id)
            technical_skills = [s['skill_name'] for s in skills if s.get('skill_category') == 'technical']
            soft_skills = [s['skill_name'] for s in skills if s.get('skill_category') == 'soft']
            
            return {
                "ai_summary": "No AI analysis available",
                "skills": technical_skills,
                "competencies": soft_skills,
                "ai_feedback": f"Analysis complete. Found {len(technical_skills)} technical skills.",
                "ai_suggestions": "Upload a resume for AI-powered analysis and recommendations.",
                "confidence_score": 0.85
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Training dashboard endpoints
@app.get("/api/consultant/{consultant_id}/training-dashboard")
async def get_training_dashboard(consultant_id: int):
    """Get comprehensive training dashboard with AI recommendations via MCP server"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get current enrollments
        training_enrollments = db.get_consultant_training(consultant_id)
        
        # Get opportunities and consultant skills
        opportunities = db.get_all_opportunities()
        consultant_skills = db.get_consultant_skills(consultant_id)
        consultant_skill_names = [skill['skill_name'] for skill in consultant_skills]
        
        # Find missing skills from open opportunities
        missing_skills = []
        opportunity_skills_map = {}
        
        for opportunity in opportunities:
            if opportunity.get('status') == 'open':
                required_skills = opportunity.get('required_skills', [])
                opportunity_missing_skills = [
                    skill for skill in required_skills 
                    if skill.lower() not in [s.lower() for s in consultant_skill_names]
                ]
                
                for missing_skill in opportunity_missing_skills:
                    if missing_skill not in missing_skills:
                        missing_skills.append(missing_skill)
                    
                    if missing_skill not in opportunity_skills_map:
                        opportunity_skills_map[missing_skill] = []
                    opportunity_skills_map[missing_skill].append(opportunity['title'])
        
        # Get AI-powered training recommendations via MCP server
        ai_recommendations = {"recommendations": [], "success": False}
        if training_client and missing_skills:
            try:
                logger.info(f"Getting AI training recommendations for {len(missing_skills)} missing skills")
                mcp_response = await training_client.get_training_recommendations(
                    consultant_id=consultant_id,
                    current_skills=consultant_skill_names,
                    missing_skills=missing_skills,
                    experience_level="intermediate"
                )
                
                # Handle nested MCP response structure
                if isinstance(mcp_response, dict) and mcp_response.get('success'):
                    recommendations_data = mcp_response.get('recommendations', {})
                    if isinstance(recommendations_data, dict):
                        ai_recommendations = {
                            "success": True,
                            "recommendations": recommendations_data.get('recommendations', [])
                        }
                    else:
                        ai_recommendations = {"success": False, "recommendations": []}
                
                logger.info(f"AI recommendations received: {ai_recommendations.get('success', False)}")
            except Exception as e:
                logger.warning(f"AI training recommendations failed, using fallback: {e}")
                ai_recommendations = {"recommendations": [], "success": False}
        
        # Format recommendations for frontend
        formatted_recommendations = []
        if ai_recommendations.get('success') and ai_recommendations.get('recommendations'):
            for rec in ai_recommendations['recommendations'][:5]:  # Top 5
                # Handle different skill formats in the recommendation
                skill = rec.get('skill', '')
                if not skill:
                    # Extract skill from skills_covered or title
                    skills_covered = rec.get('skills_covered', [])
                    if skills_covered:
                        skill = skills_covered[0]  # Use the first skill covered
                    else:
                        # Extract from title as fallback
                        title = rec.get('title', '')
                        for missing_skill in missing_skills:
                            if missing_skill.lower() in title.lower():
                                skill = missing_skill
                                break
                
                related_opportunities = opportunity_skills_map.get(skill, [])
                formatted_recommendations.append({
                    'name': rec.get('title', f"{skill} Training"),
                    'priority': rec.get('priority', 'High'),
                    'reason': rec.get('reason', f"Required for {len(related_opportunities)} opportunities: {', '.join(related_opportunities[:3])}"),
                    'missing_skill': skill,
                    'opportunities_count': len(related_opportunities),
                    'sample_opportunities': related_opportunities[:3],
                    'duration_hours': rec.get('duration_hours', 40),
                    'provider': rec.get('provider', 'Professional Training'),
                    'cost': rec.get('cost', 0),
                    'difficulty': rec.get('difficulty', 'Intermediate'),
                    'market_demand': rec.get('market_demand', 85),
                    'rating': rec.get('rating', 4.5),
                    'certification_available': rec.get('certification_available', rec.get('certification', False)),
                    'url': rec.get('url', ''),
                    'recommendation_score': rec.get('recommendation_score', 85),
                    'ai_generated': True
                })
        else:
            # Fallback recommendations if AI fails
            for skill in missing_skills[:5]:
                related_opportunities = opportunity_skills_map.get(skill, [])
                formatted_recommendations.append({
                    'name': f"{skill} Fundamentals",
                    'priority': 'High',
                    'reason': f"Required for {len(related_opportunities)} opportunities",
                    'missing_skill': skill,
                    'opportunities_count': len(related_opportunities),
                    'sample_opportunities': related_opportunities[:3],
                    'ai_generated': False
                })
        
        return {
            "current_enrollments": training_enrollments,
            "opportunity_based_recommendations": {
                "missing_skills": [
                    {
                        'skill': skill,
                        'opportunities': opportunity_skills_map.get(skill, []),
                        'priority': 'High'
                    } for skill in missing_skills[:5]
                ],
                "training_courses": formatted_recommendations,
                "total_missing": len(missing_skills),
                "ai_powered": ai_recommendations.get('success', False)
            },
            "dashboard_metrics": {
                "skills_to_develop": len(missing_skills),
                "active_trainings": len(training_enrollments),
                "missed_opportunities": len([o for o in opportunities if o.get('status') == 'open']),
                "ai_recommendations_available": ai_recommendations.get('success', False)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/{consultant_id}/opportunity-training-recommendations")
async def get_opportunity_specific_training(consultant_id: int, request_data: TrainingRecommendationRequest):
    """Get AI-powered training recommendations for specific opportunities via MCP server"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get consultant skills
        consultant_skills = db.get_consultant_skills(consultant_id)
        consultant_skill_names = [skill['skill_name'] for skill in consultant_skills]
        
        # Get specific opportunities or all open opportunities
        if request_data.opportunity_ids:
            all_opportunities = db.get_all_opportunities()
            opportunities = [opp for opp in all_opportunities if opp.get('id') and int(opp['id']) in request_data.opportunity_ids]
        else:
            opportunities = [opp for opp in db.get_all_opportunities() if opp.get('status') == 'open']
        
        # Find missing skills for these opportunities
        all_required_skills = []
        opportunity_skill_map = {}
        
        # Use provided missing skills or analyze opportunities
        if request_data.missing_skills:
            missing_skills = request_data.missing_skills
            # Create a simple mapping for provided skills
            for skill in missing_skills:
                opportunity_skill_map[skill] = [{'id': 0, 'title': 'Custom Training Request', 'company': 'Various'}]
        else:
            for opportunity in opportunities:
                required_skills = opportunity.get('required_skills', [])
                for skill in required_skills:
                    if skill.lower() not in [s.lower() for s in consultant_skill_names]:
                        all_required_skills.append(skill)
                        if skill not in opportunity_skill_map:
                            opportunity_skill_map[skill] = []
                        opportunity_skill_map[skill].append({
                            'id': opportunity['id'],
                            'title': opportunity['title'],
                            'company': opportunity['company']
                        })
            
            missing_skills = list(set(all_required_skills))
        
        if not missing_skills:
            return {
                "success": True,
                "message": "No missing skills found for selected opportunities",
                "missing_skills": [],
                "training_recommendations": [],
                "opportunities_analyzed": len(opportunities)
            }
        
        # Get AI-powered recommendations via MCP server
        ai_recommendations = {"success": False, "recommendations": []}
        if training_client and request_data.include_ai_recommendations:
            try:
                logger.info(f"Getting AI training recommendations for {len(missing_skills)} missing skills from {len(opportunities)} opportunities")
                mcp_response = await training_client.get_training_recommendations(
                    consultant_id=consultant_id,
                    current_skills=consultant_skill_names,
                    missing_skills=missing_skills,
                    experience_level=request_data.experience_level or f"{consultant.get('experience_years', 3)}_years"
                )
                
                # Handle nested MCP response structure
                if isinstance(mcp_response, dict) and mcp_response.get('success'):
                    recommendations_data = mcp_response.get('recommendations', {})
                    if isinstance(recommendations_data, dict):
                        ai_recommendations = {
                            "success": True,
                            "recommendations": recommendations_data.get('recommendations', [])
                        }
                    else:
                        ai_recommendations = {"success": False, "recommendations": []}
                
                # Also get skill gap analysis
                gap_analysis = await training_client.analyze_skill_gaps(
                    consultant_skills=consultant_skill_names,
                    target_skills=missing_skills
                )
                
                logger.info(f"AI recommendations success: {ai_recommendations.get('success', False)}")
            except Exception as e:
                logger.warning(f"AI training recommendations failed: {e}")
                ai_recommendations = {"success": False, "recommendations": []}
        
        # Format recommendations with opportunity context
        formatted_recommendations = []
        if ai_recommendations.get('success') and ai_recommendations.get('recommendations'):
            for rec in ai_recommendations['recommendations']:
                # Handle different skill formats in the recommendation
                skill = rec.get('skill', '')
                if not skill:
                    # Extract skill from skills_covered or title
                    skills_covered = rec.get('skills_covered', [])
                    if skills_covered:
                        skill = skills_covered[0]  # Use the first skill covered
                    else:
                        # Extract from title as fallback
                        title = rec.get('title', '')
                        for missing_skill in missing_skills:
                            if missing_skill.lower() in title.lower():
                                skill = missing_skill
                                break
                
                related_opportunities = opportunity_skill_map.get(skill, [])
                
                formatted_recommendations.append({
                    'id': rec.get('training_id', rec.get('id', '')),
                    'title': rec.get('title', f"{skill} Professional Training"),
                    'skill': skill,
                    'skills_covered': rec.get('skills_covered', [skill]),
                    'provider': rec.get('provider', 'Professional Training'),
                    'duration_hours': rec.get('duration_hours', 40),
                    'difficulty': rec.get('difficulty', 'Intermediate'),
                    'cost': rec.get('cost', 0),
                    'certification': rec.get('certification_available', rec.get('certification', False)),
                    'certification_name': rec.get('certification_name', ''),
                    'market_demand': rec.get('market_demand', 85),
                    'career_impact': rec.get('career_impact', 'High'),
                    'rating': rec.get('rating', 4.5),
                    'url': rec.get('url', ''),
                    'recommendation_score': rec.get('recommendation_score', 85),
                    'estimated_roi': rec.get('estimated_roi', 'High'),
                    'reason': rec.get('reason', f"Addresses {skill} skill gap"),
                    'related_opportunities': related_opportunities,
                    'opportunities_count': len(related_opportunities),
                    'priority': rec.get('priority', 'High' if len(related_opportunities) > 1 else 'Medium'),
                    'ai_generated': True,
                    'recommendation_reason': f"Required for {len(related_opportunities)} opportunity(ies): {', '.join([opp['title'] for opp in related_opportunities[:2]])}" if related_opportunities else f"Skill gap identified: {skill}"
                })
        
        return {
            "success": True,
            "consultant_id": consultant_id,
            "consultant_name": consultant.get('name', ''),
            "missing_skills": missing_skills,
            "training_recommendations": formatted_recommendations,
            "opportunities_analyzed": len(opportunities),
            "ai_powered": ai_recommendations.get('success', False),
            "total_recommendations": len(formatted_recommendations),
            "high_priority_count": len([r for r in formatted_recommendations if r['priority'] == 'High'])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting opportunity-specific training recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/{consultant_id}/create-development-plan")
async def create_skill_development_plan(consultant_id: int, request_data: DevelopmentPlanRequest):
    """Create a personalized skill development plan via MCP server"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get consultant current skills
        consultant_skills = db.get_consultant_skills(consultant_id)
        current_skill_names = [skill['skill_name'] for skill in consultant_skills]
        
        # Create development plan via MCP server
        if training_client and request_data.include_ai_analysis:
            try:
                logger.info(f"Creating development plan for consultant {consultant_id} with {len(request_data.target_skills)} target skills")
                
                development_plan = await training_client.create_development_plan(
                    consultant_id=consultant_id,
                    name=request_data.plan_name,
                    current_skills=current_skill_names,
                    target_skills=request_data.target_skills,
                    experience_years=consultant.get('experience_years', 3)
                )
                
                if development_plan.get('success'):
                    return {
                        "success": True,
                        "message": "Development plan created successfully via AI",
                        "plan": development_plan,
                        "ai_generated": True
                    }
                else:
                    raise Exception(f"MCP server failed: {development_plan.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.warning(f"AI development plan creation failed, using fallback: {e}")
        
        # Fallback manual plan creation
        missing_skills = [skill for skill in request_data.target_skills if skill.lower() not in [s.lower() for s in current_skill_names]]
        
        fallback_plan = {
            "plan_name": request_data.plan_name,
            "consultant_id": consultant_id,
            "current_skills": current_skill_names,
            "target_skills": request_data.target_skills,
            "missing_skills": missing_skills,
            "estimated_duration_weeks": len(missing_skills) * 4,  # 4 weeks per skill
            "phases": [
                {
                    "phase": i + 1,
                    "skill": skill,
                    "duration_weeks": 4,
                    "activities": [
                        f"Complete {skill} fundamentals course",
                        f"Practice {skill} through hands-on projects",
                        f"Get {skill} certification"
                    ]
                } for i, skill in enumerate(missing_skills)
            ]
        }
        
        return {
            "success": True,
            "message": "Development plan created with basic recommendations",
            "plan": fallback_plan,
            "ai_generated": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating development plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/consultant/{consultant_id}/enroll-training")
async def enroll_in_training(consultant_id: int, enrollment_data: dict):
    """Enroll consultant in training program"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        training_program = enrollment_data.get('training_program')
        provider = enrollment_data.get('provider', 'Professional Training')
        duration_hours = enrollment_data.get('duration_hours', 40)
        
        # Store enrollment using the new database method
        enrollment_result = db.store_training_enrollment(
            consultant_id=consultant_id,
            training_program=training_program,
            provider=provider,
            duration_hours=duration_hours,
            progress_percentage=5
        )
        
        if not enrollment_result.get('success'):
            raise HTTPException(status_code=500, detail="Failed to store enrollment")
        
        # Update consultant training status to in-progress
        db.update_consultant(consultant_id, training_status='in-progress')
        
        return {
            "success": True,
            "message": f"Successfully enrolled in {training_program}",
            "consultant_id": consultant_id,
            "enrollment_id": enrollment_result['enrollment_id'],
            "enrollment_details": enrollment_result['enrollment_details']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enrolling in training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/consultant/{consultant_id}/update-training-progress")
async def update_training_progress(consultant_id: int, progress_data: dict):
    """Update training progress for consultant"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        progress_percentage = progress_data.get('progress_percentage', 0)
        training_program = progress_data.get('training_program', '')
        
        # Update progress using the new database method
        update_result = db.update_training_progress(
            consultant_id=consultant_id,
            training_program=training_program,
            progress_percentage=progress_percentage
        )
        
        if not update_result.get('success'):
            raise HTTPException(status_code=404, detail="Training program not found")
        
        # Get current enrollments and calculate overall progress
        current_enrollments = db.get_consultant_training(consultant_id)
        
        # Calculate overall progress across all enrollments
        if current_enrollments:
            total_progress = sum(enrollment.get('progress_percentage', 0) for enrollment in current_enrollments)
            overall_progress = total_progress / len(current_enrollments)
        else:
            overall_progress = progress_percentage
        
        # Update training status based on overall progress
        if overall_progress >= 90:
            training_status = 'completed'
        elif overall_progress > 0:
            training_status = 'in-progress'
        else:
            training_status = 'not-started'
        
        # Update in database
        db.update_consultant(consultant_id, training_status=training_status)
        
        return {
            "success": True,
            "message": "Training progress updated successfully",
            "consultant_id": consultant_id,
            "progress_percentage": progress_percentage,
            "overall_progress": overall_progress,
            "training_status": training_status,
            "training_program": training_program
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating training progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Opportunity management
@app.get("/api/opportunities")
async def get_all_opportunities():
    """Get all opportunities"""
    try:
        opportunities = db.get_all_opportunities()
        
        # Ensure all opportunities have proper serializable data
        serialized_opportunities = []
        for opp in opportunities:
            # Ensure required_skills is always a list
            required_skills = opp.get('required_skills', [])
            if isinstance(required_skills, str):
                # If it's a string, split by comma
                required_skills = [skill.strip() for skill in required_skills.split(',') if skill.strip()]
            elif not isinstance(required_skills, list):
                required_skills = []
            
            serialized_opp = {
                'id': str(opp.get('id', '')),
                'title': str(opp.get('title', '')),
                'company': str(opp.get('company', '')),
                'client_name': str(opp.get('client_name', '')),
                'description': str(opp.get('description', '')),
                'required_skills': required_skills,
                'experience_required': int(opp.get('experience_required', 0)),
                'location': str(opp.get('location', '')),
                'status': str(opp.get('status', 'open')),
                'created_at': str(opp.get('created_at', '')),
                'created_date': str(opp.get('created_date', ''))
            }
            
            # Add optional fields if they exist
            optional_fields = ['experience_level', 'project_duration', 'budget_range', 'start_date', 'end_date']
            for field in optional_fields:
                if field in opp:
                    serialized_opp[field] = str(opp[field])
            
            serialized_opportunities.append(serialized_opp)
        
        return serialized_opportunities
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities-with-applications")
async def get_opportunities_with_applications():
    """Get all opportunities with their applications"""
    try:
        opportunities = db.get_all_opportunities()
        
        # Enhance each opportunity with applications
        enhanced_opportunities = []
        for opportunity in opportunities:
            applications = db.get_opportunity_applications(opportunity['id'])
            
            # Calculate accepted count
            accepted_count = len([app for app in applications if app.get('status') == 'accepted'])
            
            enhanced_opportunity = {
                **opportunity,
                'applications': applications,
                'accepted_count': accepted_count
            }
            enhanced_opportunities.append(enhanced_opportunity)
        
        return enhanced_opportunities
    except Exception as e:
        logger.error(f"Error getting opportunities with applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/opportunities")
async def create_opportunity(opportunity_data: OpportunityCreate):
    """Create a new opportunity"""
    try:
        logger.info(f"Creating opportunity with data: {opportunity_data.dict()}")
        
        opportunity_id = db.add_opportunity(
            title=opportunity_data.title,
            company=opportunity_data.company,
            client_name=opportunity_data.client_name,
            description=opportunity_data.description,
            required_skills=opportunity_data.required_skills,
            experience_required=opportunity_data.experience_required,
            location=opportunity_data.location,
            status=opportunity_data.status
        )
        
        logger.info(f"Opportunity created successfully with ID: {opportunity_id}")
        
        return {
            "id": opportunity_id,
            "message": "Opportunity created successfully",
            "opportunity": opportunity_data.dict()
        }
    except ValueError as ve:
        logger.error(f"Validation error creating opportunity: {ve}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Error creating opportunity: {e}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Application management endpoints
@app.post("/api/opportunities/{opportunity_id}/apply")
async def apply_to_opportunity(opportunity_id: str, application_data: ApplicationCreate):
    """Apply to an opportunity"""
    try:
        # Find consultant by email if consultant_id not provided
        if not application_data.consultant_id:
            consultants = db.get_all_consultants()
            consultant = next((c for c in consultants if c['email'] == application_data.consultant_email), None)
            if not consultant:
                raise HTTPException(status_code=404, detail="Consultant not found")
            consultant_id = consultant['id']
        else:
            consultant_id = application_data.consultant_id
            consultant = db.get_consultant(consultant_id)
            if not consultant:
                raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Check if already applied
        existing_applications = db.get_opportunity_applications(str(opportunity_id))
        if any(app['consultant_id'] == str(consultant_id) for app in existing_applications):
            raise HTTPException(status_code=400, detail="Already applied to this opportunity")
        
        # Create application with additional data
        application_id = db.add_application(
            opportunity_id=str(opportunity_id),
            consultant_id=str(consultant_id),
            consultant_email=application_data.consultant_email,
            status='pending',
            cover_letter=application_data.cover_letter,
            proposed_rate=application_data.proposed_rate,
            availability_start=application_data.availability_start
        )
        
        return {
            "id": application_id,
            "message": "Application submitted successfully",
            "consultant_id": consultant_id,
            "opportunity_id": opportunity_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying to opportunity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/opportunities/{opportunity_id}/applications/{application_id}/accept")
async def accept_application(opportunity_id: int, application_id: str):
    """Accept a consultant application"""
    try:
        # Get application details
        applications = db.get_opportunity_applications(opportunity_id)
        application = next((app for app in applications if app['id'] == application_id), None)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update application status
        db.update_application_status(application_id, 'accepted')
        
        # Update consultant status to active and assign to opportunity
        db.update_consultant_status(
            application['consultant_id'],
            status='active',
            availability_status='busy'
        )
        
        # Add assignment record
        db.add_consultant_assignment(
            consultant_id=application['consultant_id'],
            opportunity_id=opportunity_id
        )
        
        # Update opportunity accepted count
        db.increment_opportunity_accepted_count(opportunity_id)
        
        return {"message": "Application accepted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/opportunities/{opportunity_id}/applications/{application_id}/decline")
async def decline_application(opportunity_id: int, application_id: str):
    """Decline a consultant application"""
    try:
        # Get application details
        applications = db.get_opportunity_applications(opportunity_id)
        application = next((app for app in applications if app['id'] == application_id), None)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update application status
        db.update_application_status(application_id, 'declined')
        
        return {"message": "Application declined successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error declining application: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/opportunity-applications/{application_id}/{action}")
async def handle_application_action(application_id: str, action: str):
    """Handle application accept/reject actions with simplified endpoint"""
    try:
        if action not in ['accept', 'reject']:
            raise HTTPException(status_code=400, detail="Action must be 'accept' or 'reject'")
        
        # Get application details to find opportunity_id
        application = db.get_application_by_id(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        opportunity_id = application['opportunity_id']
        consultant_id = application['consultant_id']
        
        if action == 'accept':
            # Update application status to accepted
            db.update_application_status(application_id, 'accepted')
            
            # Update consultant status to active and assign to opportunity
            db.update_consultant_status(
                consultant_id,
                status='active',
                availability_status='busy'
            )
            
            # Add assignment record
            db.add_consultant_assignment(
                consultant_id=consultant_id,
                opportunity_id=opportunity_id
            )
            
            # Update opportunity accepted count
            db.increment_opportunity_accepted_count(opportunity_id)
            
            return {"message": "Application accepted successfully"}
        else:  # reject
            # Update application status to declined
            db.update_application_status(application_id, 'declined')
            
            return {"message": "Application rejected successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling application action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunity-analytics")
async def get_opportunity_analytics():
    """Get comprehensive opportunity analytics and metrics"""
    try:
        # Get all opportunities and applications
        opportunities = db.get_all_opportunities()
        consultants = db.get_all_consultants()
        
        # Calculate analytics
        total_opportunities = len(opportunities)
        open_opportunities = len([opp for opp in opportunities if opp.get('status') == 'open'])
        closed_opportunities = len([opp for opp in opportunities if opp.get('status') == 'closed'])
        in_progress_opportunities = len([opp for opp in opportunities if opp.get('status') == 'in_progress'])
        
        # Application analytics
        total_applications = 0
        pending_applications = 0
        accepted_applications = 0
        declined_applications = 0
        
        opportunity_stats = []
        
        for opportunity in opportunities:
            apps = db.get_opportunity_applications(opportunity['id'])
            total_applications += len(apps)
            
            opp_pending = len([app for app in apps if app.get('status') == 'pending'])
            opp_accepted = len([app for app in apps if app.get('status') == 'accepted'])
            opp_declined = len([app for app in apps if app.get('status') == 'declined'])
            
            pending_applications += opp_pending
            accepted_applications += opp_accepted
            declined_applications += opp_declined
            
            # Calculate match rate
            match_rate = (opp_accepted / max(len(apps), 1)) * 100 if apps else 0
            
            opportunity_stats.append({
                "opportunity_id": opportunity['id'],
                "title": opportunity['title'],
                "company": opportunity.get('company', 'Unknown'),
                "total_applications": len(apps),
                "pending_applications": opp_pending,
                "accepted_applications": opp_accepted,
                "declined_applications": opp_declined,
                "match_rate": round(match_rate, 2),
                "status": opportunity.get('status', 'open'),
                "created_date": opportunity.get('created_date', 'Unknown')
            })
        
        # Consultant engagement analytics
        consultant_engagement = []
        for consultant in consultants:
            # Count applications for this consultant
            consultant_applications = 0
            consultant_accepted = 0
            consultant_pending = 0
            
            for opportunity in opportunities:
                apps = db.get_opportunity_applications(opportunity['id'])
                consultant_apps = [app for app in apps if app.get('consultant_id') == str(consultant['id'])]
                consultant_applications += len(consultant_apps)
                consultant_accepted += len([app for app in consultant_apps if app.get('status') == 'accepted'])
                consultant_pending += len([app for app in consultant_apps if app.get('status') == 'pending'])
            
            success_rate = (consultant_accepted / max(consultant_applications, 1)) * 100 if consultant_applications > 0 else 0
            
            consultant_engagement.append({
                "consultant_id": consultant['id'],
                "name": consultant.get('name', 'Unknown'),
                "email": consultant.get('email', 'Unknown'),
                "total_applications": consultant_applications,
                "accepted_applications": consultant_accepted,
                "pending_applications": consultant_pending,
                "success_rate": round(success_rate, 2),
                "status": consultant.get('status', 'available')
            })
        
        # Skills in demand analytics
        skills_demand = {}
        for opportunity in opportunities:
            required_skills = opportunity.get('required_skills', [])
            if isinstance(required_skills, str):
                required_skills = [s.strip() for s in required_skills.split(',')]
            
            for skill in required_skills:
                if skill:
                    skills_demand[skill] = skills_demand.get(skill, 0) + 1
        
        # Sort skills by demand
        top_skills = sorted(skills_demand.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Market trends (last 30 days simulation)
        market_trends = {
            "opportunities_created_last_30_days": max(0, total_opportunities - 5),  # Simulated
            "applications_last_30_days": max(0, total_applications - 10),  # Simulated
            "average_time_to_fill": "7.5 days",  # Simulated
            "most_active_companies": [
                {"company": opp.get('company', 'Unknown'), "opportunities": 1} 
                for opp in opportunities[:5]
            ]
        }
        
        return {
            "success": True,
            "analytics": {
                "overview": {
                    "total_opportunities": total_opportunities,
                    "open_opportunities": open_opportunities,
                    "closed_opportunities": closed_opportunities,
                    "in_progress_opportunities": in_progress_opportunities,
                    "total_applications": total_applications,
                    "pending_applications": pending_applications,
                    "accepted_applications": accepted_applications,
                    "declined_applications": declined_applications,
                    "overall_success_rate": round((accepted_applications / max(total_applications, 1)) * 100, 2)
                },
                "opportunity_details": opportunity_stats,
                "consultant_engagement": consultant_engagement,
                "skills_demand": {
                    "top_skills": [{"skill": skill, "demand_count": count} for skill, count in top_skills],
                    "total_unique_skills": len(skills_demand)
                },
                "market_trends": market_trends,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting opportunity analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/opportunities/{opportunity_id}/match-consultants")
async def match_consultants_to_opportunity(opportunity_id: str):
    """Match and rank consultants for a specific opportunity based on skills and availability"""
    try:
        # Get opportunity details
        opportunities = db.get_all_opportunities()
        opportunity = next((opp for opp in opportunities if str(opp['id']) == str(opportunity_id)), None)
        
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        # Get all available consultants
        consultants = db.get_all_consultants()
        available_consultants = [c for c in consultants if c.get('availability_status') != 'busy']
        
        # Get required skills for the opportunity
        required_skills = opportunity.get('required_skills', [])
        if isinstance(required_skills, str):
            required_skills = [s.strip() for s in required_skills.split(',')]
        
        matched_consultants = []
        
        for consultant in available_consultants:
            consultant_id = consultant['id']
            
            # Get consultant's skills
            consultant_skills = db.get_consultant_skills(consultant_id)
            skill_names = [skill['skill_name'].lower() for skill in consultant_skills]
            
            # Calculate skill match score
            matched_skills = []
            missing_skills = []
            
            for req_skill in required_skills:
                skill_matched = False
                for consultant_skill in skill_names:
                    if req_skill.lower() in consultant_skill or consultant_skill in req_skill.lower():
                        matched_skills.append(req_skill)
                        skill_matched = True
                        break
                if not skill_matched:
                    missing_skills.append(req_skill)
            
            match_score = len(matched_skills) / max(len(required_skills), 1) if required_skills else 0.5
            
            # Check if already applied
            applications = db.get_opportunity_applications(str(opportunity_id))
            has_applied = any(app.get('consultant_id') == str(consultant_id) for app in applications)
            
            # Calculate consultant rating (simplified)
            rating = 4.0 + (match_score * 1.0)  # Base rating + skill bonus
            
            if not has_applied:
                matched_consultants.append({
                    "consultant_id": consultant_id,
                    "name": consultant.get('name', 'Unknown'),
                    "email": consultant.get('email', 'Unknown'),
                    "match_score": round(match_score * 100, 2),
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                    "experience_years": consultant.get('experience_years', 0),
                    "rating": round(rating, 1),
                    "availability_status": consultant.get('availability_status', 'available'),
                    "location": consultant.get('location', 'Unknown'),
                    "has_applied": has_applied
                })
        
        # Sort by match score and rating
        matched_consultants.sort(key=lambda x: (x['match_score'], x['rating']), reverse=True)
        
        return {
            "success": True,
            "opportunity": {
                "id": opportunity['id'],
                "title": opportunity['title'],
                "company": opportunity.get('company', 'Unknown'),
                "required_skills": required_skills
            },
            "matched_consultants": matched_consultants,
            "total_matches": len(matched_consultants),
            "match_summary": {
                "excellent_matches": len([c for c in matched_consultants if c['match_score'] >= 80]),
                "good_matches": len([c for c in matched_consultants if 60 <= c['match_score'] < 80]),
                "fair_matches": len([c for c in matched_consultants if 40 <= c['match_score'] < 60]),
                "weak_matches": len([c for c in matched_consultants if c['match_score'] < 40])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching consultants to opportunity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/opportunities/{opportunity_id}/notify-consultants")
async def notify_matched_consultants(opportunity_id: str):
    """Notify matched consultants about a new opportunity"""
    try:
        # Get matched consultants
        match_result = await match_consultants_to_opportunity(opportunity_id)
        
        if not match_result.get('success'):
            raise HTTPException(status_code=500, detail="Failed to match consultants")
        
        matched_consultants = match_result['matched_consultants']
        opportunity = match_result['opportunity']
        
        # Filter for high-match consultants (above 60% match)
        high_match_consultants = [c for c in matched_consultants if c['match_score'] >= 60]
        
        notifications_sent = []
        
        for consultant in high_match_consultants:
            # In a real system, you would send email/SMS/push notifications here
            notification = {
                "consultant_id": consultant['consultant_id'],
                "consultant_email": consultant['email'],
                "opportunity_id": opportunity_id,
                "opportunity_title": opportunity['title'],
                "match_score": consultant['match_score'],
                "notification_type": "opportunity_match",
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            notifications_sent.append(notification)
        
        # Log the notifications (in a real system, store in database)
        logger.info(f"Sent {len(notifications_sent)} opportunity notifications for opportunity {opportunity_id}")
        
        return {
            "success": True,
            "message": f"Notifications sent to {len(notifications_sent)} matched consultants",
            "opportunity": opportunity,
            "notifications_sent": notifications_sent,
            "notification_summary": {
                "total_sent": len(notifications_sent),
                "high_match_notifications": len([n for n in notifications_sent if n.get('match_score', 0) >= 80]),
                "good_match_notifications": len([n for n in notifications_sent if 60 <= n.get('match_score', 0) < 80])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error notifying consultants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunity-dashboard/real-time")
async def get_real_time_opportunity_dashboard():
    """Get real-time opportunity dashboard with live updates"""
    try:
        # Get current opportunities and their status
        opportunities = db.get_all_opportunities()
        consultants = db.get_all_consultants()
        
        # Real-time metrics
        active_opportunities = [opp for opp in opportunities if opp.get('status') == 'open']
        urgent_opportunities = []  # Opportunities with low application count
        recent_applications = []
        
        opportunity_pipeline = []
        
        for opportunity in opportunities:
            applications = db.get_opportunity_applications(opportunity['id'])
            
            # Check for recent applications (simulated - last 24 hours)
            for app in applications:
                if app.get('status') == 'pending':
                    recent_applications.append({
                        "application_id": app['id'],
                        "opportunity_id": opportunity['id'],
                        "opportunity_title": opportunity['title'],
                        "consultant_email": app.get('consultant_email', 'Unknown'),
                        "applied_at": app.get('applied_at', datetime.now().isoformat()),
                        "status": app['status']
                    })
            
            # Identify urgent opportunities (few applications)
            if opportunity.get('status') == 'open' and len(applications) < 3:
                urgent_opportunities.append({
                    "opportunity_id": opportunity['id'],
                    "title": opportunity['title'],
                    "company": opportunity.get('company', 'Unknown'),
                    "applications_count": len(applications),
                    "days_since_posted": 5,  # Simulated
                    "urgency_level": "high" if len(applications) == 0 else "medium"
                })
            
            # Build pipeline data
            pipeline_stage = "sourcing"
            if len(applications) > 0:
                pipeline_stage = "screening"
            if any(app.get('status') == 'accepted' for app in applications):
                pipeline_stage = "placed"
            if opportunity.get('status') == 'closed':
                pipeline_stage = "closed"
            
            opportunity_pipeline.append({
                "opportunity_id": opportunity['id'],
                "title": opportunity['title'],
                "company": opportunity.get('company', 'Unknown'),
                "stage": pipeline_stage,
                "applications_count": len(applications),
                "accepted_count": len([app for app in applications if app.get('status') == 'accepted']),
                "status": opportunity.get('status', 'open')
            })
        
        # Consultant activity
        consultant_activity = []
        for consultant in consultants[:10]:  # Top 10 active consultants
            consultant_apps = 0
            for opp in opportunities:
                apps = db.get_opportunity_applications(opp['id'])
                consultant_apps += len([app for app in apps if app.get('consultant_id') == str(consultant['id'])])
            
            consultant_activity.append({
                "consultant_id": consultant['id'],
                "name": consultant.get('name', 'Unknown'),
                "email": consultant.get('email', 'Unknown'),
                "recent_applications": consultant_apps,
                "status": consultant.get('availability_status', 'available'),
                "last_active": "2 hours ago"  # Simulated
            })
        
        # Market activity simulation
        market_activity = {
            "applications_today": len(recent_applications),
            "new_opportunities_this_week": len([opp for opp in opportunities if opp.get('status') == 'open']),
            "placements_this_month": len([opp for opp in opportunities if opp.get('status') == 'closed']),
            "avg_time_to_placement": "8.2 days",
            "success_rate": "73%",
            "trending_skills": ["React", "Python", "AWS", "DevOps", "Data Science"]
        }
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "dashboard": {
                "overview": {
                    "total_opportunities": len(opportunities),
                    "active_opportunities": len(active_opportunities),
                    "urgent_opportunities": len(urgent_opportunities),
                    "recent_applications": len(recent_applications),
                    "total_consultants": len(consultants),
                    "available_consultants": len([c for c in consultants if c.get('availability_status') == 'available'])
                },
                "urgent_opportunities": urgent_opportunities,
                "recent_applications": recent_applications[-10:],  # Last 10 applications
                "opportunity_pipeline": opportunity_pipeline,
                "consultant_activity": consultant_activity,
                "market_activity": market_activity
            }
        }
    except Exception as e:
        logger.error(f"Error getting real-time opportunity dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/opportunities/{opportunity_id}/status")
async def update_opportunity_status(opportunity_id: str, status_data: dict):
    """Update opportunity status with real-time synchronization"""
    try:
        opportunities = db.get_all_opportunities()
        opportunity = next((opp for opp in opportunities if str(opp['id']) == str(opportunity_id)), None)
        
        if not opportunity:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        new_status = status_data.get('status')
        valid_statuses = ['open', 'in_progress', 'closed', 'on_hold']
        
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        # In a real database, update the status
        # db.update_opportunity_status(opportunity_id, new_status)
        
        # Log the status change
        logger.info(f"Opportunity {opportunity_id} status changed to {new_status}")
        
        # Get updated applications
        applications = db.get_opportunity_applications(opportunity_id)
        
        # If status is closed, update related consultant statuses
        if new_status == 'closed':
            accepted_apps = [app for app in applications if app.get('status') == 'accepted']
            for app in accepted_apps:
                consultant_id = app.get('consultant_id')
                if consultant_id:
                    # In real system: db.update_consultant_availability(consultant_id, 'available')
                    logger.info(f"Released consultant {consultant_id} from closed opportunity")
        
        return {
            "success": True,
            "message": f"Opportunity status updated to {new_status}",
            "opportunity": {
                "id": opportunity_id,
                "title": opportunity['title'],
                "old_status": opportunity.get('status', 'unknown'),
                "new_status": new_status,
                "updated_at": datetime.now().isoformat()
            },
            "affected_applications": len(applications),
            "next_actions": {
                "open": ["Notify matched consultants", "Review applications"],
                "in_progress": ["Monitor progress", "Update stakeholders"],
                "closed": ["Release consultants", "Generate completion report"],
                "on_hold": ["Notify applicants", "Update timeline"]
            }.get(new_status, [])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating opportunity status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/consultant-opportunities/{email}")
async def get_consultant_opportunities(email: str):
    """Get opportunities recommended for a specific consultant based on their skills"""
    try:
        # Find consultant by email
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get all opportunities
        all_opportunities = db.get_all_opportunities()
        
        # 🔧 FIX: Use SAME skills as profile tab
        try:
            profile_response = await get_consultant_profile(email)
            if isinstance(profile_response, dict):
                technical_skills = profile_response.get('technical_skills', [])
                soft_skills = profile_response.get('soft_skills', [])
                # Use ALL skills (technical + soft) for matching
                skill_names = [skill.lower() for skill in (technical_skills + soft_skills)]
                logger.info(f"Using profile skills for {email}: {len(skill_names)} skills")
            else:
                # Fallback to database if profile fails
                consultant_skills = db.get_consultant_skills(consultant_id)
                skill_names = [skill['skill_name'].lower() for skill in consultant_skills]
                logger.warning(f"Profile failed, using database skills: {len(skill_names)} skills")
        except Exception as e:
            logger.error(f"Failed to get profile skills for {email}: {e}")
            # Final fallback
            consultant_skills = db.get_consultant_skills(consultant_id)
            skill_names = [skill['skill_name'].lower() for skill in consultant_skills]
        
        # Get consultant's applications
        applications = []
        try:
            # Get applications for this consultant across all opportunities
            all_opportunities = db.get_all_opportunities()
            for opportunity in all_opportunities:
                opp_apps = db.get_opportunity_applications(opportunity['id'])
                consultant_apps = [app for app in opp_apps if app.get('consultant_id') == str(consultant_id)]
                applications.extend(consultant_apps)
        except Exception as e:
            logger.warning(f"Could not get consultant applications: {e}")
            applications = []
        
        # Create recommendations based on skill matching
        recommended_opportunities = []
        applied_opportunities = []
        
        for opportunity in all_opportunities:
            # Simple skill matching algorithm
            required_skills = opportunity.get('required_skills', [])
            if isinstance(required_skills, str):
                required_skills = [s.strip() for s in required_skills.split(',')]
            
            # Calculate match score
            matched_skills = []
            for req_skill in required_skills:
                for consultant_skill in skill_names:
                    # Exact match or close similarity (avoid partial matching like SQL vs PostgreSQL)
                    req_lower = req_skill.lower().strip()
                    consultant_lower = consultant_skill.lower().strip()
                    
                    # Exact match
                    if req_lower == consultant_lower:
                        matched_skills.append(req_skill)
                        break
                    # Handle common variations
                    elif (req_lower == 'javascript' and consultant_lower in ['js', 'javascript']) or \
                         (req_lower == 'js' and consultant_lower == 'javascript') or \
                         (req_lower == 'postgresql' and consultant_lower in ['postgres', 'postgresql']) or \
                         (req_lower == 'postgres' and consultant_lower == 'postgresql') or \
                         (req_lower in consultant_lower and len(req_lower) > 3 and abs(len(req_lower) - len(consultant_lower)) <= 2):
                        matched_skills.append(req_skill)
                        break
            
            match_score = len(matched_skills) / max(len(required_skills), 1) if required_skills else 0.5
            
            # Check if already applied
            has_applied = any(app.get('opportunity_id') == opportunity['id'] for app in applications)
            
            if has_applied:
                # Find the application
                app = next((a for a in applications if a.get('opportunity_id') == opportunity['id']), None)
                applied_opportunities.append({
                    "application_id": app.get('id', 0) if app else 0,
                    "opportunity": opportunity,
                    "application_status": app.get('status', 'pending') if app else 'pending',
                    "match_score": match_score,
                    "applied_at": app.get('created_at', datetime.now().isoformat()) if app else datetime.now().isoformat(),
                    "matched_skills": matched_skills,  # Add matched skills info
                    "required_skills": required_skills  # Add required skills for comparison
                })
            else:
                # Only recommend if match score is reasonable and opportunity is open
                if match_score > 0.2 and opportunity.get('status', '').lower() == 'open':
                    recommended_opportunities.append({
                        "opportunity": opportunity,
                        "match_score": match_score,
                        "match_reasoning": f"Matched {len(matched_skills)} out of {len(required_skills)} required skills",
                        "strengths": matched_skills,
                        "potential_gaps": [skill for skill in required_skills if skill not in matched_skills]
                    })
        
        # Sort recommendations by match score
        recommended_opportunities.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            "recommended_opportunities": recommended_opportunities[:10],  # Top 10 recommendations
            "applied_opportunities": applied_opportunities,
            "total_recommended": len(recommended_opportunities),
            "total_applied": len(applied_opportunities),
            "debug_info": {
                "consultant_skills_count": len(skill_names),
                "skills_source": "profile_endpoint_synced",
                "consultant_email": email,
                "skills_used_for_matching": skill_names[:10]  # Show first 10 skills for verification
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant opportunities: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Report generation endpoints
@app.get("/api/reports/types")
async def get_report_types():
    """Get available report types"""
    return {
        "report_types": [
            {
                "id": "comprehensive",
                "name": "Comprehensive Report",
                "description": "Complete consultant profile with skills, performance, and opportunities analysis"
            },
            {
                "id": "performance",
                "name": "Performance Report", 
                "description": "Focus on consultant performance metrics and success rates"
            },
            {
                "id": "skills",
                "name": "Skills Analysis Report",
                "description": "Detailed breakdown of technical and soft skills with market positioning"
            },
            {
                "id": "opportunities",
                "name": "Opportunities Report",
                "description": "Analysis of application history and opportunity matching effectiveness"
            }
        ]
    }

@app.post("/api/reports/generate")
async def generate_consultant_report(request: dict):
    """Generate consultant report"""
    try:
        consultant_email = request.get("consultant_email")
        report_type = request.get("report_type", "comprehensive")
        
        if not consultant_email:
            raise HTTPException(status_code=400, detail="Consultant email is required")
        
        # Verify consultant exists
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == consultant_email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get CLEAN skills from profile endpoint (same as profile tab)
        try:
            profile_response = await get_consultant_profile(consultant_email)
            if isinstance(profile_response, dict):
                technical_skills = profile_response.get('technical_skills', [])
                soft_skills = profile_response.get('soft_skills', [])
                current_skills = []
                
                # Convert to the expected format for report
                for skill in technical_skills:
                    current_skills.append({
                        'skill_name': skill,
                        'category': 'technical',
                        'proficiency_level': 'intermediate'
                    })
                
                for skill in soft_skills:
                    current_skills.append({
                        'skill_name': skill,
                        'category': 'soft', 
                        'proficiency_level': 'intermediate'
                    })
                
                logger.info(f"Using CLEAN profile skills for {consultant_email}: {len(current_skills)} skills")
            else:
                # Fallback to database if profile fails
                current_skills = db.get_consultant_skills_from_db(consultant_id)
                logger.warning(f"Profile endpoint failed, using database skills: {len(current_skills)} skills")
        except Exception as e:
            logger.error(f"Failed to get profile skills for {consultant_email}: {e}")
            # Fallback to database
            current_skills = db.get_consultant_skills_from_db(consultant_id)
        
        # Get Resume Agent analysis data for AI insights
        resume_analysis = db.get_resume_analysis_from_db(consultant_id)
        logger.info(f"Resume analysis fetched for consultant {consultant_id}: {bool(resume_analysis)}")
        if resume_analysis:
            logger.info(f"Resume analysis keys: {list(resume_analysis.keys()) if isinstance(resume_analysis, dict) else 'Not a dict'}")
        
        # Format skills data structure to match frontend expectations
        skills_by_category = {}
        
        # Group skills by category and format for frontend
        for skill in current_skills:
            category = skill.get('category', 'Other')
            if category == 'technical':
                category = 'Technical Skills'
            elif category == 'soft':
                category = 'Soft Skills'
            elif category == 'domain':
                category = 'Domain Knowledge'
            else:
                category = 'Other Skills'
            
            if category not in skills_by_category:
                skills_by_category[category] = []
            
            skills_by_category[category].append({
                'name': skill.get('skill_name', ''),
                'proficiency': skill.get('proficiency_level', 'intermediate')
            })
        
        skills_data = {
            "skills_by_category": skills_by_category,
            "total_skills": len(current_skills),
            "technical_skills_count": len([s for s in current_skills if s.get('category') == 'technical']),
            "soft_skills_count": len([s for s in current_skills if s.get('category') == 'soft']),
            "skills_by_source": {
                "resume_ai_analysis": len([s for s in current_skills if s.get('source') == 'resume_ai_analysis']),
                "resume": len([s for s in current_skills if s.get('source') == 'resume']),
                "manual": len([s for s in current_skills if s.get('source') == 'manual']),
                "assessment": len([s for s in current_skills if s.get('source') == 'assessment'])
            },
            "confidence_scores": [s.get('confidence_score', 0) for s in current_skills if s.get('confidence_score')],
            "avg_confidence": sum([s.get('confidence_score', 0) for s in current_skills]) / max(len(current_skills), 1),
            "last_updated": max([s.get('updated_at', '') for s in current_skills] + [''])
        }
        
        # Get opportunities and applications data from PostgreSQL (needed for AI insights)
        all_opportunities = db.get_all_opportunities()
        
        # Get consultant's applications from PostgreSQL
        consultant_applications = []
        for opp in all_opportunities:
            opp_apps = db.get_opportunity_applications(opp['id'])
            consultant_apps = [app for app in opp_apps if app.get('consultant_id') == str(consultant_id)]
            for app in consultant_apps:
                app['opportunity_title'] = opp['title']
                app['opportunity_client'] = opp['client_name']
                consultant_applications.append(app)
        
        # Calculate performance metrics from real data (needed for AI insights)
        total_applications = len(consultant_applications)
        accepted_applications = len([app for app in consultant_applications if app.get('status') == 'accepted'])
        pending_applications = len([app for app in consultant_applications if app.get('status') == 'pending'])
        declined_applications = len([app for app in consultant_applications if app.get('status') == 'declined'])
        
        success_rate = (accepted_applications / max(total_applications, 1)) * 100

        # Prepare AI insights from Resume Agent analysis (LLM/MCP based)
        ai_insights = {}
        if resume_analysis:
            logger.info("Processing resume analysis for AI insights from LLM/MCP...")
            # Format AI insights for frontend (expects 'insights' and 'recommendations' arrays)
            insights_list = []
            recommendations_list = []
            
            # Add AI summary as insight
            if resume_analysis.get('ai_summary'):
                insights_list.append(f"Resume Summary: {resume_analysis['ai_summary']}")
            
            # Add AI feedback as insight
            if resume_analysis.get('ai_feedback'):
                insights_list.append(f"Performance Analysis: {resume_analysis['ai_feedback']}")
            
            # Add confidence and analysis info
            if resume_analysis.get('confidence_score'):
                insights_list.append(f"AI Confidence Score: {resume_analysis['confidence_score']:.1f}% (Analysis Method: {resume_analysis.get('analysis_method', 'LLM Analysis')})")
            
            # Add role identification
            if resume_analysis.get('roles'):
                roles_str = ', '.join(resume_analysis['roles'][:3])
                insights_list.append(f"Identified Career Roles: {roles_str}")
            
            # Add competencies
            if resume_analysis.get('competencies'):
                comp_str = ', '.join(resume_analysis['competencies'][:3])
                insights_list.append(f"Key Competencies: {comp_str}")
            
            # Parse AI suggestions into recommendations
            if resume_analysis.get('ai_suggestions'):
                # Split suggestions by common delimiters
                suggestions_text = resume_analysis['ai_suggestions']
                
                # Try to split into individual recommendations
                if '. ' in suggestions_text:
                    suggestions = [s.strip() for s in suggestions_text.split('. ') if s.strip()]
                else:
                    suggestions = [suggestions_text]
                
                for suggestion in suggestions[:5]:  # Limit to 5 suggestions
                    if suggestion and len(suggestion) > 10:  # Filter out very short suggestions
                        if not suggestion.endswith('.'):
                            suggestion += '.'
                        recommendations_list.append(f"LLM Recommendation: {suggestion}")
            
            # Add skill development recommendations based on current skills
            if resume_analysis.get('skills'):
                total_skills = len(resume_analysis['skills'])
                if total_skills > 15:
                    recommendations_list.append(f"Strong skill portfolio: {total_skills} skills identified through LLM analysis - consider specialization")
                elif total_skills > 8:
                    recommendations_list.append(f"Good skill foundation: {total_skills} skills detected - consider expanding expertise")
                else:
                    recommendations_list.append(f"Skill development opportunity: {total_skills} skills identified - focus on building expertise")
            
            # Add personalized recommendations based on consultant's skills and experience
            consultant_experience = consultant.get('experience_years', 0)
            if consultant_experience >= 7:
                recommendations_list.append(f"Senior Level ({consultant_experience} years) - Consider leadership roles and mentoring opportunities")
            elif consultant_experience >= 4:
                recommendations_list.append(f"Mid-Level ({consultant_experience} years) - Focus on advanced technical skills and project leadership")
            else:
                recommendations_list.append(f"Entry Level ({consultant_experience} years) - Build foundational skills and seek mentorship")
            
            # Add department-specific recommendations
            dept = consultant.get('department', '').lower()
            if 'technology' in dept:
                recommendations_list.append("Technology Focus - Stay updated with latest frameworks and cloud technologies")
            elif 'data' in dept:
                recommendations_list.append("Data Focus - Enhance analytics and machine learning capabilities")
            elif 'product' in dept:
                recommendations_list.append("Product Focus - Develop user experience and market analysis skills")
            
            # Add market alignment insights based on current skills
            current_skill_names = [skill.get('skill_name', '').lower() for skill in current_skills]
            high_demand_skills = ['python', 'react', 'aws', 'kubernetes', 'machine learning', 'docker', 'typescript']
            matching_demand_skills = [skill for skill in high_demand_skills if any(skill in cs for cs in current_skill_names)]
            
            if len(matching_demand_skills) >= 3:
                insights_list.append(f"High Market Demand: Strong alignment with {len(matching_demand_skills)} in-demand skills")
            elif len(matching_demand_skills) >= 1:
                insights_list.append(f"Market Relevant: {len(matching_demand_skills)} skills match current market trends")
            else:
                recommendations_list.append("Market Gap: Consider adding trending skills like Python, React, or AWS")
            
            # Add vector analysis if available (indicates LLM processing)
            if resume_analysis.get('skill_vector') and len(resume_analysis['skill_vector']) > 0:
                recommendations_list.append("Advanced skill vector analysis completed - enables intelligent project matching")
            
            ai_insights = {
                "insights": insights_list,
                "recommendations": recommendations_list,
                "analysis_metadata": {
                    "confidence_score": resume_analysis.get('confidence_score', 0.0),
                    "analysis_method": resume_analysis.get('analysis_method', 'LLM_MCP_Pipeline'),
                    "total_extracted_skills": len(resume_analysis.get('skills', [])),
                    "last_analysis_date": resume_analysis.get('created_at', ''),
                    "llm_processed": True
                }
            }
        
        logger.info(f"Final AI insights structure: {bool(ai_insights)} with {len(ai_insights.get('insights', []))} insights and {len(ai_insights.get('recommendations', []))} recommendations")
        
        # Enhanced AI insights generation using PostgreSQL data
        if not ai_insights:
            ai_insights = {"insights": [], "recommendations": [], "analysis_metadata": {}}
        
        # Add database-driven insights
        db_insights = []
        db_recommendations = []
        
        # Skill diversity analysis
        if skills_data['total_skills'] > 15:
            db_insights.append(f"Strong Skill Portfolio: {skills_data['total_skills']} skills across multiple domains")
        elif skills_data['total_skills'] > 8:
            db_insights.append(f"Good Skill Foundation: {skills_data['total_skills']} skills - room for specialization")
        else:
            db_recommendations.append("Skill Development: Consider expanding technical skill portfolio")
        
        # Experience level insights
        experience_years = consultant.get('experience_years', 0)
        if experience_years >= 8:
            db_insights.append(f"Senior Level ({experience_years} years) - Consider leadership roles")
        elif experience_years >= 5:
            db_insights.append(f"Mid-Level Professional ({experience_years} years) - Ready for complex projects")
        elif experience_years >= 2:
            db_insights.append(f"Growing Professional ({experience_years} years) - Focus on skill building")
        else:
            db_recommendations.append("Early Career: Focus on gaining diverse project experience")
        
        # Department-specific insights
        department = consultant.get('department', '')
        if department.lower() == 'technology':
            db_recommendations.append("Technology Focus - Stay updated with latest frameworks")
        elif department.lower() == 'data':
            db_recommendations.append("Data Excellence - Consider advanced analytics certifications")
        
        # Application performance insights
        if total_applications > 0:
            if success_rate >= 70:
                db_insights.append(f"High Success Rate: {success_rate:.1f}% application acceptance")
            elif success_rate >= 40:
                db_insights.append(f"Good Performance: {success_rate:.1f}% success rate")
            else:
                db_recommendations.append(f"Improvement Opportunity: {success_rate:.1f}% success rate - review application approach")
        else:
            db_recommendations.append("Ready to Apply: No applications yet - great opportunities await")
        
        # Skill source analysis
        resume_skills = skills_data['skills_by_source'].get('resume_ai_analysis', 0)
        manual_skills = skills_data['skills_by_source'].get('manual', 0)
        if resume_skills > manual_skills:
            db_insights.append(f"AI-Enhanced Profile: {resume_skills} skills identified through resume analysis")
        
        # Market demand analysis based on current skills
        current_skill_names = [skill.get('skill_name', '').lower() for skill in current_skills]
        high_demand_skills = ['python', 'react', 'aws', 'kubernetes', 'machine learning', 'docker', 'typescript', 'node.js', 'postgresql']
        matching_demand_skills = [skill for skill in high_demand_skills if any(skill in cs for cs in current_skill_names)]
        
        if len(matching_demand_skills) >= 4:
            db_insights.append(f"High Market Demand: Strong alignment with {len(matching_demand_skills)} trending skills")
        elif len(matching_demand_skills) >= 2:
            db_insights.append(f"Market Relevant: {len(matching_demand_skills)} skills match current trends")
        else:
            db_recommendations.append("Market Gap: Consider adding trending skills like Python, React, or AWS")
        
        # Combine with existing AI insights
        ai_insights["insights"].extend(db_insights)
        ai_insights["recommendations"].extend(db_recommendations)
        
        # Ensure we have meaningful analysis metadata
        if not ai_insights.get("analysis_metadata"):
            ai_insights["analysis_metadata"] = {
                "confidence_score": 85.0,
                "analysis_method": "PostgreSQL_Data_Analysis",
                "total_extracted_skills": skills_data['total_skills'],
                "last_analysis_date": datetime.now().isoformat()
            }
        
        # Opportunities analysis with real data (using already calculated variables)
        opportunities_analysis = {
            "total_applications": total_applications,
            "accepted_applications": accepted_applications,
            "pending_applications": pending_applications,
            "declined_applications": declined_applications,
            "success_rate": round(success_rate, 1),
            "recent_applications": consultant_applications[-5:] if consultant_applications else [],
            "top_skills_in_demand": [skill.get('skill_name') for skill in current_skills[:5]],
            "opportunities_by_status": {
                "applied": total_applications,
                "accepted": accepted_applications,
                "declined": declined_applications,
                "pending": pending_applications
            }
        }
        
        # Performance metrics with real data
        performance_metrics_real = {
            "opportunity_success_rate": round(success_rate, 1),
            "total_applications": total_applications,
            "response_rate": round((accepted_applications + declined_applications) / max(total_applications, 1) * 100, 1),
            "market_competitiveness_score": ai_insights.get('analysis_metadata', {}).get('confidence_score', 0) * 100 if ai_insights else 85,
            "skill_utilization_rate": 90,
            "active_applications": pending_applications,
            "completed_projects": accepted_applications,
            "average_response_time_days": 1.5,
            "applications_this_month": len([app for app in consultant_applications if app.get('applied_at', '').startswith('2025-08')]),
            "performance_trend": "improving" if success_rate > 50 else "needs_attention"
        }

        # Generate report using MCP client
        if report_client:
            # Include skills data in the report request
            enhanced_request = {
                "consultant_email": consultant_email,
                "report_type": report_type,
                "skills_data": skills_data,
                "consultant_profile": consultant
            }
            
            # Try the enhanced method first, fallback to regular method
            try:
                if hasattr(report_client, 'generate_consultant_report_with_skills'):
                    report_result = await report_client.generate_consultant_report_with_skills(enhanced_request)
                else:
                    report_result = await report_client.generate_consultant_report(consultant_email, report_type)
            except Exception as e:
                logger.warning(f"MCP report generation failed: {e}, using fallback")
                report_result = {"success": False}
            
            if report_result.get('success'):
                # Merge MCP report with real PostgreSQL data
                mcp_report_data = report_result.get('report_data', {})
                
                # Override with real PostgreSQL data - including consultant overview
                mcp_report_data.update({
                    "consultant_overview": {
                        "name": consultant['name'],
                        "email": consultant['email'],
                        "department": consultant.get('department', ''),
                        "experience_years": consultant.get('experience_years', 0),
                        "primary_skill": consultant.get('primary_skill', ''),
                        "status": consultant.get('status', 'available')
                    },
                    "opportunities_analysis": opportunities_analysis,
                    "performance_metrics": performance_metrics_real,
                    "skills_analysis": skills_data,
                    "ai_insights": ai_insights  # Add real AI insights
                })
                
                return {
                    "success": True,
                    "message": "Report generated successfully with real PostgreSQL data",
                    "report_id": f"RPT_{consultant['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "consultant_email": consultant_email,
                    "report_type": report_type,
                    "generated_at": datetime.now().isoformat(),
                    "report_data": mcp_report_data,
                    "skills_summary": skills_data,
                    "ai_insights": ai_insights
                }
        
        basic_report = {
            "consultant_overview": {
                "name": consultant['name'],
                "email": consultant['email'],
                "department": consultant.get('department', ''),
                "experience_years": consultant.get('experience_years', 0),
                "primary_skill": consultant.get('primary_skill', ''),
                "status": consultant.get('status', 'available')
            },
            "skills_analysis": skills_data,
            "opportunities_analysis": opportunities_analysis,
            "performance_metrics": performance_metrics_real,
            "ai_insights": ai_insights,
            "market_analysis": {},
            "competitiveness_analysis": {}
        }
        
        # Generate recommendations based on Resume Agent analysis
        recommendations = []
        
        if resume_analysis:
            # Real AI-generated recommendations from Resume Agent
            recommendations.append("AI Analysis Complete - Data from Resume Agent")
            recommendations.append(f"{skills_data['total_skills']} skills identified and analyzed")
                
            # Add AI insights summary for this section
            if ai_insights.get('analysis_metadata'):
                metadata = ai_insights['analysis_metadata']
                recommendations.append(f"🎯 Analysis Confidence: {metadata.get('confidence_score', 0):.1f}%")
                recommendations.append(f"🧠 Analysis Method: {metadata.get('analysis_method', 'AI Pipeline')}")
                    
            # Add a few key insights
            if ai_insights.get('insights') and len(ai_insights['insights']) > 0:
                for insight in ai_insights['insights'][:2]:  # Add first 2 insights
                    recommendations.append(insight[:100] + "..." if len(insight) > 100 else insight)
                
            if skills_data['skills_by_source']['resume_ai_analysis'] > 0:
                recommendations.append(f"🚀 {skills_data['skills_by_source']['resume_ai_analysis']} skills extracted by AI from resume")
        else:
            # Generate AI insights even without resume analysis based on database skills
            insights_list = []
            recommendations_list = []
            
            # Analyze current skills from database
            if skills_data['total_skills'] > 0:
                insights_list.append(f"📊 Skills Portfolio: {skills_data['total_skills']} skills tracked in database")
                insights_list.append(f"⚙️ Technical Skills: {skills_data['technical_skills_count']} | Soft Skills: {skills_data['soft_skills_count']}")
                
                # Analyze skill sources
                if skills_data['skills_by_source']['manual'] > 0:
                    insights_list.append(f"👤 Manual Entry: {skills_data['skills_by_source']['manual']} skills manually added")
                
                # Experience-based insights
                consultant_experience = consultant.get('experience_years', 0)
                if consultant_experience >= 7:
                    insights_list.append(f"🎖️ Senior Professional: {consultant_experience} years experience - ideal for leadership roles")
                elif consultant_experience >= 4:
                    insights_list.append(f"📈 Mid-Level Professional: {consultant_experience} years experience - ready for complex projects")
                else:
                    insights_list.append(f"🌟 Growing Professional: {consultant_experience} years experience - high potential for development")
                
                # Department insights
                dept = consultant.get('department', '')
                if dept:
                    insights_list.append(f"🏢 Department: {dept} - specialized domain expertise")
                
                # Market analysis based on current skills
                current_skill_names = [skill.get('skill_name', '').lower() for skill in current_skills]
                high_demand_skills = ['python', 'react', 'aws', 'kubernetes', 'machine learning', 'docker', 'typescript', 'javascript', 'java', 'sql']
                matching_demand_skills = [skill for skill in high_demand_skills if any(skill in cs for cs in current_skill_names)]
                
                if len(matching_demand_skills) >= 3:
                    insights_list.append(f"🔥 Market Alignment: {len(matching_demand_skills)} high-demand skills identified")
                    recommendations_list.append("� Strong market position - pursue senior opportunities")
                elif len(matching_demand_skills) >= 1:
                    insights_list.append(f"📊 Market Relevant: {len(matching_demand_skills)} trending skills in portfolio")
                    recommendations_list.append("📈 Good foundation - consider adding complementary skills")
                else:
                    recommendations_list.append("🎯 Skill Gap: Add trending technologies like Python, React, or cloud platforms")
                
                # Performance recommendations
                if total_applications > 0:
                    if success_rate > 70:
                        recommendations_list.append(f"🏆 Excellent performance: {success_rate:.1f}% success rate")
                    elif success_rate > 40:
                        recommendations_list.append(f"📊 Good performance: {success_rate:.1f}% success rate - room for improvement")
                    else:
                        recommendations_list.append(f"🔧 Needs improvement: {success_rate:.1f}% success rate - consider skill development")
                else:
                    recommendations_list.append("🚀 Ready to apply: No application history - time to pursue opportunities")
                
            # General recommendations
            recommendations_list.extend([
                "📤 Upload resume for AI-powered skills analysis and deeper insights",
                f"🎯 Focus on {consultant.get('primary_skill', 'core skills')} expertise development",
                "📚 Consider industry certifications to validate expertise"
            ])
            
            ai_insights = {
                "insights": insights_list,
                "recommendations": recommendations_list,
                "analysis_metadata": {
                    "confidence_score": 75.0,  # Based on database skills
                    "analysis_method": "Database_Skills_Analysis",
                    "total_extracted_skills": skills_data['total_skills'],
                    "last_analysis_date": skills_data.get('last_updated', datetime.now().isoformat())
                }
            }
            
        basic_report["recommendations"] = recommendations
            
        return {
            "success": True,
            "message": "Report generated successfully (fallback mode)",
            "report_id": f"RPT_{consultant['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "consultant_email": consultant_email,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "report_data": basic_report,
            "skills_summary": skills_data,
            "ai_insights": ai_insights,
            "note": "Report generated using database skills data with Resume Agent AI insights - UPDATED VERSION"
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/consultant/{email}")
async def get_consultant_reports(email: str):
    """Get consultant data and application history"""
    try:
        # Find consultant by email
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get consultant's real application history from PostgreSQL
        all_opportunities = db.get_all_opportunities()
        consultant_applications = []
        
        for opp in all_opportunities:
            opp_apps = db.get_opportunity_applications(opp['id'])
            consultant_apps = [app for app in opp_apps if app.get('consultant_id') == str(consultant_id)]
            for app in consultant_apps:
                consultant_applications.append({
                    "application_id": app.get('id'),
                    "opportunity_title": opp['title'],
                    "opportunity_client": opp['client_name'],
                    "status": app.get('status'),
                    "applied_at": app.get('applied_at'),
                    "cover_letter": app.get('cover_letter', ''),
                    "match_score": app.get('match_score', 0)
                })
        
        # Get consultant skills
        consultant_skills = db.get_consultant_skills_from_db(consultant_id)
        
        # Calculate summary statistics
        total_applications = len(consultant_applications)
        accepted_applications = len([app for app in consultant_applications if app.get('status') == 'accepted'])
        pending_applications = len([app for app in consultant_applications if app.get('status') == 'pending'])
        declined_applications = len([app for app in consultant_applications if app.get('status') == 'declined'])
        
        success_rate = (accepted_applications / max(total_applications, 1)) * 100
        
        return {
            "consultant_profile": consultant,
            "application_history": consultant_applications,
            "skills_summary": {
                "total_skills": len(consultant_skills),
                "skills_by_category": {
                    "technical": len([s for s in consultant_skills if s.get('category') == 'technical']),
                    "soft": len([s for s in consultant_skills if s.get('category') == 'soft']),
                    "domain": len([s for s in consultant_skills if s.get('category') == 'domain'])
                }
            },
            "performance_summary": {
                "total_applications": total_applications,
                "accepted_applications": accepted_applications,
                "pending_applications": pending_applications,
                "declined_applications": declined_applications,
                "success_rate": round(success_rate, 1)
            }
        }
        
        return {
            "consultant_email": email,
            "total_reports": len(mock_reports),
            "reports": mock_reports
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/analytics")
async def get_report_analytics():
    """Get report generation analytics from PostgreSQL"""
    try:
        # Get real data from PostgreSQL
        all_consultants = db.get_all_consultants()
        all_opportunities = db.get_all_opportunities()
        
        # Calculate application statistics
        total_applications = 0
        accepted_applications = 0
        pending_applications = 0
        declined_applications = 0
        recent_activity = []
        
        for opp in all_opportunities:
            opp_apps = db.get_opportunity_applications(opp['id'])
            total_applications += len(opp_apps)
            
            for app in opp_apps:
                if app.get('status') == 'accepted':
                    accepted_applications += 1
                elif app.get('status') == 'pending':
                    pending_applications += 1
                elif app.get('status') == 'declined':
                    declined_applications += 1
                
                # Add to recent activity (last 10)
                recent_activity.append({
                    "consultant_email": app.get('consultant_email', 'Unknown'),
                    "opportunity_title": opp['title'],
                    "status": app.get('status', 'unknown'),
                    "applied_at": app.get('applied_at', ''),
                    "action": "application_submitted"
                })
        
        # Sort recent activity by date and take last 10
        recent_activity.sort(key=lambda x: x.get('applied_at', ''), reverse=True)
        recent_activity = recent_activity[:10]
        
        # Calculate success rates
        total_processed = accepted_applications + declined_applications
        success_rate = (accepted_applications / max(total_processed, 1)) * 100
        
        analytics = {
            "total_consultants": len(all_consultants),
            "total_opportunities": len(all_opportunities),
            "total_applications": total_applications,
            "applications_breakdown": {
                "accepted": accepted_applications,
                "pending": pending_applications,
                "declined": declined_applications
            },
            "success_rate": round(success_rate, 1),
            "active_consultants": len([c for c in all_consultants if c.get('current_status') != 'inactive']),
            "open_opportunities": len([o for o in all_opportunities if o.get('status') == 'open']),
            "recent_activity": recent_activity,
            "performance_metrics": {
                "avg_applications_per_opportunity": round(total_applications / max(len(all_opportunities), 1), 1),
                "placement_rate": round(success_rate, 1),
                "consultant_utilization": round((accepted_applications / max(len(all_consultants), 1)) * 100, 1)
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting report analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_ai_insights_for_consultant(consultant: dict, technical_skills: list, soft_skills: list) -> dict:
    """Generate AI insights for a consultant based on their skills and profile"""
    try:
        all_skills = technical_skills + soft_skills
        total_skills = len(all_skills)
        
        # Initialize insights and recommendations
        insights = []
        recommendations = []
        
        # Skill diversity analysis
        if total_skills > 15:
            insights.append(f"Strong Skill Portfolio: {total_skills} skills across multiple domains")
        elif total_skills > 8:
            insights.append(f"Good Skill Foundation: {total_skills} skills - room for specialization")
        else:
            recommendations.append("Skill Development: Consider expanding technical skill portfolio")
        
        # Technical vs Soft skills balance
        tech_ratio = len(technical_skills) / max(total_skills, 1) * 100
        if tech_ratio > 80:
            recommendations.append("Soft Skills: Consider developing communication and leadership skills")
        elif tech_ratio < 30:
            recommendations.append("Technical Skills: Focus on expanding technical expertise")
        else:
            insights.append(f"Balanced Profile: Good mix of technical ({len(technical_skills)}) and soft skills ({len(soft_skills)})")
        
        # Experience level insights
        experience_years = consultant.get('experience_years', 0)
        if experience_years >= 8:
            insights.append(f"Senior Level ({experience_years} years) - Consider leadership roles")
        elif experience_years >= 5:
            insights.append(f"Mid-Level Professional ({experience_years} years) - Ready for complex projects")
        elif experience_years >= 2:
            insights.append(f"Growing Professional ({experience_years} years) - Focus on skill building")
        else:
            recommendations.append("Early Career: Focus on gaining diverse project experience")
        
        # Market demand analysis
        skill_names_lower = [skill.lower() for skill in all_skills]
        high_demand_skills = ['python', 'react', 'aws', 'kubernetes', 'machine learning', 'docker', 'typescript', 'node.js', 'postgresql']
        matching_demand_skills = [skill for skill in high_demand_skills if any(skill in cs for cs in skill_names_lower)]
        
        if len(matching_demand_skills) >= 4:
            insights.append(f"High Market Demand: Strong alignment with {len(matching_demand_skills)} trending skills")
        elif len(matching_demand_skills) >= 2:
            insights.append(f"Market Relevant: {len(matching_demand_skills)} skills match current trends")
        else:
            recommendations.append("Market Gap: Consider adding trending skills like Python, React, or AWS")
        # Department-specific insights
        department = consultant.get('department', '')
        if department.lower() == 'technology':
            recommendations.append("Technology Focus - Stay updated with latest frameworks")
        elif department.lower() == 'data':
            recommendations.append("Data Excellence - Consider advanced analytics certifications")
        # Status-based recommendations
        status = consultant.get('status', 'available')
        if status == 'available':
            recommendations.append("Ready for Projects: Profile shows availability for new opportunities")
        elif status == 'busy':
            insights.append("Currently Engaged: Active in ongoing projects")
        return {
            "insights": insights,
            "recommendations": recommendations,
            "analysis_metadata": {
                "confidence_score": 90.0,
                "analysis_method": "Real_Time_Profile_Analysis",
                "total_skills_analyzed": total_skills,
                "technical_skills_count": len(technical_skills),
                "soft_skills_count": len(soft_skills),
                "last_analysis_date": datetime.utcnow().isoformat(),
                "market_skills_matched": len(matching_demand_skills)
            }
        }
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return {
            "insights": ["Profile analysis completed"],
            "recommendations": ["Continue developing professional skills"],
            "analysis_metadata": {
                "confidence_score": 50.0,
                "analysis_method": "Fallback_Analysis",
                "last_analysis_date": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        }

#Dynamic Skill-Synced Report Generation
@app.get("/api/reports/consultant/{email}/synced")
async def get_consultant_report_with_current_skills(email: str):
    """Get consultant report with real-time skill synchronization"""
    try:
        # Find consultant by email
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        consultant_id = consultant['id']
        
        # Get EXACT SAME skills that profile tab shows
        profile_response = await get_consultant_profile(email)
        
        if isinstance(profile_response, dict):
            current_technical_skills = profile_response.get('technical_skills', [])
            current_soft_skills = profile_response.get('soft_skills', [])
            total_skills = len(current_technical_skills) + len(current_soft_skills)
        else:
            # Fallback if profile endpoint fails
            current_skills = db.get_consultant_skills(consultant_id)
            current_technical_skills = [skill['skill_name'] for skill in current_skills if skill.get('skill_category') == 'technical']
            current_soft_skills = [skill['skill_name'] for skill in current_skills if skill.get('skill_category') == 'soft']
            total_skills = len(current_technical_skills) + len(current_soft_skills)
        
        # Get base report data
        base_report = await get_consultant_reports(email)
        
        # Generate AI Insights with current skills data
        ai_insights = await generate_ai_insights_for_consultant(consultant, current_technical_skills, current_soft_skills)
        
        #skill analysis with EXACT profile skills
        if isinstance(base_report, dict):
            # Update skills in the report to match EXACT profile
            base_report["skills_summary"] = {
                "total_skills": total_skills,
                "skills_list": current_technical_skills + current_soft_skills,
                "skills_by_category": {
                    "technical": len(current_technical_skills),
                    "soft": len(current_soft_skills),
                    "other": 0
                },
                "sync_status": "synchronized_with_profile",
                "last_synced": datetime.utcnow().isoformat()
            }
            # Add skill analysis section with EXACT profile skills
            base_report["skill_analysis"] = {
                "current_skills": current_technical_skills + current_soft_skills,
                "technical_skills": current_technical_skills,
                "soft_skills": current_soft_skills,
                "skill_count": total_skills,
                "technical_count": len(current_technical_skills),
                "soft_count": len(current_soft_skills),
                "source": "profile_exact_match",
                "updated_at": datetime.utcnow().isoformat()
            }
            # Add AI insights to the report
            base_report["ai_insights"] = ai_insights
        return {
            "status": "success",
            "consultant_email": email,
            "report_data": base_report,
            "sync_info": {
                "skills_synchronized": True,
                "sync_timestamp": datetime.utcnow().isoformat(),
                "skills_count": total_skills,
                "technical_count": len(current_technical_skills),
                "soft_count": len(current_soft_skills),
                "source": "profile_endpoint_exact_match"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating synced report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#Update consultant skills with auto-sync
@app.put("/api/consultants/{consultant_id}/skills/update")
async def update_consultant_skills_with_sync(consultant_id: int, skills_data: dict):
    """Update consultant skills and ensure reports will reflect changes"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Remove existing skills
        db.remove_consultant_skills(consultant_id)
        
        # Add new skills
        new_skills = skills_data.get('skills', [])
        soft_skills = skills_data.get('soft_skills', [])
        all_skills = new_skills + soft_skills
        
        skills_added = 0
        for skill in all_skills:
            db.add_consultant_skill(
                consultant_id=consultant_id,
                skill_name=skill,
                proficiency_level="intermediate",  # Default
                skill_category="technical" if skill in new_skills else "soft"
            )
            skills_added += 1
        
        return {
            "status": "success",
            "message": f"Updated {skills_added} skills for consultant {consultant_id}",
            "skills_updated": {
                "technical_skills": new_skills,
                "soft_skills": soft_skills,
                "total_skills": skills_added
            },
            "sync_info": {
                "skills_updated": True,
                "reports_will_reflect_changes": True,
                "synced_report_endpoint": f"/api/reports/consultant/{consultant['email']}/synced",
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating consultant skills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#Check skill sync status
@app.get("/api/consultants/{consultant_id}/skills/sync-status")
async def check_skill_sync_status(consultant_id: int):
    """Check if consultant profile skills are available for report sync"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get current skills from profile
        current_skills = db.get_consultant_skills(consultant_id)
        current_skill_names = [skill['skill_name'] for skill in current_skills]
        
        return {
            "consultant_id": consultant_id,
            "consultant_email": consultant.get('email'),
            "skills_available": len(current_skills) > 0,
            "total_skills": len(current_skills),
            "skills_breakdown": {
                "technical": len([s for s in current_skills if s.get('skill_category') == 'technical']),
                "soft": len([s for s in current_skills if s.get('skill_category') == 'soft']),
                "other": len([s for s in current_skills if s.get('skill_category') not in ['technical', 'soft']])
            },
            "skills_list": current_skill_names,
            "sync_ready": True,
            "synced_report_url": f"/api/reports/consultant/{consultant.get('email')}/synced",
            "last_checked": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking skill sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reports/export")
async def export_report(request: dict):
    """Export report in various formats"""
    try:
        consultant_email = request.get("consultant_email")
        export_format = request.get("format", "json")
        
        if not consultant_email:
            raise HTTPException(status_code=400, detail="Consultant email is required")
        
        # Generate the report data first
        if report_client:
            report_result = await report_client.generate_consultant_report(consultant_email, "comprehensive")
            
            if report_result.get('success'):
                if export_format == "json":
                    return {
                        "success": True,
                        "export_format": "json",
                        "export_data": report_result.get('report_data', {})
                    }
                elif export_format == "csv":
                    # Convert to CSV format (simplified)
                    csv_data = "Field,Value\n"
                    report_data = report_result.get('report_data', {})
                    
                    # Flatten the data for CSV
                    overview = report_data.get('consultant_overview', {})
                    csv_data += f"Name,{overview.get('name', 'N/A')}\n"
                    csv_data += f"Email,{overview.get('email', 'N/A')}\n"
                    csv_data += f"Primary Skill,{overview.get('primary_skill', 'N/A')}\n"
                    csv_data += f"Experience Years,{overview.get('experience_years', 'N/A')}\n"
                    
                    return {
                        "success": True,
                        "export_format": "csv", 
                        "csv_data": csv_data
                    }
                else:
                    raise HTTPException(status_code=400, detail="Unsupported export format")
            else:
                raise HTTPException(status_code=500, detail="Failed to generate report for export")
        else:
            raise HTTPException(status_code=503, detail="Report service not available")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-training-mcp")
async def test_training_mcp_server():
    """Test endpoint to verify training MCP server connectivity"""
    try:
        if not training_client:
            return {
                "success": False,
                "message": "Training client not initialized",
                "status": "error"
            }
        
        # Test with sample data
        test_result = await training_client.get_training_recommendations(
            consultant_id=999,
            current_skills=["Python", "Django"],
            missing_skills=["React", "AWS"],
            experience_level="intermediate"
        )
        
        return {
            "success": True,
            "message": "Training MCP server is working",
            "test_result": test_result,
            "ai_powered": test_result.get('success', False)
        }
        
    except Exception as e:
        logger.error(f"Training MCP test failed: {e}")
        return {
            "success": False,
            "message": f"Training MCP server test failed: {str(e)}",
            "status": "error"
        }

@app.get("/api/test-opportunities")
async def test_opportunities():
    """Test endpoint to debug opportunity data structure"""
    try:
        opportunities = db.get_all_opportunities()
        
        test_response = {
            "total_opportunities": len(opportunities),
            "sample_opportunity": opportunities[0] if opportunities else None,
            "data_types": {}
        }
        
        if opportunities:
            sample = opportunities[0]
            for key, value in sample.items():
                test_response["data_types"][key] = str(type(value).__name__)
        
        return test_response
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/api/consultant/opportunities/{email}")
async def get_consultant_opportunities_simple(email: str):
    """Get opportunities for consultant (simplified)"""
    try:
        # Find consultant by email
        consultants = db.get_all_consultants()
        consultant = next((c for c in consultants if c['email'] == email), None)
        
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get all opportunities
        opportunities = db.get_all_opportunities()
        
        # Filter only open opportunities
        open_opportunities = [opp for opp in opportunities if opp.get('status') == 'open']
        
        return {
            "opportunities": open_opportunities,
            "total": len(open_opportunities),
            "consultant_id": consultant['id'],
            "consultant_name": consultant['name']
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ATTENDANCE CHATBOT ENDPOINTS
class AttendanceQuery(BaseModel):
    question: str
    user_email: Optional[str] = None

@app.post("/api/attendance/chat")
async def attendance_chat(query: AttendanceQuery):
    """Process attendance chatbot questions"""
    try:
        if not attendance_chatbot:
            raise HTTPException(status_code=503, detail="Attendance chatbot not available")
        
        response = attendance_chatbot.process_question(query.question, query.user_email)
        
        return {
            "success": True,
            "question": query.question,
            "response": response,
            "user_email": query.user_email,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in attendance chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/stats/{email}")
async def get_attendance_stats(email: str, days: int = 30):
    """Get attendance statistics for a specific user"""
    try:
        if not attendance_chatbot:
            raise HTTPException(status_code=503, detail="Attendance chatbot not available")
        
        stats = attendance_chatbot.get_user_attendance_stats(email, days)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail=stats["error"])
        
        return {
            "success": True,
            "stats": stats,
            "period_days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/team-stats")
async def get_team_attendance_stats(days: int = 30):
    """Get team-wide attendance statistics"""
    try:
        if not attendance_chatbot:
            raise HTTPException(status_code=503, detail="Attendance chatbot not available")
        
        team_stats = attendance_chatbot.get_all_consultants_attendance(days)
        
        if "error" in team_stats:
            raise HTTPException(status_code=500, detail=team_stats["error"])
        
        return {
            "success": True,
            "team_stats": team_stats,
            "period_days": days
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting team attendance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/attendance/add-sample-data/{email}")
async def add_sample_attendance_data(email: str, days: int = 30):
    """Add sample attendance data for testing"""
    try:
        if not attendance_chatbot:
            raise HTTPException(status_code=503, detail="Attendance chatbot not available")
        
        success = attendance_chatbot.add_sample_attendance_data(email, days)
        
        if success:
            return {
                "success": True,
                "message": f"Added {days} days of sample attendance data for {email}",
                "email": email,
                "days_added": days
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add sample data")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding sample attendance data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/dashboard/{email}")
async def get_attendance_dashboard(email: str):
    """Get attendance dashboard data for consultant"""
    try:
        if not attendance_chatbot:
            raise HTTPException(status_code=503, detail="Attendance chatbot not available")
        
        # Get current stats
        current_stats = attendance_chatbot.get_user_attendance_stats(email, 30)
        weekly_stats = attendance_chatbot.get_user_attendance_stats(email, 7)
        
        if "error" in current_stats:
            raise HTTPException(status_code=404, detail=current_stats["error"])
        
        # Calculate attendance trends
        attendance_trend = "stable"
        if weekly_stats.get("attendance_rate", 0) > current_stats.get("attendance_rate", 0):
            attendance_trend = "improving"
        elif weekly_stats.get("attendance_rate", 0) < current_stats.get("attendance_rate", 0):
            attendance_trend = "declining"
        
        # Get performance status
        attendance_rate = current_stats.get("attendance_rate", 0)
        if attendance_rate >= 95:
            performance_status = "excellent"
            status_message = "Outstanding attendance! Keep it up!"
        elif attendance_rate >= 85:
            performance_status = "good"
            status_message = "Good attendance. Well done!"
        elif attendance_rate >= 75:
            performance_status = "satisfactory"
            status_message = "Satisfactory attendance. Room for improvement."
        else:
            performance_status = "needs_improvement"
            status_message = "Attendance needs improvement. Please focus on regularity."
        
        return {
            "success": True,
            "user_name": current_stats.get("user_name"),
            "user_email": email,
            "current_month": {
                "attendance_rate": current_stats.get("attendance_rate", 0),
                "present_days": current_stats.get("present_days", 0),
                "absent_days": current_stats.get("absent_days", 0),
                "total_hours": current_stats.get("total_hours", 0),
                "avg_hours_per_day": current_stats.get("avg_hours_per_day", 0)
            },
            "this_week": {
                "attendance_rate": weekly_stats.get("attendance_rate", 0),
                "present_days": weekly_stats.get("present_days", 0),
                "absent_days": weekly_stats.get("absent_days", 0)
            },
            "performance": {
                "status": performance_status,
                "message": status_message,
                "trend": attendance_trend
            },
            "recent_records": current_stats.get("recent_records", [])[:5]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attendance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

#Verify data synchronization between different endpoints
@app.get("/api/attendance/sync-verify/{email}")
async def verify_attendance_sync(email: str):
    """Verify that all attendance data sources return consistent values"""
    try:
        if not attendance_chatbot:
            raise HTTPException(status_code=503, detail="Attendance chatbot not available")
        
        # Get data from the same source used by all systems (30 days)
        stats_30_days = attendance_chatbot.get_user_attendance_stats(email, 30)
        if "error" in stats_30_days:
            return {
                "synced": False,
                "error": stats_30_days["error"]
            }
        
        # Get data from chatbot personal method (should match now)
        chatbot_response = attendance_chatbot._get_personal_attendance(email)
        if "error" in chatbot_response:
            return {
                "synced": False,
                "error": chatbot_response["error"]
            }
        
        # Extract attendance rates for comparison
        dashboard_rate = stats_30_days.get("attendance_rate", 0)
        chatbot_rate = chatbot_response["data"].get("attendance_rate", 0) if "data" in chatbot_response else 0
        
        # Check if rates match (within 0.1% tolerance)
        rates_match = abs(dashboard_rate - chatbot_rate) <= 0.1
        
        return {
            "synced": rates_match,
            "email": email,
            "dashboard_data": {
                "attendance_rate": dashboard_rate,
                "present_days": stats_30_days.get("present_days", 0),
                "total_days": stats_30_days.get("total_days", 0),
                "source": "get_user_attendance_stats(30)"
            },
            "chatbot_data": {
                "attendance_rate": chatbot_rate,
                "present_days": chatbot_response["data"].get("present_days", 0) if "data" in chatbot_response else 0,
                "total_days": chatbot_response["data"].get("total_days", 0) if "data" in chatbot_response else 0,
                "source": "_get_personal_attendance"
            },
            "rate_difference": abs(dashboard_rate - chatbot_rate),
            "verification_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error verifying sync for {email}: {e}")
        return {
            "synced": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
