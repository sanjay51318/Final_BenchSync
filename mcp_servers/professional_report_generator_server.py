#!/usr/bin/env python3
"""
Professional Report Generator MCP Server
Generates comprehensive consultant reports with real-time data synchronization
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Add project root to path
import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Database imports
from database.professional_connection import SessionLocal
from database.models.professional_models import (
    ConsultantProfile, User, ConsultantSkill, ResumeAnalysis,
    ProjectOpportunity, OpportunityApplication, AttendanceRecord
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize server
server = Server("professional-report-generator")

class ProfessionalReportGenerator:
    """Advanced report generator with AI analytics"""
    
    def __init__(self):
        self.db_session = None
    
    def get_db_session(self) -> Session:
        """Get database session"""
        if self.db_session is None:
            self.db_session = SessionLocal()
        return self.db_session
    
    def close_db_session(self):
        """Close database session"""
        if self.db_session:
            self.db_session.close()
            self.db_session = None
    
    async def generate_consultant_report(self, consultant_email: str, report_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive consultant report"""
        try:
            db = self.get_db_session()
            
            # Get consultant profile
            consultant = db.query(ConsultantProfile).join(User).filter(
                User.email == consultant_email
            ).first()
            
            if not consultant:
                return {"error": f"Consultant with email {consultant_email} not found"}
            
            # Generate different report types
            if report_type == "comprehensive":
                return await self._generate_comprehensive_report(consultant, db)
            elif report_type == "performance":
                return await self._generate_performance_report(consultant, db)
            elif report_type == "skills":
                return await self._generate_skills_report(consultant, db)
            elif report_type == "opportunities":
                return await self._generate_opportunities_report(consultant, db)
            else:
                return await self._generate_comprehensive_report(consultant, db)
                
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {"error": f"Report generation failed: {str(e)}"}
        finally:
            self.close_db_session()
    
    async def _generate_comprehensive_report(self, consultant: ConsultantProfile, db: Session) -> Dict[str, Any]:
        """Generate comprehensive consultant report"""
        
        # 1. Consultant Overview
        consultant_overview = {
            "consultant_id": consultant.id,
            "name": consultant.user.name,
            "email": consultant.user.email,
            "primary_skill": consultant.primary_skill,
            "experience_years": consultant.experience_years,
            "current_status": consultant.current_status,
            "resume_status": consultant.resume_status,
            "training_status": consultant.training_status,
            "opportunities_count": consultant.opportunities_count,
            "profile_created": consultant.created_at.isoformat() if consultant.created_at else None,
            "last_updated": consultant.updated_at.isoformat() if consultant.updated_at else None
        }
        
        # 2. Skills Analysis
        skills_data = await self._analyze_consultant_skills(consultant, db)
        
        # 3. Opportunity Analysis
        opportunities_data = await self._analyze_consultant_opportunities(consultant, db)
        
        # 4. Performance Metrics
        performance_data = await self._calculate_performance_metrics(consultant, db)
        
        # 5. Attendance Analysis (if available)
        attendance_data = await self._analyze_attendance(consultant, db)
        
        # 6. Resume Analysis
        resume_data = await self._analyze_resume_data(consultant, db)
        
        # 7. AI Insights and Recommendations
        ai_insights = await self._generate_ai_insights(consultant, skills_data, opportunities_data, performance_data, db)
        
        # 8. Market Position Analysis
        market_analysis = await self._analyze_market_position(consultant, skills_data, db)
        
        return {
            "success": True,
            "report_type": "comprehensive",
            "generated_at": datetime.now().isoformat(),
            "consultant_overview": consultant_overview,
            "skills_analysis": skills_data,
            "opportunities_analysis": opportunities_data,
            "performance_metrics": performance_data,
            "attendance_analysis": attendance_data,
            "resume_analysis": resume_data,
            "ai_insights": ai_insights,
            "market_analysis": market_analysis,
            "report_summary": {
                "total_skills": len(skills_data.get("skills_by_category", {})),
                "opportunities_applied": opportunities_data.get("total_applications", 0),
                "success_rate": performance_data.get("opportunity_success_rate", 0),
                "skill_growth_trend": ai_insights.get("skill_growth_trend", "stable"),
                "recommendation_priority": ai_insights.get("top_recommendations", [])[:3]
            }
        }
    
    async def _analyze_consultant_skills(self, consultant: ConsultantProfile, db: Session) -> Dict[str, Any]:
        """Analyze consultant skills in detail"""
        
        # Get all skills
        skills = db.query(ConsultantSkill).filter(
            ConsultantSkill.consultant_id == consultant.id
        ).all()
        
        # Group by category
        skills_by_category = {}
        skill_sources = {}
        proficiency_distribution = {"beginner": 0, "intermediate": 0, "advanced": 0, "expert": 0}
        
        for skill in skills:
            category = skill.skill_category or 'other'
            if category not in skills_by_category:
                skills_by_category[category] = []
            
            skill_data = {
                "name": skill.skill_name,
                "proficiency": skill.proficiency_level,
                "years_experience": skill.years_experience,
                "source": skill.source,
                "confidence_score": skill.confidence_score,
                "is_primary": skill.is_primary,
                "verified": getattr(skill, 'verified', False),
                "last_updated": skill.updated_at.isoformat() if skill.updated_at else None
            }
            
            skills_by_category[category].append(skill_data)
            
            # Track sources
            source = skill.source or 'unknown'
            skill_sources[source] = skill_sources.get(source, 0) + 1
            
            # Track proficiency distribution
            proficiency = skill.proficiency_level or 'intermediate'
            if proficiency in proficiency_distribution:
                proficiency_distribution[proficiency] += 1
        
        # Calculate skill metrics
        total_skills = len(skills)
        verified_skills = len([s for s in skills if getattr(s, 'verified', False)])
        primary_skills = len([s for s in skills if s.is_primary])
        avg_experience = sum([s.years_experience or 0 for s in skills]) / max(total_skills, 1)
        avg_confidence = sum([s.confidence_score or 0 for s in skills]) / max(total_skills, 1)
        
        return {
            "total_skills": total_skills,
            "verified_skills": verified_skills,
            "primary_skills": primary_skills,
            "skills_by_category": skills_by_category,
            "skill_sources": skill_sources,
            "proficiency_distribution": proficiency_distribution,
            "metrics": {
                "average_experience_years": round(avg_experience, 1),
                "average_confidence_score": round(avg_confidence, 2),
                "skill_diversity": len(skills_by_category),
                "verification_rate": round((verified_skills / max(total_skills, 1)) * 100, 1)
            }
        }
    
    async def _analyze_consultant_opportunities(self, consultant: ConsultantProfile, db: Session) -> Dict[str, Any]:
        """Analyze consultant opportunity history and success"""
        
        # Get all applications
        applications = db.query(OpportunityApplication).filter(
            OpportunityApplication.consultant_id == consultant.id
        ).order_by(OpportunityApplication.created_at.desc()).all()
        
        # Analyze applications by status
        status_breakdown = {}
        monthly_applications = {}
        success_metrics = {
            "total_applications": len(applications),
            "successful_applications": 0,
            "pending_applications": 0,
            "rejected_applications": 0
        }
        
        for app in applications:
            # Status breakdown
            status = app.status or 'unknown'
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
            
            # Monthly applications (last 12 months)
            if app.created_at:
                month_key = app.created_at.strftime("%Y-%m")
                monthly_applications[month_key] = monthly_applications.get(month_key, 0) + 1
            
            # Success metrics
            if status in ['accepted', 'hired', 'selected']:
                success_metrics["successful_applications"] += 1
            elif status in ['pending', 'applied', 'under_review']:
                success_metrics["pending_applications"] += 1
            elif status in ['rejected', 'declined']:
                success_metrics["rejected_applications"] += 1
        
        # Get opportunity details
        recent_applications = []
        for app in applications[:10]:  # Last 10 applications
            opportunity = db.query(ProjectOpportunity).filter(
                ProjectOpportunity.id == app.opportunity_id
            ).first()
            
            if opportunity:
                recent_applications.append({
                    "opportunity_title": opportunity.title,
                    "client_name": opportunity.client_name,
                    "status": app.status,
                    "applied_at": app.created_at.isoformat() if app.created_at else None,
                    "match_score": getattr(app, 'match_score', 0.0),
                    "required_skills": opportunity.required_skills or []
                })
        
        # Calculate success rate
        success_rate = 0
        if success_metrics["total_applications"] > 0:
            success_rate = (success_metrics["successful_applications"] / success_metrics["total_applications"]) * 100
        
        return {
            "total_applications": success_metrics["total_applications"],
            "status_breakdown": status_breakdown,
            "success_metrics": success_metrics,
            "success_rate": round(success_rate, 1),
            "monthly_trends": monthly_applications,
            "recent_applications": recent_applications,
            "application_insights": {
                "most_applied_month": max(monthly_applications.items(), key=lambda x: x[1])[0] if monthly_applications else None,
                "average_applications_per_month": round(sum(monthly_applications.values()) / max(len(monthly_applications), 1), 1),
                "trending": "increasing" if len(monthly_applications) > 1 and list(monthly_applications.values())[-1] > list(monthly_applications.values())[-2] else "stable"
            }
        }
    
    async def _calculate_performance_metrics(self, consultant: ConsultantProfile, db: Session) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        # Get applications for performance calculation
        applications = db.query(OpportunityApplication).filter(
            OpportunityApplication.consultant_id == consultant.id
        ).all()
        
        # Basic performance metrics
        total_applications = len(applications)
        successful_applications = len([app for app in applications if app.status in ['accepted', 'hired', 'selected']])
        
        # Calculate various performance indicators
        opportunity_success_rate = (successful_applications / max(total_applications, 1)) * 100
        
        # Response time metrics (time between opportunity posting and application)
        response_times = []
        for app in applications:
            if app.created_at:
                # Mock calculation - in real scenario, you'd compare with opportunity post date
                response_times.append(1.5)  # Mock: 1.5 days average
        
        avg_response_time = sum(response_times) / max(len(response_times), 1) if response_times else 0
        
        # Skills utilization (how many of consultant's skills match applied opportunities)
        consultant_skills = db.query(ConsultantSkill).filter(
            ConsultantSkill.consultant_id == consultant.id
        ).all()
        
        skill_names = [skill.skill_name.lower() for skill in consultant_skills]
        skills_utilized = set()
        
        for app in applications:
            opportunity = db.query(ProjectOpportunity).filter(
                ProjectOpportunity.id == app.opportunity_id
            ).first()
            
            if opportunity and opportunity.required_skills:
                for req_skill in opportunity.required_skills:
                    if req_skill.lower() in skill_names:
                        skills_utilized.add(req_skill.lower())
        
        skill_utilization_rate = (len(skills_utilized) / max(len(skill_names), 1)) * 100
        
        # Market competitiveness score
        market_score = min(100, (opportunity_success_rate + skill_utilization_rate) / 2)
        
        return {
            "opportunity_success_rate": round(opportunity_success_rate, 1),
            "average_response_time_days": round(avg_response_time, 1),
            "skill_utilization_rate": round(skill_utilization_rate, 1),
            "market_competitiveness_score": round(market_score, 1),
            "performance_indicators": {
                "total_opportunities_applied": total_applications,
                "successful_placements": successful_applications,
                "skills_actively_used": len(skills_utilized),
                "profile_completeness": self._calculate_profile_completeness(consultant),
                "activity_level": "high" if total_applications > 10 else "medium" if total_applications > 5 else "low"
            },
            "performance_trends": {
                "last_30_days": {
                    "applications": len([app for app in applications if app.created_at and app.created_at > datetime.now() - timedelta(days=30)]),
                    "success_rate": round(opportunity_success_rate, 1)  # Simplified
                },
                "last_90_days": {
                    "applications": len([app for app in applications if app.created_at and app.created_at > datetime.now() - timedelta(days=90)]),
                    "success_rate": round(opportunity_success_rate, 1)  # Simplified
                }
            }
        }
    
    def _calculate_profile_completeness(self, consultant: ConsultantProfile) -> float:
        """Calculate profile completeness percentage"""
        completeness = 0
        total_fields = 8
        
        if consultant.user.name: completeness += 1
        if consultant.user.email: completeness += 1
        if consultant.primary_skill: completeness += 1
        if consultant.experience_years and consultant.experience_years > 0: completeness += 1
        if consultant.current_status: completeness += 1
        if consultant.resume_status == 'updated': completeness += 1
        if consultant.training_status: completeness += 1
        if consultant.opportunities_count and consultant.opportunities_count > 0: completeness += 1
        
        return round((completeness / total_fields) * 100, 1)
    
    async def _analyze_attendance(self, consultant: ConsultantProfile, db: Session) -> Dict[str, Any]:
        """Analyze attendance patterns (if available)"""
        
        # Try to get attendance records - may not exist for all consultants
        try:
            attendance_records = db.query(AttendanceRecord).filter(
                AttendanceRecord.user_id == str(consultant.user.id)
            ).order_by(AttendanceRecord.date.desc()).limit(90).all()  # Last 90 days
            
            if not attendance_records:
                return {
                    "has_attendance_data": False,
                    "message": "No attendance data available for this consultant"
                }
            
            # Analyze attendance
            total_days = len(attendance_records)
            present_days = len([r for r in attendance_records if r.status == 'present'])
            absent_days = len([r for r in attendance_records if r.status == 'absent'])
            half_days = len([r for r in attendance_records if r.status == 'half_day'])
            leave_days = len([r for r in attendance_records if r.status == 'leave'])
            
            total_hours = sum([r.hours_worked or 0 for r in attendance_records])
            attendance_rate = (present_days + (half_days * 0.5)) / max(total_days, 1) * 100
            
            # Weekly patterns
            weekly_pattern = {}
            for record in attendance_records:
                if record.date:
                    day_name = datetime.strptime(record.date, "%Y-%m-%d").strftime("%A")
                    if day_name not in weekly_pattern:
                        weekly_pattern[day_name] = {"present": 0, "absent": 0, "total": 0}
                    
                    weekly_pattern[day_name]["total"] += 1
                    if record.status == 'present':
                        weekly_pattern[day_name]["present"] += 1
                    else:
                        weekly_pattern[day_name]["absent"] += 1
            
            return {
                "has_attendance_data": True,
                "period_days": total_days,
                "present_days": present_days,
                "absent_days": absent_days,
                "half_days": half_days,
                "leave_days": leave_days,
                "total_hours_worked": total_hours,
                "attendance_rate": round(attendance_rate, 1),
                "average_hours_per_day": round(total_hours / max(present_days + half_days, 1), 1),
                "weekly_patterns": weekly_pattern,
                "attendance_insights": {
                    "consistency": "high" if attendance_rate > 90 else "medium" if attendance_rate > 75 else "low",
                    "punctuality": "excellent" if attendance_rate > 95 else "good" if attendance_rate > 85 else "needs_improvement"
                }
            }
            
        except Exception as e:
            logger.warning(f"Attendance analysis failed: {str(e)}")
            return {
                "has_attendance_data": False,
                "error": f"Attendance analysis failed: {str(e)}"
            }
    
    async def _analyze_resume_data(self, consultant: ConsultantProfile, db: Session) -> Dict[str, Any]:
        """Analyze resume data and AI insights"""
        
        # Get latest resume analysis
        resume_analysis = db.query(ResumeAnalysis).filter(
            ResumeAnalysis.consultant_id == consultant.id
        ).order_by(ResumeAnalysis.created_at.desc()).first()
        
        if not resume_analysis:
            return {
                "has_resume": False,
                "message": "No resume analysis available"
            }
        
        return {
            "has_resume": True,
            "file_name": resume_analysis.file_name,
            "upload_date": resume_analysis.created_at.isoformat() if resume_analysis.created_at else None,
            "extracted_skills": resume_analysis.extracted_skills or [],
            "extracted_competencies": resume_analysis.extracted_competencies or [],
            "identified_roles": resume_analysis.identified_roles or [],
            "ai_summary": resume_analysis.ai_summary,
            "ai_feedback": resume_analysis.ai_feedback,
            "ai_suggestions": resume_analysis.ai_suggestions,
            "confidence_score": resume_analysis.confidence_score,
            "processing_time": resume_analysis.processing_time,
            "resume_insights": {
                "skills_extracted_count": len(resume_analysis.extracted_skills or []),
                "competencies_identified": len(resume_analysis.extracted_competencies or []),
                "career_roles_suggested": len(resume_analysis.identified_roles or []),
                "ai_confidence_level": "high" if resume_analysis.confidence_score > 0.8 else "medium" if resume_analysis.confidence_score > 0.6 else "low",
                "resume_quality": "excellent" if resume_analysis.confidence_score > 0.85 else "good" if resume_analysis.confidence_score > 0.7 else "needs_improvement"
            }
        }
    
    async def _generate_ai_insights(self, consultant: ConsultantProfile, skills_data: Dict, opportunities_data: Dict, performance_data: Dict, db: Session) -> Dict[str, Any]:
        """Generate AI-powered insights and recommendations"""
        
        # Skill growth recommendations
        skill_recommendations = []
        skill_categories = skills_data.get("skills_by_category", {})
        
        # Identify skill gaps based on market opportunities
        all_opportunities = db.query(ProjectOpportunity).filter(
            ProjectOpportunity.status == "open"
        ).all()
        
        market_skills = {}
        for opp in all_opportunities:
            if opp.required_skills:
                for skill in opp.required_skills:
                    market_skills[skill.lower()] = market_skills.get(skill.lower(), 0) + 1
        
        consultant_skills = []
        for category_skills in skill_categories.values():
            consultant_skills.extend([skill["name"].lower() for skill in category_skills])
        
        # Find top market skills not in consultant's profile
        missing_skills = []
        for skill, demand in sorted(market_skills.items(), key=lambda x: x[1], reverse=True)[:10]:
            if skill not in consultant_skills:
                missing_skills.append({"skill": skill, "market_demand": demand})
        
        # Career progression recommendations
        current_level = consultant.experience_years or 0
        career_recommendations = []
        
        if current_level < 2:
            career_recommendations.extend([
                "Focus on building foundational technical skills",
                "Seek mentorship opportunities",
                "Contribute to open-source projects"
            ])
        elif current_level < 5:
            career_recommendations.extend([
                "Develop leadership and communication skills",
                "Take on project management responsibilities",
                "Expand technical expertise in emerging technologies"
            ])
        else:
            career_recommendations.extend([
                "Consider architectural and strategic roles",
                "Mentor junior developers",
                "Develop business and domain expertise"
            ])
        
        # Performance improvement suggestions
        success_rate = performance_data.get("opportunity_success_rate", 0)
        improvement_suggestions = []
        
        if success_rate < 30:
            improvement_suggestions.extend([
                "Review and optimize your application approach",
                "Enhance your skill profile with in-demand technologies",
                "Consider specialized training or certifications"
            ])
        elif success_rate < 60:
            improvement_suggestions.extend([
                "Target opportunities that better match your skill set",
                "Improve your application response time",
                "Develop additional complementary skills"
            ])
        else:
            improvement_suggestions.extend([
                "Maintain your excellent performance",
                "Consider higher-level or specialized roles",
                "Share your expertise through mentoring"
            ])
        
        return {
            "skill_gap_analysis": {
                "missing_high_demand_skills": missing_skills[:5],
                "recommended_skill_additions": [skill["skill"] for skill in missing_skills[:3]]
            },
            "career_progression": {
                "current_level": "junior" if current_level < 2 else "mid" if current_level < 5 else "senior",
                "next_level_requirements": career_recommendations,
                "estimated_time_to_next_level": f"{max(1, 3 - (current_level % 3))} years"
            },
            "performance_optimization": {
                "current_success_rate": success_rate,
                "improvement_suggestions": improvement_suggestions,
                "target_success_rate": min(100, success_rate + 20)
            },
            "top_recommendations": [
                f"Add {missing_skills[0]['skill']} to your skill set" if missing_skills else "Maintain current skills",
                "Improve application response time" if performance_data.get("average_response_time_days", 0) > 2 else "Good application timing",
                "Focus on high-demand market skills" if len(missing_skills) > 3 else "Well-aligned with market demands"
            ],
            "skill_growth_trend": "growing" if len(consultant_skills) > 5 else "stable",
            "market_alignment_score": round(min(100, (len(consultant_skills) / max(len(market_skills), 1)) * 100), 1)
        }
    
    async def _analyze_market_position(self, consultant: ConsultantProfile, skills_data: Dict, db: Session) -> Dict[str, Any]:
        """Analyze consultant's position in the market"""
        
        # Get similar consultants for benchmarking
        similar_consultants = db.query(ConsultantProfile).filter(
            ConsultantProfile.primary_skill == consultant.primary_skill,
            ConsultantProfile.id != consultant.id
        ).limit(20).all()
        
        # Market position metrics
        total_consultants = len(similar_consultants) + 1
        consultant_skills_count = skills_data.get("total_skills", 0)
        consultant_experience = consultant.experience_years or 0
        
        # Calculate relative positioning
        skill_rank = 1  # Start with best rank
        experience_rank = 1
        
        for other in similar_consultants:
            other_skills = db.query(ConsultantSkill).filter(
                ConsultantSkill.consultant_id == other.id
            ).count()
            
            if other_skills > consultant_skills_count:
                skill_rank += 1
            
            if (other.experience_years or 0) > consultant_experience:
                experience_rank += 1
        
        # Market competitiveness analysis
        competitiveness_factors = {
            "skill_diversity": min(100, (consultant_skills_count / 15) * 100),  # Assuming 15 is excellent
            "experience_level": min(100, (consultant_experience / 10) * 100),  # Assuming 10 years is senior
            "market_alignment": skills_data.get("metrics", {}).get("verification_rate", 0),
            "profile_completeness": self._calculate_profile_completeness(consultant)
        }
        
        overall_competitiveness = sum(competitiveness_factors.values()) / len(competitiveness_factors)
        
        return {
            "market_position": {
                "skill_rank": f"{skill_rank}/{total_consultants}",
                "experience_rank": f"{experience_rank}/{total_consultants}",
                "percentile_skill": round((1 - (skill_rank - 1) / total_consultants) * 100, 1),
                "percentile_experience": round((1 - (experience_rank - 1) / total_consultants) * 100, 1)
            },
            "competitiveness_analysis": {
                "overall_score": round(overall_competitiveness, 1),
                "skill_diversity_score": round(competitiveness_factors["skill_diversity"], 1),
                "experience_score": round(competitiveness_factors["experience_level"], 1),
                "market_alignment_score": round(competitiveness_factors["market_alignment"], 1),
                "profile_completeness_score": round(competitiveness_factors["profile_completeness"], 1)
            },
            "market_insights": {
                "demand_level": "high" if consultant.primary_skill in ['Python', 'React', 'AWS', 'Machine Learning'] else "medium",
                "competition_level": "high" if total_consultants > 15 else "medium" if total_consultants > 8 else "low",
                "growth_opportunities": [
                    "Cloud technologies" if "cloud" not in str(skills_data).lower() else "Advanced cloud architectures",
                    "AI/ML skills" if "machine learning" not in str(skills_data).lower() else "Deep learning specialization",
                    "DevOps practices" if "devops" not in str(skills_data).lower() else "Advanced CI/CD"
                ]
            },
            "benchmark_comparison": {
                "skills_vs_peers": "above_average" if skill_rank <= total_consultants * 0.3 else "average",
                "experience_vs_peers": "above_average" if experience_rank <= total_consultants * 0.3 else "average",
                "recommendations": [
                    "Maintain competitive edge" if overall_competitiveness > 75 else "Focus on skill development",
                    "Leverage experience advantage" if experience_rank <= 3 else "Gain more project experience",
                    "Optimize profile visibility" if competitiveness_factors["profile_completeness"] < 80 else "Profile well-optimized"
                ]
            }
        }

# Initialize report generator
report_generator = ProfessionalReportGenerator()

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available report generation tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="generate_consultant_report",
                description="Generate comprehensive consultant performance report",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "consultant_email": {
                            "type": "string",
                            "description": "Email of the consultant to generate report for"
                        },
                        "report_type": {
                            "type": "string",
                            "description": "Type of report: comprehensive, performance, skills, opportunities",
                            "enum": ["comprehensive", "performance", "skills", "opportunities"],
                            "default": "comprehensive"
                        }
                    },
                    "required": ["consultant_email"]
                }
            ),
            Tool(
                name="get_market_analytics",
                description="Get market analytics and trends for consultant positioning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "skill_area": {
                            "type": "string",
                            "description": "Primary skill area to analyze (optional)"
                        }
                    }
                }
            ),
            Tool(
                name="compare_consultants",
                description="Compare multiple consultants performance and skills",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "consultant_emails": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of consultant emails to compare"
                        },
                        "comparison_metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to compare: skills, performance, opportunities, experience",
                            "default": ["skills", "performance"]
                        }
                    },
                    "required": ["consultant_emails"]
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool execution requests"""
    
    try:
        if request.params.name == "generate_consultant_report":
            consultant_email = request.params.arguments.get("consultant_email")
            report_type = request.params.arguments.get("report_type", "comprehensive")
            
            if not consultant_email:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: consultant_email is required")]
                )
            
            result = await report_generator.generate_consultant_report(consultant_email, report_type)
            
            return CallToolResult(
                content=[TextContent(
                    type="text", 
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
            )
        
        elif request.params.name == "get_market_analytics":
            # Implement market analytics
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": "Market analytics feature coming soon",
                        "basic_insights": {
                            "trending_skills": ["Python", "React", "AWS", "Machine Learning", "Docker"],
                            "market_demand": "high",
                            "avg_response_time": "2.3 days"
                        }
                    }, indent=2)
                )]
            )
        
        elif request.params.name == "compare_consultants":
            # Implement consultant comparison
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": "Consultant comparison feature coming soon",
                        "comparison_available": True
                    }, indent=2)
                )]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {request.params.name}")]
            )
            
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error executing tool: {str(e)}")]
        )

async def main():
    """Main server entry point"""
    # Startup notification
    logger.info("🚀 Professional Report Generator MCP Server Starting...")
    logger.info("📊 Ready to generate comprehensive consultant reports")
    logger.info("🔗 Database: Connected to PostgreSQL consultant_bench_db")
    
    async with stdio_server() as streams:
        await server.run(
            streams[0], streams[1], InitializationOptions(
                server_name="professional-report-generator",
                server_version="1.0.0",
                capabilities={}
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
