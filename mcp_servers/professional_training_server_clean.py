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
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "generate_training_recommendations",
                                "description": "Generate personalized training recommendations for a consultant",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "consultant_id": {"type": "integer"},
                                        "current_skills": {"type": "array", "items": {"type": "string"}},
                                        "missing_skills": {"type": "array", "items": {"type": "string"}},
                                        "experience_level": {"type": "string", "default": "intermediate"},
                                        "career_goals": {"type": "array", "items": {"type": "string"}}
                                    },
                                    "required": ["consultant_id", "current_skills", "missing_skills"]
                                }
                            },
                            {
                                "name": "analyze_skill_gaps",
                                "description": "Analyze skill gaps between current and target skills",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "consultant_skills": {"type": "array", "items": {"type": "string"}},
                                        "target_skills": {"type": "array", "items": {"type": "string"}}
                                    },
                                    "required": ["consultant_skills", "target_skills"]
                                }
                            },
                            {
                                "name": "create_skill_development_plan",
                                "description": "Create comprehensive skill development plan",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "consultant_id": {"type": "integer"},
                                        "name": {"type": "string"},
                                        "current_skills": {"type": "array", "items": {"type": "string"}},
                                        "target_skills": {"type": "array", "items": {"type": "string"}},
                                        "experience_years": {"type": "integer", "default": 3}
                                    },
                                    "required": ["consultant_id", "name", "current_skills", "target_skills"]
                                }
                            },
                            {
                                "name": "track_training_progress",
                                "description": "Track and update training progress",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "enrollment_id": {"type": "integer"},
                                        "progress_data": {"type": "object"}
                                    },
                                    "required": ["enrollment_id", "progress_data"]
                                }
                            },
                            {
                                "name": "get_training_catalog",
                                "description": "Get available training programs catalog",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "category": {"type": "string", "default": "all"}
                                    }
                                }
                            }
                        ]
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
                    # Use 'difficulty' instead of 'level' as that's what the training catalog has
                    formatted_programs.append({
                        "id": program["id"],
                        "title": program["title"],
                        "provider": program["provider"],
                        "difficulty": program.get("difficulty", "Unknown"),  # Fixed field name
                        "duration": program.get("duration_hours", "Unknown"),  # Fixed field name
                        "description": program.get("description", "No description available"),
                        "skills": program.get("skills", []),
                        "cost": program.get("cost", 0),
                        "certification": program.get("certification", False),
                        "market_demand": program.get("market_demand", 0)
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

async def main():
    """Main function to handle JSON-RPC requests"""
    server = ProfessionalTrainingMCPServer()
    
    try:
        # Read input from stdin
        for line in sys.stdin:
            if line.strip():
                try:
                    request = json.loads(line.strip())
                    response = await server.handle_request(request)
                    print(json.dumps(response))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {line}")
                except Exception as e:
                    logger.error(f"Error processing request: {str(e)}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
