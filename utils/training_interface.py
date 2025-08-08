"""
Professional Training Interface
Client interface for training and certification services via MCP Server
"""

import asyncio
import json
import subprocess
import logging
import os
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalTrainingClient:
    """Client interface for training services via MCP Server"""
    
    def __init__(self):
        self.service_name = "Professional Training Service"
        self.version = "1.0.0"
        self.server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "mcp_servers", 
            "professional_training_server.py"
        )
        self.python_path = "C:/Users/Sanjay N/anaconda3/python.exe"  # Use Anaconda Python
        logger.info("✅ Professional Training Client initialized")
    
    async def _communicate_with_server(self, request: Dict) -> Dict:
        """Send request to MCP server and get response"""
        try:
            # Check if server file exists
            if not os.path.exists(self.server_path):
                raise FileNotFoundError(f"MCP server not found at: {self.server_path}")
            
            # Run the MCP server
            process = subprocess.Popen(
                [self.python_path, self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(self.server_path),
                shell=False
            )
            
            # Send initialization first
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "training-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send requests
            input_data = json.dumps(init_request) + "\n" + json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=input_data)
            
            if process.returncode != 0:
                logger.error(f"MCP server error: {stderr}")
                raise Exception(f"Server failed: {stderr}")
            
            # Parse responses (skip initialization response, get actual result)
            if stdout.strip():
                lines = stdout.strip().split('\n')
                for line in lines:
                    try:
                        response = json.loads(line)
                        # Skip initialization response, get the actual tool response
                        if 'result' in response and response.get('id') != 0:
                            if 'content' in response['result']:
                                content = response['result']['content'][0]['text']
                                return json.loads(content)
                    except json.JSONDecodeError:
                        continue
            
            raise Exception("No valid response received from server")
            
        except Exception as e:
            logger.error(f"MCP communication failed: {str(e)}")
            raise e
    
    async def get_training_recommendations(
        self,
        consultant_id: int,
        current_skills: List[str],
        missing_skills: List[str],
        experience_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """Get personalized training recommendations via MCP server"""
        try:
            # Prepare the request for MCP server
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "generate_training_recommendations",
                    "arguments": {
                        "consultant_id": consultant_id,
                        "current_skills": current_skills,
                        "missing_skills": missing_skills,
                        "experience_level": experience_level,
                        "career_goals": []
                    }
                }
            }
            
            # Communicate with MCP server
            result = await self._communicate_with_server(request)
            return result
            
        except Exception as e:
            logger.error(f"Training recommendation request failed: {str(e)}")
            return {
                "success": False,
                "error": f"Training recommendation failed: {str(e)}",
                "recommendations": [],
                "training_catalog": []
            }
    
    async def analyze_skill_gaps(
        self,
        consultant_skills: List[str],
        target_skills: List[str]
    ) -> Dict[str, Any]:
        """Analyze skill gaps via MCP server"""
        try:
            # Prepare the request for MCP server
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "analyze_skill_gaps",
                    "arguments": {
                        "consultant_skills": consultant_skills,
                        "target_skills": target_skills
                    }
                }
            }
            
            # Communicate with MCP server
            result = await self._communicate_with_server(request)
            return result
            
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Skill gap analysis failed: {str(e)}"
            }
    
    async def create_development_plan(
        self,
        consultant_id: int,
        name: str,
        current_skills: List[str],
        target_skills: List[str],
        experience_years: int = 3
    ) -> Dict[str, Any]:
        """Create skill development plan via MCP server"""
        try:
            # Prepare the request for MCP server
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "create_skill_development_plan",
                    "arguments": {
                        "consultant_id": consultant_id,
                        "name": name,
                        "current_skills": current_skills,
                        "target_skills": target_skills,
                        "experience_years": experience_years
                    }
                }
            }
            
            # Communicate with MCP server
            result = await self._communicate_with_server(request)
            return result
            
        except Exception as e:
            logger.error(f"Development plan creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create development plan: {str(e)}"
            }
    
    async def track_progress(
        self,
        enrollment_id: int,
        progress_percentage: float,
        milestone: str = "",
        time_spent_hours: float = 0
    ) -> Dict[str, Any]:
        """Track training progress via MCP server"""
        try:
            # Prepare the request for MCP server
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "track_training_progress",
                    "arguments": {
                        "enrollment_id": enrollment_id,
                        "progress_data": {
                            "progress_percentage": progress_percentage,
                            "milestone": milestone,
                            "time_spent_hours": time_spent_hours,
                            "total_duration_hours": 40
                        }
                    }
                }
            }
            
            # Communicate with MCP server
            result = await self._communicate_with_server(request)
            return result
            
        except Exception as e:
            logger.error(f"Progress tracking failed: {str(e)}")
            return {
                "success": False,
                "error": f"Progress tracking failed: {str(e)}"
            }
    
    async def get_training_catalog(self, category: str = "all") -> Dict[str, Any]:
        """Get training catalog via MCP server"""
        try:
            # Prepare the request for MCP server
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "get_training_catalog",
                    "arguments": {
                        "category": category
                    }
                }
            }
            
            # Communicate with MCP server
            result = await self._communicate_with_server(request)
            return result
            
        except Exception as e:
            logger.error(f"Training catalog request failed: {str(e)}")
            return {
                "success": False,
                "error": f"Training catalog request failed: {str(e)}",
                "catalog": {}
            }

# Global client instance
training_client = ProfessionalTrainingClient()

# Export for use in backend
__all__ = ["training_client", "ProfessionalTrainingClient"]
