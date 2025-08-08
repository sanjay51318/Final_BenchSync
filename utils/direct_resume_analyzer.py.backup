"""
Direct Resume Analyzer Interface
Simple wrapper that imports the analyzer class directly to preserve all AI functionality
"""
import sys
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DirectResumeAnalyzer:
    """Direct interface to Resume Analyzer - preserves all AI/LLM functionality"""
    
    def __init__(self):
        self.analyzer = None
        self._initialize_analyzer()
    
    def _initialize_analyzer(self):
        """Initialize the resume analyzer directly"""
        try:
            # Add the mcp_servers directory to path
            mcp_servers_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_servers")
            if mcp_servers_path not in sys.path:
                sys.path.append(mcp_servers_path)
            
            # Import and initialize the analyzer class directly
            from professional_resume_analyzer_server import ResumeAnalyzerMCP
            self.analyzer = ResumeAnalyzerMCP()
            
            logger.info(f"✅ Resume Analyzer initialized - AI capabilities: {self.analyzer.has_ai}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Resume Analyzer: {str(e)}")
            self.analyzer = None
    
    async def analyze_resume(self, resume_text: str, filename: str = "resume.txt") -> Dict[str, Any]:
        """Analyze resume using the full AI-powered analyzer"""
        try:
            if not self.analyzer:
                return self._fallback_analysis(resume_text, filename)
            
            # Use AI-enhanced analysis if available, otherwise basic
            if self.analyzer.has_ai:
                result = self.analyzer.extract_skills_advanced(resume_text)
                analysis_method = "AI-Enhanced"
            else:
                result = self.analyzer.extract_skills_basic(resume_text)
                analysis_method = "Pattern-Based"
            
            # Format the result to match expected output
            formatted_result = {
                "extracted_text": resume_text,
                "skills": result.get("skills", []),
                "skill_categories": result.get("skill_categories", {}),
                "competencies": list(result.get("skill_categories", {}).keys()),
                "roles": self.analyzer._infer_roles_from_skills(result.get("skills", [])),
                "skill_vector": self._generate_skill_vector(result.get("skills", [])),
                "ai_summary": self._generate_summary(result, analysis_method),
                "ai_feedback": self._generate_feedback(result, analysis_method),
                "ai_suggestions": self.analyzer._generate_ai_suggestions(
                    result.get("skills", []), 
                    result.get("skill_categories", {})
                ),
                "confidence_score": result.get("confidence_score", 0.8),
                "total_skills": len(result.get("skills", [])),
                "analysis_method": analysis_method,
                "filename": filename,
                "success": True
            }
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {str(e)}")
            return self._fallback_analysis(resume_text, filename)
    
    def _generate_skill_vector(self, skills: List[str]) -> List[float]:
        """Generate a simple skill vector"""
        return [1.0] * len(skills) if skills else [0.0]
    
    def _generate_summary(self, result: Dict, method: str) -> str:
        """Generate AI summary"""
        skill_count = len(result.get("skills", []))
        categories = len(result.get("skill_categories", {}))
        
        if method == "AI-Enhanced":
            return f"AI analysis completed. Identified {skill_count} skills across {categories} categories using advanced NLP models."
        else:
            return f"Pattern-based analysis completed. Found {skill_count} skills across {categories} categories."
    
    def _generate_feedback(self, result: Dict, method: str) -> str:
        """Generate feedback"""
        if method == "AI-Enhanced":
            return "Advanced AI analysis with transformers and NLP models successfully applied."
        else:
            return "Pattern-based analysis completed successfully."
    
    def _fallback_analysis(self, resume_text: str, filename: str) -> Dict[str, Any]:
        """Simple fallback analysis"""
        # Basic skill extraction using simple patterns
        basic_skills = []
        skill_patterns = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue',
            'django', 'flask', 'spring', 'node.js', 'express',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'aws', 'azure', 'docker', 'kubernetes', 'jenkins',
            'git', 'github', 'gitlab', 'ci/cd', 'devops'
        ]
        
        text_lower = resume_text.lower()
        for skill in skill_patterns:
            if skill.lower() in text_lower:
                basic_skills.append(skill.title())
        
        return {
            "extracted_text": resume_text,
            "skills": basic_skills,
            "skill_categories": {"General": basic_skills},
            "competencies": ["General"],
            "roles": ["Software Developer"],
            "skill_vector": [1.0] * len(basic_skills),
            "ai_summary": f"Fallback analysis. Found {len(basic_skills)} skills.",
            "ai_feedback": "Basic pattern matching analysis (fallback mode).",
            "ai_suggestions": "Consider adding more specific project examples.",
            "confidence_score": 0.6,
            "total_skills": len(basic_skills),
            "analysis_method": "Fallback",
            "filename": filename,
            "success": True
        }
    
    async def get_server_capabilities(self) -> Dict[str, Any]:
        """Get analyzer capabilities"""
        if self.analyzer:
            return {
                "has_ai_capabilities": self.analyzer.has_ai,
                "available_models": {
                    "ner_model": hasattr(self.analyzer, 'ner_pipeline') and self.analyzer.ner_pipeline is not None,
                    "similarity_model": hasattr(self.analyzer, 'similarity_model') and self.analyzer.similarity_model is not None,
                    "text_classifier": hasattr(self.analyzer, 'text_classifier') and self.analyzer.text_classifier is not None
                },
                "supported_features": [
                    "AI-powered skill extraction",
                    "Named Entity Recognition", 
                    "Skill categorization",
                    "Role inference",
                    "Semantic similarity"
                ],
                "status": "ready"
            }
        else:
            return {
                "has_ai_capabilities": False,
                "error": "Analyzer not initialized",
                "status": "error"
            }
