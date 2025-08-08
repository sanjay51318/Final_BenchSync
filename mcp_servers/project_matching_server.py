import asyncio
import json
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models.consultant import Consultant
from database.models.project_opportunity import ProjectOpportunity, ConsultantProjectMatch

class ProjectMatchingAgent:
    def __init__(self):
        self.match_threshold = 0.3  # Minimum match score for recommendations

    async def create_project_opportunity(
        self,
        project_name: str,
        client_name: str,
        project_description: str,
        required_skills: List[str],
        required_experience_years: float,
        start_date: str,
        duration_months: float,
        hourly_rate: Optional[float] = None,
        location: Optional[str] = None,
        remote_allowed: bool = True
    ) -> Dict[str, Any]:
        """Create a new project opportunity"""
        try:
            db = SessionLocal()
            try:
                project = ProjectOpportunity(
                    project_name=project_name,
                    client_name=client_name,
                    project_description=project_description,
                    required_skills=required_skills,
                    required_experience_years=required_experience_years,
                    start_date=datetime.fromisoformat(start_date),
                    duration_months=duration_months,
                    hourly_rate=hourly_rate,
                    location=location,
                    remote_allowed=remote_allowed,
                    status="open",
                    priority="medium"
                )

                db.add(project)
                db.commit()
                db.refresh(project)

                return {
                    "success": True,
                    "project_id": project.id,
                    "message": f"Project '{project_name}' created successfully"
                }

            finally:
                db.close()

        except Exception as e:
            return {"success": False, "error": f"Project creation failed: {str(e)}"}

    async def match_consultants_to_project(
        self, 
        project_id: int, 
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Find and rank consultants for a specific project"""
        try:
            db = SessionLocal()
            try:
                # Get project details
                project = db.query(ProjectOpportunity).filter(
                    ProjectOpportunity.id == project_id
                ).first()

                if not project:
                    return {"success": False, "error": "Project not found"}

                # Get available consultants
                consultants = db.query(Consultant).filter(
                    Consultant.bench_status == "available"
                ).all()

                if not consultants:
                    return {
                        "success": True,
                        "project_id": project_id,
                        "matches": [],
                        "message": "No available consultants found"
                    }

                matches = []

                for consultant in consultants:
                    match_analysis = self.calculate_consultant_project_match(
                        consultant, project
                    )

                    if match_analysis["overall_score"] >= self.match_threshold:
                        matches.append({
                            "consultant_id": consultant.id,
                            "name": consultant.name,
                            "employee_id": consultant.employee_id,
                            "email": consultant.email,
                            "overall_score": match_analysis["overall_score"],
                            "skill_score": match_analysis["skill_score"],
                            "experience_score": match_analysis["experience_score"],
                            "matching_skills": match_analysis["matching_skills"],
                            "missing_skills": match_analysis["missing_skills"],
                            "recommendation": match_analysis["recommendation"],
                            "reasoning": match_analysis["reasoning"]
                        })

                # Sort by overall score
                matches.sort(key=lambda x: x["overall_score"], reverse=True)
                top_matches = matches[:top_n]

                # Save matches to database
                for match in top_matches:
                    existing_match = db.query(ConsultantProjectMatch).filter(
                        ConsultantProjectMatch.consultant_id == match["consultant_id"],
                        ConsultantProjectMatch.project_opportunity_id == project_id
                    ).first()

                    if not existing_match:
                        db_match = ConsultantProjectMatch(
                            consultant_id=match["consultant_id"],
                            project_opportunity_id=project_id,
                            match_score=match["overall_score"],
                            skill_match_details=json.dumps({
                                "matching_skills": match["matching_skills"],
                                "missing_skills": match["missing_skills"]
                            }),
                            experience_match=match["experience_score"],
                            match_reasoning=match["reasoning"],
                            recommendation=match["recommendation"]
                        )
                        db.add(db_match)

                db.commit()

                return {
                    "success": True,
                    "project_id": project_id,
                    "project_name": project.project_name,
                    "total_consultants_evaluated": len(consultants),
                    "qualified_matches": len(matches),
                    "top_matches": top_matches
                }

            finally:
                db.close()

        except Exception as e:
            return {"success": False, "error": f"Matching failed: {str(e)}"}

    def calculate_consultant_project_match(
        self, 
        consultant: Consultant, 
        project: ProjectOpportunity
    ) -> Dict[str, Any]:
        """Calculate detailed match score between consultant and project"""

        # Skill matching
        consultant_skills = [skill.lower() for skill in (consultant.technical_skills or [])]
        required_skills = [skill.lower() for skill in (project.required_skills or [])]

        matching_skills = list(set(consultant_skills) & set(required_skills))
        missing_skills = list(set(required_skills) - set(consultant_skills))

        skill_score = len(matching_skills) / len(required_skills) if required_skills else 0

        # Experience matching
        consultant_experience = consultant.years_of_experience or 0
        required_experience = project.required_experience_years or 0

        if required_experience == 0:
            experience_score = 1.0
        elif consultant_experience >= required_experience:
            # Bonus for more experience, but with diminishing returns
            excess_experience = consultant_experience - required_experience
            experience_score = min(1.0 + (excess_experience * 0.1), 1.5)
        else:
            # Penalty for insufficient experience
            experience_score = consultant_experience / required_experience

        # Overall score calculation (weighted)
        overall_score = (skill_score * 0.7) + (min(experience_score, 1.0) * 0.3)

        # Generate recommendation
        if overall_score >= 0.8:
            recommendation = "strong"
            reasoning = f"Excellent match with {len(matching_skills)}/{len(required_skills)} required skills and {consultant_experience} years experience."
        elif overall_score >= 0.6:
            recommendation = "good"
            reasoning = f"Good match with {len(matching_skills)}/{len(required_skills)} required skills. Some skill gaps: {', '.join(missing_skills[:3])}."
        elif overall_score >= 0.3:
            recommendation = "moderate"
            reasoning = f"Moderate match. Missing key skills: {', '.join(missing_skills[:3])}. May need training."
        else:
            recommendation = "weak"
            reasoning = f"Low match. Missing most required skills: {', '.join(missing_skills[:5])}."

        return {
            "overall_score": round(overall_score, 3),
            "skill_score": round(skill_score, 3),
            "experience_score": round(min(experience_score, 1.0), 3),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "recommendation": recommendation,
            "reasoning": reasoning
        }

    async def get_project_opportunities(
        self, 
        status: str = "open",
        client_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get list of project opportunities"""
        try:
            db = SessionLocal()
            try:
                query = db.query(ProjectOpportunity).filter(
                    ProjectOpportunity.status == status
                )

                if client_name:
                    query = query.filter(
                        ProjectOpportunity.client_name.ilike(f"%{client_name}%")
                    )

                projects = query.all()

                project_list = []
                for project in projects:
                    project_list.append({
                        "id": project.id,
                        "project_name": project.project_name,
                        "client_name": project.client_name,
                        "required_skills": project.required_skills,
                        "required_experience_years": project.required_experience_years,
                        "duration_months": project.duration_months,
                        "start_date": project.start_date.isoformat() if project.start_date else None,
                        "location": project.location,
                        "remote_allowed": project.remote_allowed,
                        "hourly_rate": project.hourly_rate,
                        "status": project.status,
                        "priority": project.priority,
                        "created_at": project.created_at.isoformat()
                    })

                return {
                    "success": True,
                    "total_projects": len(project_list),
                    "projects": project_list
                }

            finally:
                db.close()

        except Exception as e:
            return {"success": False, "error": f"Failed to get projects: {str(e)}"}

    async def get_consultant_recommendations_for_skills(
        self, 
        required_skills: List[str],
        min_experience: float = 0.0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get consultant recommendations based on required skills"""
        try:
            db = SessionLocal()
            try:
                consultants = db.query(Consultant).filter(
                    Consultant.bench_status == "available",
                    Consultant.years_of_experience >= min_experience
                ).all()

                recommendations = []

                for consultant in consultants:
                    consultant_skills = [skill.lower() for skill in (consultant.technical_skills or [])]
                    required_skills_lower = [skill.lower() for skill in required_skills]

                    matching_skills = list(set(consultant_skills) & set(required_skills_lower))

                    if matching_skills:
                        skill_match_rate = len(matching_skills) / len(required_skills_lower)

                        recommendations.append({
                            "consultant_id": consultant.id,
                            "name": consultant.name,
                            "employee_id": consultant.employee_id,
                            "technical_skills": consultant.technical_skills,
                            "years_of_experience": consultant.years_of_experience,
                            "matching_skills": matching_skills,
                            "skill_match_rate": round(skill_match_rate, 3),
                            "total_skills": len(consultant_skills)
                        })

                # Sort by skill match rate
                recommendations.sort(key=lambda x: x["skill_match_rate"], reverse=True)

                return {
                    "success": True,
                    "required_skills": required_skills,
                    "min_experience": min_experience,
                    "total_found": len(recommendations),
                    "recommendations": recommendations[:limit]
                }

            finally:
                db.close()

        except Exception as e:
            return {"success": False, "error": f"Recommendation failed: {str(e)}"}

# Test the agent
if __name__ == "__main__":
    agent = ProjectMatchingAgent()

    # Test project creation
    import asyncio
    result = asyncio.run(agent.create_project_opportunity(
        project_name="Cloud Migration Project",
        client_name="TechCorp Inc",
        project_description="Migrate legacy systems to AWS cloud",
        required_skills=["AWS", "Python", "Docker", "Kubernetes"],
        required_experience_years=5.0,
        start_date="2025-02-01",
        duration_months=6.0,
        hourly_rate=150.0,
        location="New York",
        remote_allowed=True
    ))
    print("Project Creation Result:", result)
