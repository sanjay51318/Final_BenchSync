#!/usr/bin/env python3
"""
MCP Client for Resume Analyzer
Handles communication with the resume analyzer MCP server
"""
import asyncio
import json
import subprocess
import logging
import os
import tempfile
from typing import Dict, Any, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class ResumeAnalyzerMCPClient:
    """Client for communicating with Resume Analyzer MCP Server"""
    
    def __init__(self):
        self.server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "mcp_servers", 
            "professional_resume_analyzer_server.py"
        )
        self.python_path = "C:/Users/Sanjay N/anaconda3/python.exe"  # Use Anaconda Python
    
    async def analyze_resume(self, resume_text: str, filename: str = "resume.txt") -> Dict[str, Any]:
        """Analyze resume using MCP server"""
        try:
            # Prepare the request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "analyze_resume",
                    "arguments": {
                        "resume_text": resume_text,
                        "filename": filename
                    }
                }
            }
            
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(request, f)
                input_file = f.name
            
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
                        "name": "resume-analyzer-client",
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
                        except json.JSONDecodeError:
                            continue
                
                logger.warning("No valid response from MCP server, using fallback")
                return self._fallback_analysis(resume_text, filename)
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(input_file)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"MCP client error: {str(e)}")
            return self._fallback_analysis(resume_text, filename)
    
    def _fallback_analysis(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """Fallback analysis when MCP server is not available"""
        technical_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue.js', 'Node.js',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
            'Git', 'CI/CD', 'DevOps', 'Terraform', 'Ansible',
            'HTML', 'CSS', 'SCSS', 'Bootstrap', 'Tailwind',
            'PHP', 'C++', 'C#', '.NET', 'Ruby', 'Go', 'Rust',
            'Django', 'Flask', 'Spring Boot', 'Express.js', 'FastAPI',
            'Machine Learning', 'AI', 'TensorFlow', 'PyTorch', 'scikit-learn',
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum'
        ]
        
        resume_text_lower = resume_text.lower()
        extracted_skills = []
        skill_categories = {}
        
        for skill in technical_skills:
            if skill.lower() in resume_text_lower:
                extracted_skills.append(skill)
                category = self._categorize_skill(skill)
                if category not in skill_categories:
                    skill_categories[category] = []
                skill_categories[category].append(skill)
        
        return {
            "extracted_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text,
            "skills": extracted_skills,
            "skill_categories": skill_categories,
            "competencies": list(skill_categories.keys()),
            "roles": self._infer_roles_from_skills(extracted_skills),
            "skill_vector": [1.0] * len(extracted_skills),
            "ai_summary": f"Fallback analysis. Found {len(extracted_skills)} skills.",
            "ai_feedback": "Basic pattern matching analysis (fallback mode).",
            "ai_suggestions": "Consider adding more specific project examples.",
            "confidence_score": min(0.7, len(extracted_skills) / 15.0),
            "total_skills": len(extracted_skills),
            "analysis_method": "Fallback",
            "filename": filename,
            "success": True
        }
    
    def _categorize_skill(self, skill: str) -> str:
        """Categorize skills into groups"""
        skill_lower = skill.lower()
        
        if skill_lower in ['python', 'java', 'javascript', 'typescript', 'php', 'c++', 'c#', 'ruby', 'go', 'rust']:
            return 'Programming Languages'
        elif skill_lower in ['react', 'angular', 'vue.js', 'django', 'flask', 'spring boot', 'express.js', 'fastapi']:
            return 'Frameworks'
        elif skill_lower in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch']:
            return 'Databases'
        elif skill_lower in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible']:
            return 'DevOps & Cloud'
        elif skill_lower in ['html', 'css', 'scss', 'bootstrap', 'tailwind']:
            return 'Frontend Technologies'
        elif skill_lower in ['machine learning', 'ai', 'tensorflow', 'pytorch', 'scikit-learn']:
            return 'AI & ML'
        else:
            return 'Other Technologies'
    
    def _infer_roles_from_skills(self, skills: list) -> list:
        """Infer possible roles based on skills"""
        skills_lower = [skill.lower() for skill in skills]
        roles = []
        
        if any(skill in skills_lower for skill in ['react', 'angular', 'vue.js', 'html', 'css', 'javascript']):
            roles.append('Frontend Developer')
        
        if any(skill in skills_lower for skill in ['python', 'java', 'node.js', 'sql', 'postgresql']):
            roles.append('Backend Developer')
        
        if any(skill in skills_lower for skill in ['react', 'angular']) and any(skill in skills_lower for skill in ['python', 'java', 'node.js']):
            roles.append('Full Stack Developer')
        
        if any(skill in skills_lower for skill in ['aws', 'azure', 'docker', 'kubernetes', 'jenkins']):
            roles.append('DevOps Engineer')
        
        if any(skill in skills_lower for skill in ['machine learning', 'ai', 'tensorflow', 'pytorch']):
            roles.append('Data Scientist')
        
        return roles if roles else ['Software Developer']
    
    async def get_server_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities and status"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 99,
                "method": "tools/call",
                "params": {
                    "name": "get_capabilities",
                    "arguments": {}
                }
            }
            
            # Create temporary input file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(request, f)
                input_file = f.name
            
            try:
                # Run the MCP server
                process = subprocess.Popen(
                    [self.python_path, self.server_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(os.path.dirname(__file__))
                )
                
                with open(input_file, 'r') as f:
                    request_data = f.read()
                
                stdout, stderr = process.communicate(input=request_data, timeout=30)
                
                if process.returncode != 0:
                    return {"error": f"Server error: {stderr}", "status": "error"}
                
                # Parse response
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get("result"):
                                content = response["result"].get("content", [])
                                if content and len(content) > 0:
                                    text_content = content[0].get("text", "{}")
                                    return json.loads(text_content)
                        except json.JSONDecodeError:
                            continue
                
                return {"status": "ready", "capabilities": ["resume_analysis"], "ai_enabled": True}
                
            finally:
                os.unlink(input_file)
            
        except Exception as e:
            logger.error(f"Capability check failed: {str(e)}")
            return {"error": f"Capability check failed: {str(e)}", "status": "error"}

# Global instance
resume_analyzer_client = ResumeAnalyzerMCPClient()
