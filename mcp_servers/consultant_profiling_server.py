import asyncio
import json
from typing import Dict, Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from agents.consultant_profiling_agent.agent import ConsultantProfilingAgent
from database.connection import get_db, SessionLocal
from database.models.consultant import Consultant
from sqlalchemy.orm import Session

class ConsultantProfilingMCPServer:
    def __init__(self):
        self.server = Server("consultant-profiling-agent")
        self.agent = ConsultantProfilingAgent()
        self.setup_tools()
    
    def setup_tools(self):
        """Register MCP tools for consultant profiling"""
        
        @self.server.tool("analyze_consultant_profile")
        async def analyze_consultant_profile(
            profile_content: str,
            consultant_name: str,
            employee_id: str,
            email: str
        ) -> Dict[str, Any]:
            """
            Analyze consultant profile and store in database
            
            Args:
                profile_content: Resume/profile text or PDF content
                consultant_name: Full name of consultant
                employee_id: Unique employee identifier
                email: Consultant email address
            """
            try:
                # Analyze profile using agent
                analysis_result = await self.agent.analyze_consultant_profile(
                    profile_content, consultant_name
                )
                
                if not analysis_result.get("success"):
                    return analysis_result
                
                # Save to database
                db = SessionLocal()
                try:
                    # Check if consultant exists
                    existing_consultant = db.query(Consultant).filter(
                        Consultant.employee_id == employee_id
                    ).first()
                    
                    if existing_consultant:
                        # Update existing consultant
                        existing_consultant.name = consultant_name
                        existing_consultant.email = email
                        existing_consultant.technical_skills = analysis_result["technical_skills"]
                        existing_consultant.soft_skills = analysis_result["soft_skills"]
                        existing_consultant.certifications = analysis_result["certifications"]
                        existing_consultant.years_of_experience = analysis_result["experience_years"]
                        existing_consultant.profile_analysis = analysis_result["ai_summary"]
                        existing_consultant.skill_vector = json.dumps(analysis_result["skill_vector"])
                        
                        consultant_id = existing_consultant.id
                    else:
                        # Create new consultant
                        new_consultant = Consultant(
                            employee_id=employee_id,
                            name=consultant_name,
                            email=email,
                            technical_skills=analysis_result["technical_skills"],
                            soft_skills=analysis_result["soft_skills"],
                            certifications=analysis_result["certifications"],
                            years_of_experience=analysis_result["experience_years"],
                            profile_analysis=analysis_result["ai_summary"],
                            skill_vector=json.dumps(analysis_result["skill_vector"]),
                            bench_status="available"
                        )
                        
                        db.add(new_consultant)
                        db.flush()
                        consultant_id = new_consultant.id
                    
                    db.commit()
                    
                    return {
                        "success": True,
                        "consultant_id": consultant_id,
                        "analysis": analysis_result,
                        "message": f"Profile analyzed and saved for {consultant_name}"
                    }
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Profile analysis failed: {str(e)}"
                }
        
        @self.server.tool("get_consultant_profile")
        async def get_consultant_profile(consultant_id: int) -> Dict[str, Any]:
            """Get consultant profile by ID"""
            try:
                db = SessionLocal()
                try:
                    consultant = db.query(Consultant).filter(
                        Consultant.id == consultant_id
                    ).first()
                    
                    if not consultant:
                        return {"success": False, "error": "Consultant not found"}
                    
                    return {
                        "success": True,
                        "consultant": {
                            "id": consultant.id,
                            "employee_id": consultant.employee_id,
                            "name": consultant.name,
                            "email": consultant.email,
                            "technical_skills": consultant.technical_skills,
                            "soft_skills": consultant.soft_skills,
                            "certifications": consultant.certifications,
                            "years_of_experience": consultant.years_of_experience,
                            "bench_status": consultant.bench_status,
                            "profile_analysis": consultant.profile_analysis,
                            "created_at": consultant.created_at.isoformat()
                        }
                    }
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to retrieve consultant: {str(e)}"
                }
        
        @self.server.tool("search_consultants_by_skills")
        async def search_consultants_by_skills(
            required_skills: list,
            min_experience_years: float = 0.0
        ) -> Dict[str, Any]:
            """Search consultants by required skills and experience"""
            try:
                db = SessionLocal()
                try:
                    consultants = db.query(Consultant).filter(
                        Consultant.years_of_experience >= min_experience_years,
                        Consultant.bench_status == "available"
                    ).all()
                    
                    # Filter by skills
                    matching_consultants = []
                    for consultant in consultants:
                        if not consultant.technical_skills:
                            continue
                            
                        consultant_skills = [skill.lower() for skill in consultant.technical_skills]
                        required_skills_lower = [skill.lower() for skill in required_skills]
                        
                        # Calculate skill match percentage
                        matching_skills = set(consultant_skills) & set(required_skills_lower)
                        match_percentage = len(matching_skills) / len(required_skills_lower) * 100
                        
                        if match_percentage > 30:  # At least 30% skill match
                            matching_consultants.append({
                                "id": consultant.id,
                                "name": consultant.name,
                                "employee_id": consultant.employee_id,
                                "technical_skills": consultant.technical_skills,
                                "years_of_experience": consultant.years_of_experience,
                                "match_percentage": round(match_percentage, 2),
                                "matching_skills": list(matching_skills),
                                "bench_status": consultant.bench_status
                            })
                    
                    # Sort by match percentage
                    matching_consultants.sort(key=lambda x: x["match_percentage"], reverse=True)
                    
                    return {
                        "success": True,
                        "total_found": len(matching_consultants),
                        "consultants": matching_consultants[:10]  # Top 10 matches
                    }
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Search failed: {str(e)}"
                }

async def main():
    """Run the Consultant Profiling MCP Server"""
    server = ConsultantProfilingMCPServer()
    print("Starting Consultant Profiling MCP Server on port 8001...")
    await server.server.run(port=8001)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import json
from typing import Dict, Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from agents.consultant_profiling_agent.agent import ConsultantProfilingAgent
from database.connection import get_db, SessionLocal
from database.models.consultant import Consultant
from sqlalchemy.orm import Session

class ConsultantProfilingMCPServer:
    def __init__(self):
        self.server = Server("consultant-profiling-agent")
        self.agent = ConsultantProfilingAgent()
        self.setup_tools()
    
    def setup_tools(self):
        """Register MCP tools for consultant profiling"""
        
        @self.server.tool("analyze_consultant_profile")
        async def analyze_consultant_profile(
            profile_content: str,
            consultant_name: str,
            employee_id: str,
            email: str
        ) -> Dict[str, Any]:
            """
            Analyze consultant profile and store in database
            
            Args:
                profile_content: Resume/profile text or PDF content
                consultant_name: Full name of consultant
                employee_id: Unique employee identifier
                email: Consultant email address
            """
            try:
                # Analyze profile using agent
                analysis_result = await self.agent.analyze_consultant_profile(
                    profile_content, consultant_name
                )
                
                if not analysis_result.get("success"):
                    return analysis_result
                
                # Save to database
                db = SessionLocal()
                try:
                    # Check if consultant exists
                    existing_consultant = db.query(Consultant).filter(
                        Consultant.employee_id == employee_id
                    ).first()
                    
                    if existing_consultant:
                        # Update existing consultant
                        existing_consultant.name = consultant_name
                        existing_consultant.email = email
                        existing_consultant.technical_skills = analysis_result["technical_skills"]
                        existing_consultant.soft_skills = analysis_result["soft_skills"]
                        existing_consultant.certifications = analysis_result["certifications"]
                        existing_consultant.years_of_experience = analysis_result["experience_years"]
                        existing_consultant.profile_analysis = analysis_result["ai_summary"]
                        existing_consultant.skill_vector = json.dumps(analysis_result["skill_vector"])
                        
                        consultant_id = existing_consultant.id
                    else:
                        # Create new consultant
                        new_consultant = Consultant(
                            employee_id=employee_id,
                            name=consultant_name,
                            email=email,
                            technical_skills=analysis_result["technical_skills"],
                            soft_skills=analysis_result["soft_skills"],
                            certifications=analysis_result["certifications"],
                            years_of_experience=analysis_result["experience_years"],
                            profile_analysis=analysis_result["ai_summary"],
                            skill_vector=json.dumps(analysis_result["skill_vector"]),
                            bench_status="available"
                        )
                        
                        db.add(new_consultant)
                        db.flush()
                        consultant_id = new_consultant.id
                    
                    db.commit()
                    
                    return {
                        "success": True,
                        "consultant_id": consultant_id,
                        "analysis": analysis_result,
                        "message": f"Profile analyzed and saved for {consultant_name}"
                    }
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Profile analysis failed: {str(e)}"
                }
        
        @self.server.tool("get_consultant_profile")
        async def get_consultant_profile(consultant_id: int) -> Dict[str, Any]:
            """Get consultant profile by ID"""
            try:
                db = SessionLocal()
                try:
                    consultant = db.query(Consultant).filter(
                        Consultant.id == consultant_id
                    ).first()
                    
                    if not consultant:
                        return {"success": False, "error": "Consultant not found"}
                    
                    return {
                        "success": True,
                        "consultant": {
                            "id": consultant.id,
                            "employee_id": consultant.employee_id,
                            "name": consultant.name,
                            "email": consultant.email,
                            "technical_skills": consultant.technical_skills,
                            "soft_skills": consultant.soft_skills,
                            "certifications": consultant.certifications,
                            "years_of_experience": consultant.years_of_experience,
                            "bench_status": consultant.bench_status,
                            "profile_analysis": consultant.profile_analysis,
                            "created_at": consultant.created_at.isoformat()
                        }
                    }
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to retrieve consultant: {str(e)}"
                }
        
        @self.server.tool("search_consultants_by_skills")
        async def search_consultants_by_skills(
            required_skills: list,
            min_experience_years: float = 0.0
        ) -> Dict[str, Any]:
            """Search consultants by required skills and experience"""
            try:
                db = SessionLocal()
                try:
                    consultants = db.query(Consultant).filter(
                        Consultant.years_of_experience >= min_experience_years,
                        Consultant.bench_status == "available"
                    ).all()
                    
                    # Filter by skills
                    matching_consultants = []
                    for consultant in consultants:
                        if not consultant.technical_skills:
                            continue
                            
                        consultant_skills = [skill.lower() for skill in consultant.technical_skills]
                        required_skills_lower = [skill.lower() for skill in required_skills]
                        
                        # Calculate skill match percentage
                        matching_skills = set(consultant_skills) & set(required_skills_lower)
                        match_percentage = len(matching_skills) / len(required_skills_lower) * 100
                        
                        if match_percentage > 30:  # At least 30% skill match
                            matching_consultants.append({
                                "id": consultant.id,
                                "name": consultant.name,
                                "employee_id": consultant.employee_id,
                                "technical_skills": consultant.technical_skills,
                                "years_of_experience": consultant.years_of_experience,
                                "match_percentage": round(match_percentage, 2),
                                "matching_skills": list(matching_skills),
                                "bench_status": consultant.bench_status
                            })
                    
                    # Sort by match percentage
                    matching_consultants.sort(key=lambda x: x["match_percentage"], reverse=True)
                    
                    return {
                        "success": True,
                        "total_found": len(matching_consultants),
                        "consultants": matching_consultants[:10]  # Top 10 matches
                    }
                    
                finally:
                    db.close()
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Search failed: {str(e)}"
                }

async def main():
    """Run the Consultant Profiling MCP Server"""
    server = ConsultantProfilingMCPServer()
    print("Starting Consultant Profiling MCP Server on port 8001...")
    await server.server.run(port=8001)

if __name__ == "__main__":
    asyncio.run(main())
