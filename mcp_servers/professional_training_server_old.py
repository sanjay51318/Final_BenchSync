"""
Professional Training MCP Server
Handles training recommendations, progress tracking, and certification management
"""

import asyncio
import json
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the training agent
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.training_agent.agent import TrainingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalTrainingMCPServer:
    """MCP Server for training and certification services"""
    
    def __init__(self):
        self.training_agent = TrainingAgent()
        logger.info("✅ Professional Training MCP Server initialized")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id", 1)
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "professional-training-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "generate_training_recommendations":
                    result = await self.generate_training_recommendations(**arguments)
                elif tool_name == "analyze_skill_gaps":
                    result = await self.analyze_skill_gaps(**arguments)
                elif tool_name == "create_skill_development_plan":
                    result = await self.create_skill_development_plan(**arguments)
                elif tool_name == "track_training_progress":
                    result = await self.track_training_progress(**arguments)
                elif tool_name == "get_training_catalog":
                    result = await self.get_training_catalog(**arguments)
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Request handling failed: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def generate_training_recommendations(
        self,
        consultant_id: int,
        current_skills: list,
        missing_skills: list,
        experience_level: str = "intermediate",
        career_goals: list = None
    ) -> Dict[str, Any]:
        """Generate personalized training recommendations for a consultant"""
        try:
            consultant_data = {
                "consultant_id": consultant_id,
                "skills": current_skills,
                "missing_skills": missing_skills,
                "experience_level": experience_level,
                "career_goals": career_goals or []
            }
            
            result = await self.training_agent.generate_training_recommendations(consultant_data)
            
            return {
                "success": True,
                "recommendations": result,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Training recommendation generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate training recommendations: {str(e)}"
            }
    
    async def analyze_skill_gaps(
        self,
        consultant_skills: list,
        target_skills: list
    ) -> Dict[str, Any]:
        """Analyze skill gaps between current and target skills"""
        try:
            result = await self.training_agent.analyze_skill_gaps(consultant_skills, target_skills)
            
            return {
                "success": True,
                "skill_gap_analysis": result,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Skill gap analysis failed: {str(e)}"
            }
                
            except Exception as e:
                logger.error(f"Skill gap analysis failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"Skill gap analysis failed: {str(e)}"
                }
    
    async def create_skill_development_plan(
        self,
        consultant_id: int,
        name: str,
        current_skills: list,
        target_skills: list,
        experience_years: int = 3
    ) -> Dict[str, Any]:
        """Create comprehensive skill development plan"""
        try:
            consultant_data = {
                "consultant_id": consultant_id,
                "name": name,
                "skills": current_skills,
                "target_skills": target_skills,
                "experience_years": experience_years
            }
            
            result = await self.training_agent.generate_skill_development_plan(consultant_data)
            
            return {
                "success": True,
                "development_plan": result,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Skill development plan creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create development plan: {str(e)}"
            }
    
    async def track_training_progress(
        self,
            enrollment_id: int,
        progress_data: dict
    ) -> Dict[str, Any]:
        """Track and update training progress"""
        try:
            result = await self.training_agent.track_training_progress(enrollment_id, progress_data)
            
            return {
                "success": True,
                "progress_update": result,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Progress tracking failed: {str(e)}")
            return {
                "success": False,
                "error": f"Progress tracking failed: {str(e)}"
            }
    
    async def get_training_catalog(self, category: str = "all") -> Dict[str, Any]:
        """Get available training programs catalog"""
        try:
            if category == "all":
                catalog = self.training_agent.training_catalog
            else:
                catalog = {category: self.training_agent.training_catalog.get(category, [])}
            
            # Format catalog for better readability
            formatted_catalog = {}
            total_programs = 0
            
            for cat, programs in catalog.items():
                formatted_programs = []
                for program in programs:
                    formatted_programs.append({
                        "id": program["id"],
                        "title": program["title"],
                        "provider": program["provider"],
                            "duration_hours": program["duration_hours"],
                            "difficulty": program["difficulty"],
                            "cost": program["cost"],
                            "certification": program.get("certification", False),
                            "skills": program["skills"],
                            "market_demand": program["market_demand"],
                            "rating": program["rating"],
                            "url": program["url"]
                        })
                        total_programs += 1
                    
                    formatted_catalog[cat] = {
                        "category_name": cat.replace("_", " ").title(),
                        "programs": formatted_programs,
                        "program_count": len(formatted_programs)
                    }
                
                return {
                    "success": True,
                    "catalog": formatted_catalog,
                    "total_programs": total_programs,
                    "categories": list(formatted_catalog.keys()),
                    "retrieved_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Training catalog retrieval failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"Failed to retrieve training catalog: {str(e)}"
                }
        
        @self.server.tool("suggest_certification_path")
        async def suggest_certification_path(
            consultant_skills: list,
            target_role: str,
            experience_level: str = "intermediate"
        ) -> Dict[str, Any]:
            """Suggest certification path for specific career goals"""
            try:
                # Define certification paths for different roles
                certification_paths = {
                    "cloud_architect": [
                        {"name": "AWS Solutions Architect Associate", "priority": 1, "skills": ["AWS", "Cloud Architecture"]},
                        {"name": "Azure Solutions Architect Expert", "priority": 2, "skills": ["Azure", "Cloud Design"]},
                        {"name": "Google Cloud Professional Cloud Architect", "priority": 3, "skills": ["GCP", "Cloud Solutions"]}
                    ],
                    "full_stack_developer": [
                        {"name": "Microsoft Certified: Azure Developer Associate", "priority": 1, "skills": ["Azure", "Development"]},
                        {"name": "AWS Certified Developer Associate", "priority": 2, "skills": ["AWS", "APIs"]},
                        {"name": "Oracle Certified Professional, Java SE", "priority": 3, "skills": ["Java", "Programming"]}
                    ],
                    "data_scientist": [
                        {"name": "Google Cloud Professional Data Engineer", "priority": 1, "skills": ["GCP", "Data Engineering"]},
                        {"name": "Microsoft Certified: Azure Data Scientist Associate", "priority": 2, "skills": ["Azure", "Machine Learning"]},
                        {"name": "AWS Certified Machine Learning - Specialty", "priority": 3, "skills": ["AWS", "ML"]}
                    ],
                    "devops_engineer": [
                        {"name": "Certified Kubernetes Administrator (CKA)", "priority": 1, "skills": ["Kubernetes", "DevOps"]},
                        {"name": "AWS Certified DevOps Engineer Professional", "priority": 2, "skills": ["AWS", "CI/CD"]},
                        {"name": "Docker Certified Associate", "priority": 3, "skills": ["Docker", "Containers"]}
                    ]
                }
                
                # Get suggested path
                suggested_certs = certification_paths.get(target_role.lower().replace(" ", "_"), [])
                
                # Analyze current skills against certification requirements
                recommendations = []
                for cert in suggested_certs:
                    skill_match = len(set(consultant_skills) & set(cert["skills"]))
                    skill_coverage = (skill_match / len(cert["skills"])) * 100 if cert["skills"] else 0
                    
                    recommendations.append({
                        "certification_name": cert["name"],
                        "priority": cert["priority"],
                        "required_skills": cert["skills"],
                        "current_skill_coverage": round(skill_coverage, 1),
                        "readiness_level": "Ready" if skill_coverage >= 70 else "Needs Preparation",
                        "preparation_needed": [skill for skill in cert["skills"] if skill not in consultant_skills]
                    })
                
                return {
                    "success": True,
                    "target_role": target_role,
                    "certification_path": recommendations,
                    "recommended_order": sorted(recommendations, key=lambda x: (x["priority"], -x["current_skill_coverage"])),
                    "generated_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Certification path suggestion failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"Failed to suggest certification path: {str(e)}"
                }
        
        @self.server.tool("calculate_training_roi")
        async def calculate_training_roi(
            training_cost: float,
            current_salary: float,
            target_salary: float,
            training_duration_months: int = 6
        ) -> Dict[str, Any]:
            """Calculate return on investment for training programs"""
            try:
                # Calculate potential salary increase
                salary_increase = target_salary - current_salary
                annual_roi = salary_increase
                
                # Calculate payback period
                payback_months = training_cost / (salary_increase / 12) if salary_increase > 0 else float('inf')
                
                # Calculate 5-year ROI
                five_year_benefit = salary_increase * 5
                five_year_roi = ((five_year_benefit - training_cost) / training_cost) * 100 if training_cost > 0 else 0
                
                # Determine ROI rating
                if five_year_roi >= 500:
                    roi_rating = "Excellent"
                elif five_year_roi >= 300:
                    roi_rating = "Very Good"
                elif five_year_roi >= 100:
                    roi_rating = "Good"
                elif five_year_roi >= 50:
                    roi_rating = "Fair"
                else:
                    roi_rating = "Poor"
                
                return {
                    "success": True,
                    "roi_analysis": {
                        "training_investment": training_cost,
                        "expected_annual_salary_increase": salary_increase,
                        "payback_period_months": round(payback_months, 1) if payback_months != float('inf') else "No payback",
                        "five_year_roi_percentage": round(five_year_roi, 1),
                        "five_year_total_benefit": five_year_benefit,
                        "roi_rating": roi_rating,
                        "break_even_point": f"{round(payback_months, 1)} months" if payback_months != float('inf') else "Not achievable",
                        "recommendation": "Invest" if five_year_roi >= 100 else "Consider alternatives"
                    },
                    "calculated_at": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"ROI calculation failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"ROI calculation failed: {str(e)}"
                }

    async def run(self, port: int = 3001):
        """Run the MCP server"""
        try:
            logger.info(f"🚀 Starting Professional Training MCP Server on port {port}")
            logger.info("📚 Training catalog loaded")
            logger.info("🎯 AI recommendation engine ready")
            logger.info("📊 Progress tracking system active")
            
            # In a real implementation, this would start the actual MCP server
            # For now, we'll simulate it
            await asyncio.sleep(1)
            logger.info("✅ Professional Training MCP Server is running")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Professional Training MCP Server: {str(e)}")
            raise

# Entry point for the server
if __name__ == "__main__":
    async def main():
        server = ProfessionalTrainingMCPServer()
        await server.run()
    
    asyncio.run(main())
