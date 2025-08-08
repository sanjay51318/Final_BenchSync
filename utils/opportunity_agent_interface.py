"""
Opportunity Agent MCP Client Interface
Handles communication with the Professional Opportunity Agent MCP Server
"""
import asyncio
import json
import logging
import subprocess
import os
from typing import Dict, List, Optional, Any
import sys

logger = logging.getLogger(__name__)

class OpportunityAgentMCPClient:
    """Client for communicating with the Opportunity Agent MCP Server"""
    
    def __init__(self):
        self.server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "mcp_servers", 
            "professional_opportunity_agent_server.py"
        )
        self.process = None
        
    async def _communicate_with_server(self, request: Dict) -> Dict:
        """Send request to MCP server and get response"""
        try:
            # Start server process if not running
            if not self.process or self.process.poll() is not None:
                self.process = subprocess.Popen(
                    ["C:/Users/Sanjay N/anaconda3/python.exe", self.server_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0
                )
            
            # Send initialization first if it's a fresh process
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "opportunity-agent-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send initialization
            init_json = json.dumps(init_request) + '\n'
            self.process.stdin.write(init_json)
            self.process.stdin.flush()
            
            # Send actual request
            request_json = json.dumps(request) + '\n'
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read initialization response (ignore it)
            init_response = self.process.stdout.readline()
            
            # Read actual response
            response_line = self.process.stdout.readline()
            if not response_line:
                raise Exception("No response from server")
            
            response = json.loads(response_line.strip())
            return response
            
        except Exception as e:
            logger.error(f"MCP communication failed: {str(e)}")
            # Clean up process on error
            if self.process:
                try:
                    self.process.terminate()
                except:
                    pass
                self.process = None
            
            # Return fallback response
            return {
                "error": f"MCP server communication failed: {str(e)}",
                "success": False,
                "fallback": True
            }
    
    async def match_consultant_to_opportunities(self, consultant_skills: List[str], opportunities: List[Dict]) -> Dict:
        """Match consultant skills to available opportunities"""
        try:
            if not consultant_skills:
                return {
                    "matches": [],
                    "total_matches": 0,
                    "error": "No consultant skills provided",
                    "success": False
                }
            
            # Prepare MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "match_opportunities",
                    "arguments": {
                        "consultant_skills": consultant_skills,
                        "opportunities": opportunities
                    }
                }
            }
            
            # Send to MCP server
            response = await self._communicate_with_server(request)
            
            if response.get("error"):
                logger.warning(f"MCP server error: {response['error']}")
                return self._fallback_opportunity_matching(consultant_skills, opportunities)
            
            # Parse MCP response
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content and len(content) > 0:
                text_content = content[0].get("text", "{}")
                data = json.loads(text_content)
                return data
            
            # Fallback if no content
            return self._fallback_opportunity_matching(consultant_skills, opportunities)
            
        except Exception as e:
            logger.error(f"Opportunity matching failed: {str(e)}")
            return self._fallback_opportunity_matching(consultant_skills, opportunities)
    
    async def recommend_skill_development(self, consultant_skills: List[str], target_opportunities: List[Dict]) -> Dict:
        """Get skill development recommendations"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "recommend_skills",
                    "arguments": {
                        "consultant_skills": consultant_skills,
                        "target_opportunities": target_opportunities
                    }
                }
            }
            
            response = await self._communicate_with_server(request)
            
            if response.get("error"):
                return self._fallback_skill_recommendations(consultant_skills, target_opportunities)
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content and len(content) > 0:
                text_content = content[0].get("text", "{}")
                data = json.loads(text_content)
                return data
            
            return self._fallback_skill_recommendations(consultant_skills, target_opportunities)
            
        except Exception as e:
            logger.error(f"Skill recommendation failed: {str(e)}")
            return self._fallback_skill_recommendations(consultant_skills, target_opportunities)
    
    async def analyze_market_trends(self, opportunities: List[Dict]) -> Dict:
        """Analyze market trends from opportunities"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "analyze_market",
                    "arguments": {
                        "opportunities": opportunities
                    }
                }
            }
            
            response = await self._communicate_with_server(request)
            
            if response.get("error"):
                return self._fallback_market_analysis(opportunities)
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content and len(content) > 0:
                text_content = content[0].get("text", "{}")
                data = json.loads(text_content)
                return data
            
            return self._fallback_market_analysis(opportunities)
            
        except Exception as e:
            logger.error(f"Market analysis failed: {str(e)}")
            return self._fallback_market_analysis(opportunities)
    
    async def get_server_capabilities(self) -> Dict:
        """Get server capabilities and status"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_capabilities",
                    "arguments": {}
                }
            }
            
            response = await self._communicate_with_server(request)
            
            if response.get("error"):
                return {"error": "Could not get server capabilities", "success": False}
            
            result = response.get("result", {})
            content = result.get("content", [])
            
            if content and len(content) > 0:
                text_content = content[0].get("text", "{}")
                data = json.loads(text_content)
                return data
            
            return {"error": "No capability data received", "success": False}
            
        except Exception as e:
            logger.error(f"Capability check failed: {str(e)}")
            return {"error": f"Capability check failed: {str(e)}", "success": False}
    
    def _fallback_opportunity_matching(self, consultant_skills: List[str], opportunities: List[Dict]) -> Dict:
        """Basic fallback opportunity matching"""
        matches = []
        consultant_skills_lower = [skill.lower() for skill in consultant_skills]
        
        for opp in opportunities:
            required_skills = opp.get('required_skills', [])
            required_skills_lower = [skill.lower() for skill in required_skills]
            
            # Simple intersection-based matching
            matched_skills = list(set(consultant_skills_lower) & set(required_skills_lower))
            match_score = len(matched_skills) / max(len(required_skills_lower), 1)
            
            if match_score > 0:
                matches.append({
                    'opportunity': opp,
                    'match_score': match_score,
                    'match_reasoning': f"Basic pattern matching: {len(matched_skills)}/{len(required_skills_lower)} skills matched",
                    'strengths': matched_skills,
                    'potential_gaps': [skill for skill in required_skills_lower if skill not in consultant_skills_lower],
                    'analysis_method': 'Fallback Pattern-Based'
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            "matches": matches[:10],
            "total_matches": len(matches),
            "analysis_method": "Fallback Pattern-Based",
            "success": True,
            "fallback_used": True
        }
    
    def _fallback_skill_recommendations(self, consultant_skills: List[str], target_opportunities: List[Dict]) -> Dict:
        """Basic fallback skill recommendations"""
        all_required_skills = []
        consultant_skills_lower = [skill.lower() for skill in consultant_skills]
        
        for opp in target_opportunities:
            required_skills = opp.get('required_skills', [])
            all_required_skills.extend([skill.lower() for skill in required_skills])
        
        # Count skill frequency
        skill_frequency = {}
        for skill in all_required_skills:
            if skill not in consultant_skills_lower:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Sort by frequency
        recommended_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "recommendations": {
                "high_priority": [skill for skill, freq in recommended_skills[:3]],
                "medium_priority": [skill for skill, freq in recommended_skills[3:6]],
                "low_priority": [skill for skill, freq in recommended_skills[6:]],
                "skill_frequency": dict(recommended_skills),
                "total_opportunities": len(target_opportunities)
            },
            "success": True,
            "fallback_used": True
        }
    
    def _fallback_market_analysis(self, opportunities: List[Dict]) -> Dict:
        """Basic fallback market analysis"""
        if not opportunities:
            return {
                "market_analysis": {"error": "No opportunities to analyze"},
                "success": False
            }
        
        skill_demand = {}
        for opp in opportunities:
            for skill in opp.get('required_skills', []):
                skill_lower = skill.lower()
                skill_demand[skill_lower] = skill_demand.get(skill_lower, 0) + 1
        
        top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "market_analysis": {
                "total_opportunities": len(opportunities),
                "top_skills_in_demand": dict(top_skills),
                "market_insights": ["Basic market analysis completed"],
                "analysis_method": "Fallback Pattern-Based"
            },
            "success": True,
            "fallback_used": True
        }
    
    def __del__(self):
        """Clean up subprocess on deletion"""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
