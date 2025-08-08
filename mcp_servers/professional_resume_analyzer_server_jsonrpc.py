#!/usr/bin/env python3
"""
Professional Resume Analyzer MCP Server
Handles resume analysis with AI/ML capabilities via JSON-RPC
"""
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import traceback

# Set environment variables before importing TensorFlow-dependent modules
os.environ["TRANSFORMERS_BACKEND"] = "pt"
os.environ["USE_TF"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force CPU usage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resume-analyzer-server")

# AI/ML dependencies with fallback
HAS_AI_CAPABILITIES = False
try:
    import torch
    import numpy as np
    from transformers import pipeline, AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    HAS_AI_CAPABILITIES = True
    logger.info("✅ AI capabilities loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ AI capabilities not available: {str(e)}")
    HAS_AI_CAPABILITIES = False

class ProfessionalResumeAnalyzerServer:
    """Professional Resume Analyzer with AI capabilities"""
    
    def __init__(self):
        self.ai_models = {}
        self.initialize_ai_models()
        logger.info("✅ Professional Resume Analyzer Server initialized")
    
    def initialize_ai_models(self):
        """Initialize AI models if available"""
        if not HAS_AI_CAPABILITIES:
            logger.warning("⚠️ AI models not available, using fallback analysis")
            return
            
        try:
            # Initialize NER model for extracting entities
            self.ai_models['ner'] = pipeline(
                "ner", 
                model="dbmdz/bert-large-cased-finetuned-conll03-english",
                aggregation_strategy="simple",
                device=-1  # Use CPU
            )
            
            # Initialize sentence transformer for semantic analysis
            self.ai_models['embeddings'] = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Download NLTK data if needed
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            
            logger.info("✅ AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ AI model initialization failed: {str(e)}")
            self.ai_models = {}
    
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
                            "name": "professional-resume-analyzer",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "analyze_resume":
                    result = await self.analyze_resume(**arguments)
                elif tool_name == "get_capabilities":
                    result = await self.get_capabilities()
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
    
    async def analyze_resume(self, resume_text: str, filename: str = "resume.txt") -> Dict[str, Any]:
        """Analyze resume with AI-powered analysis"""
        try:
            if self.ai_models:
                return await self._ai_analysis(resume_text, filename)
            else:
                return self._fallback_analysis(resume_text, filename)
                
        except Exception as e:
            logger.error(f"Resume analysis failed: {str(e)}")
            return self._fallback_analysis(resume_text, filename)
    
    async def _ai_analysis(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """AI-powered resume analysis"""
        try:
            # Extract technical skills using NER and pattern matching
            skills = self._extract_skills_ai(resume_text)
            
            # Categorize skills
            skill_categories = self._categorize_skills(skills)
            
            # Generate AI summary and feedback
            ai_summary = self._generate_ai_summary(resume_text, skills)
            ai_feedback = self._generate_ai_feedback(resume_text, skills)
            ai_suggestions = self._generate_ai_suggestions(skills)
            
            # Calculate semantic embedding
            skill_vector = self._generate_skill_vector(skills)
            
            # Infer roles
            roles = self._infer_roles_from_skills(skills)
            
            # Calculate confidence score
            confidence_score = min(0.95, 0.6 + len(skills) / 30.0)
            
            return {
                "extracted_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text,
                "skills": skills,
                "skill_categories": skill_categories,
                "competencies": list(skill_categories.keys()),
                "roles": roles,
                "skill_vector": skill_vector,
                "ai_summary": ai_summary,
                "ai_feedback": ai_feedback,
                "ai_suggestions": ai_suggestions,
                "confidence_score": confidence_score,
                "total_skills": len(skills),
                "analysis_method": "AI-Enhanced",
                "filename": filename,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._fallback_analysis(resume_text, filename)
    
    def _extract_skills_ai(self, text: str) -> List[str]:
        """Extract skills using AI and pattern matching"""
        skills = set()
        
        # Technical skills patterns
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
        
        # Pattern matching
        text_lower = text.lower()
        for skill in technical_skills:
            if skill.lower() in text_lower:
                skills.add(skill)
        
        # Use NER if available
        if 'ner' in self.ai_models:
            try:
                entities = self.ai_models['ner'](text)
                for entity in entities:
                    if entity['entity_group'] in ['ORG', 'MISC'] and len(entity['word']) > 2:
                        # Could be a technology or tool
                        word = entity['word'].strip()
                        if any(tech.lower() in word.lower() for tech in technical_skills):
                            skills.add(word)
            except Exception as e:
                logger.warning(f"NER extraction failed: {str(e)}")
        
        return sorted(list(skills))
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into groups"""
        categories = {
            'Programming Languages': [],
            'Frameworks': [],
            'Databases': [],
            'DevOps & Cloud': [],
            'Frontend Technologies': [],
            'AI & ML': [],
            'Other Technologies': []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if skill_lower in ['python', 'java', 'javascript', 'typescript', 'php', 'c++', 'c#', 'ruby', 'go', 'rust']:
                categories['Programming Languages'].append(skill)
            elif skill_lower in ['react', 'angular', 'vue.js', 'django', 'flask', 'spring boot', 'express.js', 'fastapi']:
                categories['Frameworks'].append(skill)
            elif skill_lower in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch']:
                categories['Databases'].append(skill)
            elif skill_lower in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible']:
                categories['DevOps & Cloud'].append(skill)
            elif skill_lower in ['html', 'css', 'scss', 'bootstrap', 'tailwind']:
                categories['Frontend Technologies'].append(skill)
            elif skill_lower in ['machine learning', 'ai', 'tensorflow', 'pytorch', 'scikit-learn']:
                categories['AI & ML'].append(skill)
            else:
                categories['Other Technologies'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _generate_skill_vector(self, skills: List[str]) -> List[float]:
        """Generate semantic skill vector"""
        if 'embeddings' in self.ai_models and skills:
            try:
                # Create skill text for embedding
                skill_text = " ".join(skills)
                embeddings = self.ai_models['embeddings'].encode([skill_text])
                return embeddings[0].tolist()[:50]  # Limit to 50 dimensions
            except Exception as e:
                logger.warning(f"Embedding generation failed: {str(e)}")
        
        # Fallback: simple skill presence vector
        return [1.0] * min(len(skills), 20)
    
    def _generate_ai_summary(self, text: str, skills: List[str]) -> str:
        """Generate AI summary of the resume"""
        skill_count = len(skills)
        main_skills = skills[:5] if skills else ["general skills"]
        
        return f"Professional with {skill_count} identified technical skills including {', '.join(main_skills)}. " \
               f"Strong background in technology with diverse skill set suitable for multiple roles."
    
    def _generate_ai_feedback(self, text: str, skills: List[str]) -> str:
        """Generate AI feedback on the resume"""
        if len(skills) >= 10:
            return "Excellent technical skill coverage. Resume demonstrates strong technical competency across multiple domains."
        elif len(skills) >= 5:
            return "Good technical skill foundation. Consider adding more specific project examples and certifications."
        else:
            return "Limited technical skills shown. Recommend highlighting more technologies and adding project details."
    
    def _generate_ai_suggestions(self, skills: List[str]) -> str:
        """Generate AI suggestions for improvement"""
        suggestions = []
        
        if not any('cloud' in skill.lower() or skill.lower() in ['aws', 'azure', 'gcp'] for skill in skills):
            suggestions.append("Consider adding cloud platform experience (AWS, Azure, GCP)")
        
        if not any(skill.lower() in ['docker', 'kubernetes'] for skill in skills):
            suggestions.append("Container technologies (Docker, Kubernetes) are highly valued")
        
        if not any('ai' in skill.lower() or 'ml' in skill.lower() for skill in skills):
            suggestions.append("AI/ML skills are increasingly important in the job market")
        
        return ". ".join(suggestions) if suggestions else "Strong skill set. Continue building expertise in emerging technologies."
    
    def _infer_roles_from_skills(self, skills: List[str]) -> List[str]:
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
    
    def _fallback_analysis(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        # Extract skills using pattern matching
        skills = self._extract_skills_ai(resume_text)
        skill_categories = self._categorize_skills(skills)
        
        return {
            "extracted_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text,
            "skills": skills,
            "skill_categories": skill_categories,
            "competencies": list(skill_categories.keys()),
            "roles": self._infer_roles_from_skills(skills),
            "skill_vector": [1.0] * len(skills),
            "ai_summary": f"Pattern-based analysis. Found {len(skills)} skills.",
            "ai_feedback": "Basic pattern matching analysis (fallback mode).",
            "ai_suggestions": "Consider adding more specific project examples.",
            "confidence_score": min(0.7, len(skills) / 15.0),
            "total_skills": len(skills),
            "analysis_method": "Fallback",
            "filename": filename,
            "success": True
        }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return {
            "ai_enabled": bool(self.ai_models),
            "capabilities": ["resume_analysis", "skill_extraction", "role_inference"],
            "ai_models": list(self.ai_models.keys()) if self.ai_models else [],
            "status": "ready"
        }

async def main():
    """Main function to handle JSON-RPC requests"""
    server = ProfessionalResumeAnalyzerServer()
    
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
