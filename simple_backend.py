#!/usr/bin/env python3
"""
Professional Bench Tracking System - Backend API
Enhanced with AI-powered skill analysis and training recommendations
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import uvicorn

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import database models and connections
try:
    from database.professional_connection import ProfessionalDatabase
    from database.models.professional_models import (
        Consultant, ConsultantSkill, Opportunity, Training, 
        Attendance, Report, OpportunitySkillGap
    )
    from utils.resume_analyzer_interface import ResumeAnalyzerMCPClient
    from utils.training_interface import TrainingMCPClient
    logger.info("Successfully imported all dependencies")
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error(traceback.format_exc())

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

# Initialize AI clients
resume_analyzer = ResumeAnalyzerMCPClient()
training_client = TrainingMCPClient()

# Pydantic models for API
class ConsultantCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    experience_years: int
    department: str
    primary_skill: str
    skills: List[str] = []
    soft_skills: List[str] = []
    availability_status: str = "available"
    status: str = "active"
    attendance_rate: float = 100.0
    training_status: str = "not-started"

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
    title: str
    company: str
    client_name: str
    description: str
    required_skills: List[str]
    experience_required: int
    location: str
    status: str = "open"

class ApplicationCreate(BaseModel):
    consultant_id: int
    consultant_email: str

class ApplicationUpdate(BaseModel):
    status: str  # 'accepted' or 'declined'

class SkillsAnalysisResponse(BaseModel):
    ai_summary: str
    skills: List[str]
    competencies: List[str]
    ai_feedback: str
    ai_suggestions: str
    confidence_score: float

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
            "reportsGenerated": 0,  # Will be updated with actual reports
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
            # Get skills
            skills = db.get_consultant_skills(consultant['id'])
            
            # Get active assignments (opportunities)
            assignments = db.get_consultant_assignments(consultant['id'])
            
            enhanced_consultant = {
                **consultant,
                'skills': [skill['skill_name'] for skill in skills],
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
                skill_type="technical" if skill in consultant_data.skills else "soft"
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
                    skill_type="technical" if skill in (consultant_data.skills or []) else "soft"
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
        
        # Get consultant assignments and opportunities
        assignments = db.get_consultant_assignments(consultant['id'])
        opportunities = db.get_all_opportunities()
        
        # Calculate metrics
        opportunities_count = len([o for o in opportunities if o.get('status') == 'open'])
        
        return {
            "consultant_id": consultant['id'],
            "name": consultant['name'],
            "email": consultant['email'],
            "resume_status": "updated" if consultant.get('resume_uploaded') else "not updated",
            "attendance_rate": consultant.get('attendance_rate', 85),
            "opportunities_count": opportunities_count,
            "training_progress": consultant.get('training_status', 'not-started'),
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
                    "completed": consultant.get('attendance_rate', 0) > 80,
                    "inProgress": False
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
                    "completed": consultant.get('training_status') == 'completed',
                    "inProgress": consultant.get('training_status') == 'in-progress'
                }
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting consultant dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resume upload and analysis
@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    consultant_email: str = Form(...)
):
    """Upload and analyze resume with AI"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
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
        
        # Analyze resume with AI
        try:
            analysis_result = resume_analyzer.analyze_resume(str(file_path))
            
            if analysis_result.get('success'):
                skills = analysis_result.get('skills', [])
                ai_summary = analysis_result.get('ai_summary', '')
                
                # Update consultant with AI analysis
                db.update_consultant(
                    consultant['id'],
                    resume_uploaded=True,
                    ai_summary=ai_summary
                )
                
                # Update skills
                db.remove_consultant_skills(consultant['id'])
                for skill in skills:
                    db.add_consultant_skill(
                        consultant_id=consultant['id'],
                        skill_name=skill,
                        proficiency_level="intermediate",
                        skill_type="technical"
                    )
                
                return {
                    "message": "Resume uploaded and analyzed successfully",
                    "analysis": {
                        "skills": skills,
                        "ai_summary": ai_summary,
                        "total_skills": len(skills)
                    }
                }
            else:
                # Fallback: just save the file
                db.update_consultant(consultant['id'], resume_uploaded=True)
                return {
                    "message": "Resume uploaded successfully (analysis unavailable)",
                    "analysis": {"skills": [], "ai_summary": "Analysis not available"}
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
        
        # Get skills
        skills = db.get_consultant_skills(consultant_id)
        skill_names = [skill['skill_name'] for skill in skills]
        
        # Get AI summary
        ai_summary = consultant.get('ai_summary', 'No AI analysis available')
        
        return {
            "ai_summary": ai_summary,
            "skills": skill_names,
            "competencies": [skill['skill_name'] for skill in skills if skill.get('skill_type') == 'soft'],
            "ai_feedback": f"Analysis complete. Found {len(skill_names)} skills.",
            "ai_suggestions": "Continue developing your technical skills and consider adding certifications.",
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
    """Get comprehensive training dashboard with AI recommendations"""
    try:
        consultant = db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Get current enrollments
        training_enrollments = db.get_consultant_training(consultant_id)
        
        # Get opportunities and skill gaps for recommendations
        opportunities = db.get_all_opportunities()
        consultant_skills = db.get_consultant_skills(consultant_id)
        consultant_skill_names = [skill['skill_name'].lower() for skill in consultant_skills]
        
        # Analyze skill gaps
        missing_skills = []
        training_recommendations = []
        
        for opportunity in opportunities:
            if opportunity.get('status') == 'open':
                required_skills = opportunity.get('required_skills', [])
                opportunity_missing_skills = [
                    skill for skill in required_skills 
                    if skill.lower() not in consultant_skill_names
                ]
                
                for missing_skill in opportunity_missing_skills:
                    if not any(gap['skill'].lower() == missing_skill.lower() for gap in missing_skills):
                        missing_skills.append({
                            'skill': missing_skill,
                            'opportunities': [opportunity['title']],
                            'priority': 'High'
                        })
                        
                        # Add training recommendation
                        training_recommendations.append({
                            'name': f"{missing_skill} Fundamentals",
                            'priority': 'High',
                            'reason': f"Required for {opportunity['title']} and similar opportunities",
                            'missing_skill': missing_skill,
                            'opportunities_count': 1,
                            'sample_opportunities': [opportunity['title']]
                        })
        
        return {
            "current_enrollments": training_enrollments,
            "opportunity_based_recommendations": {
                "missing_skills": missing_skills[:5],  # Top 5
                "training_courses": training_recommendations[:5],  # Top 5
                "total_missing": len(missing_skills)
            },
            "dashboard_metrics": {
                "skills_to_develop": len(missing_skills),
                "active_trainings": len(training_enrollments),
                "missed_opportunities": len([o for o in opportunities if o.get('status') == 'open'])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Opportunity management
@app.get("/api/opportunities")
async def get_all_opportunities():
    """Get all opportunities"""
    try:
        opportunities = db.get_all_opportunities()
        return opportunities
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
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
        
        return {
            "id": opportunity_id,
            "message": "Opportunity created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating opportunity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Application management endpoints
@app.post("/api/opportunities/{opportunity_id}/apply")
async def apply_to_opportunity(opportunity_id: int, application_data: ApplicationCreate):
    """Apply to an opportunity"""
    try:
        # Check if consultant exists
        consultant = db.get_consultant(application_data.consultant_id)
        if not consultant:
            raise HTTPException(status_code=404, detail="Consultant not found")
        
        # Check if already applied
        existing_applications = db.get_opportunity_applications(opportunity_id)
        if any(app['consultant_id'] == str(application_data.consultant_id) for app in existing_applications):
            raise HTTPException(status_code=400, detail="Already applied to this opportunity")
        
        # Create application
        application_id = db.add_application(
            opportunity_id=opportunity_id,
            consultant_id=application_data.consultant_id,
            consultant_email=application_data.consultant_email,
            status='pending'
        )
        
        return {
            "id": application_id,
            "message": "Application submitted successfully"
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
        db.update_consultant(
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

if __name__ == "__main__":
    uvicorn.run(
        "simple_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
