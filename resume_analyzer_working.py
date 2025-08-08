#!/usr/bin/env python3
"""
Resume Analyzer Module - AI-Powered Resume Analysis
Extracts skills, competencies, and generates AI insights from resume text
Uses available ML libraries with fallback strategies
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
import numpy as np

# Core dependencies
try:
    import PyPDF2
    HAS_PYPDF = True
except ImportError:
    try:
        import pypdf
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.tag import pos_tag
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

# AI/ML dependencies with fallbacks
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """AI-powered resume analysis with multiple LLM models and fallback strategies"""
    
    def __init__(self):
        """Initialize the analyzer with available models"""
        self.models_loaded = False
        self.bert_ner = None
        self.bert_classifier = None
        self.sentence_transformer = None
        self.gpt2_generator = None
        
        # Predefined skill lists for fallback
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'nosql'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'git'],
            'data': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'sklearn', 'matplotlib', 'tableau', 'powerbi'],
            'mobile': ['android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic'],
            'devops': ['ci/cd', 'jenkins', 'gitlab', 'github actions', 'ansible', 'puppet', 'chef']
        }
        
        self.soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'creativity',
            'adaptability', 'time management', 'critical thinking', 'collaboration',
            'project management', 'analytical thinking', 'decision making'
        ]
        
        # Initialize models if available
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models with fallback strategies"""
        try:
            if HAS_TRANSFORMERS:
                logger.info("Loading Transformers models...")
                
                # BERT NER for skill extraction (fallback to simpler model)
                try:
                    self.bert_ner = pipeline("ner", 
                                           model="dbmdz/bert-large-cased-finetuned-conll03-english",
                                           aggregation_strategy="simple")
                except Exception as e:
                    logger.warning(f"Failed to load BERT NER: {e}, using fallback")
                    try:
                        self.bert_ner = pipeline("ner", aggregation_strategy="simple")
                    except:
                        self.bert_ner = None
                
                # BART for classification (fallback to simpler model)
                try:
                    self.bert_classifier = pipeline("text-classification",
                                                   model="microsoft/DialoGPT-medium",
                                                   return_all_scores=True)
                except Exception as e:
                    logger.warning(f"Failed to load BART classifier: {e}, using fallback")
                    try:
                        self.bert_classifier = pipeline("text-classification", return_all_scores=True)
                    except:
                        self.bert_classifier = None
                
                # GPT-2 for text generation (fallback to simpler model)
                try:
                    self.gpt2_generator = pipeline("text-generation", 
                                                 model="gpt2",
                                                 max_length=50,
                                                 num_return_sequences=1)
                except Exception as e:
                    logger.warning(f"Failed to load GPT-2: {e}")
                    self.gpt2_generator = None
            
            if HAS_SENTENCE_TRANSFORMERS:
                logger.info("Loading SentenceTransformer...")
                try:
                    self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception as e:
                    logger.warning(f"Failed to load SentenceTransformer: {e}")
                    self.sentence_transformer = None
            
            self.models_loaded = True
            logger.info("Models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            self.models_loaded = False
    
    def extract_text_from_pdf(self, file_content: bytes, filename: str) -> str:
        """Extract text from PDF with fallback strategies"""
        try:
            if HAS_PYPDF:
                # Try PyPDF2 first
                try:
                    import PyPDF2
                    from io import BytesIO
                    pdf_file = BytesIO(file_content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
                except:
                    pass
                
                # Try pypdf as fallback
                try:
                    import pypdf
                    from io import BytesIO
                    pdf_file = BytesIO(file_content)
                    pdf_reader = pypdf.PdfReader(pdf_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    return text
                except:
                    pass
            
            # If PDF extraction fails, return placeholder
            return f"PDF text extraction not available. File: {filename}"
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return f"Error processing PDF: {str(e)}"
    
    def extract_skills_advanced(self, text: str) -> List[str]:
        """Extract skills using advanced NLP models"""
        skills = set()
        
        try:
            if self.bert_ner:
                # Use BERT NER to identify entities
                entities = self.bert_ner(text)
                for entity in entities:
                    if entity['entity_group'] in ['PER', 'ORG', 'MISC']:
                        word = entity['word'].lower()
                        if any(skill in word for category in self.technical_skills.values() for skill in category):
                            skills.add(word)
        except Exception as e:
            logger.warning(f"Advanced skill extraction failed: {e}")
        
        return list(skills)
    
    def extract_skills_basic(self, text: str) -> List[str]:
        """Extract skills using basic pattern matching"""
        skills = set()
        text_lower = text.lower()
        
        # Search for technical skills
        for category, skill_list in self.technical_skills.items():
            for skill in skill_list:
                if skill in text_lower:
                    skills.add(skill)
        
        # Look for common skill patterns
        skill_patterns = [
            r'\b(?:experience|skilled|proficient|expert|familiar)\s+(?:in|with)\s+([a-zA-Z0-9\+\-\.]+)',
            r'\b([a-zA-Z0-9\+\-\.]+)\s+(?:programming|development|framework|library)',
            r'(?:technologies|tools|languages):\s*([^.]+)',
        ]
        
        for pattern in skill_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                potential_skills = match.group(1).split(',')
                for skill in potential_skills:
                    skill = skill.strip()
                    if len(skill) > 2 and skill.isalpha():
                        skills.add(skill)
        
        return list(skills)
    
    def extract_competencies(self, text: str) -> List[str]:
        """Extract soft skills and competencies"""
        competencies = set()
        text_lower = text.lower()
        
        # Look for soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                competencies.add(skill)
        
        # Look for competency patterns
        competency_patterns = [
            r'\b(?:strong|excellent|good)\s+([a-zA-Z\s]+?)\s+(?:skills|abilities)',
            r'\b(?:responsible for|managed|led|coordinated)\s+([^.]+)',
        ]
        
        for pattern in competency_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                comp_text = match.group(1).strip()
                if any(soft_skill in comp_text for soft_skill in self.soft_skills):
                    for soft_skill in self.soft_skills:
                        if soft_skill in comp_text:
                            competencies.add(soft_skill)
        
        return list(competencies)
    
    def generate_skill_vector(self, skills: List[str]) -> List[float]:
        """Generate skill vector using available models"""
        try:
            if self.sentence_transformer and skills:
                # Use SentenceTransformer if available
                combined_skills = " ".join(skills)
                vector = self.sentence_transformer.encode(combined_skills)
                return vector.tolist()
            elif HAS_SKLEARN and skills:
                # Fallback to TF-IDF
                vectorizer = TfidfVectorizer(max_features=100)
                combined_skills = " ".join(skills)
                vector = vectorizer.fit_transform([combined_skills])
                return vector.toarray()[0].tolist()
            else:
                # Simple one-hot encoding fallback
                all_possible_skills = [skill for category in self.technical_skills.values() for skill in category]
                vector = [1.0 if skill in skills else 0.0 for skill in all_possible_skills[:50]]
                return vector
        except Exception as e:
            logger.warning(f"Vector generation failed: {e}")
            return [0.0] * 50  # Return zero vector as fallback
    
    def generate_ai_summary(self, text: str, skills: List[str]) -> str:
        """Generate AI summary of the resume"""
        try:
            if self.gpt2_generator:
                prompt = f"Professional summary: {text[:200]}... Skills: {', '.join(skills[:5])}"
                result = self.gpt2_generator(prompt, max_length=100, num_return_sequences=1)
                return result[0]['generated_text'][len(prompt):].strip()
        except Exception as e:
            logger.warning(f"AI summary generation failed: {e}")
        
        # Fallback summary
        skill_count = len(skills)
        primary_skills = skills[:3] if skills else ["various technical skills"]
        return f"Professional with {skill_count} identified skills including {', '.join(primary_skills)}. Resume shows experience across multiple domains with technical competencies."
    
    def generate_ai_feedback(self, text: str, skills: List[str]) -> str:
        """Generate AI feedback on the resume"""
        feedback_points = []
        
        # Basic analysis
        word_count = len(text.split())
        skill_count = len(skills)
        
        if word_count < 200:
            feedback_points.append("Resume could benefit from more detailed descriptions of experience and achievements.")
        
        if skill_count < 5:
            feedback_points.append("Consider adding more technical skills and competencies to strengthen your profile.")
        
        if not any(word in text.lower() for word in ['project', 'achieved', 'improved', 'managed']):
            feedback_points.append("Include more specific achievements and project outcomes to demonstrate impact.")
        
        if feedback_points:
            return " ".join(feedback_points)
        else:
            return "Well-structured resume with good coverage of skills and experience."
    
    def generate_ai_suggestions(self, skills: List[str]) -> str:
        """Generate AI-powered skill development suggestions"""
        suggestions = []
        
        # Analyze skill gaps
        has_web = any(skill in skills for skill in self.technical_skills['web'])
        has_data = any(skill in skills for skill in self.technical_skills['data'])
        has_cloud = any(skill in skills for skill in self.technical_skills['cloud'])
        
        if not has_cloud:
            suggestions.append("Consider learning cloud technologies like AWS or Azure to enhance your technical profile.")
        
        if has_web and not has_data:
            suggestions.append("Adding data analysis skills like Python pandas or SQL could complement your web development experience.")
        
        if len(skills) < 10:
            suggestions.append("Expanding your technical skill set with additional programming languages or frameworks could increase opportunities.")
        
        if not suggestions:
            suggestions.append("Continue building on your existing skills and stay updated with latest industry trends.")
        
        return " ".join(suggestions)
    
    def analyze_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Complete resume analysis with AI insights
        
        Args:
            file_content: PDF file content as bytes
            filename: Name of the uploaded file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract text from PDF
            extracted_text = self.extract_text_from_pdf(file_content, filename)
            
            if "Error" in extracted_text:
                return {"error": extracted_text}
            
            # Extract skills using available methods
            skills = []
            if self.models_loaded:
                skills.extend(self.extract_skills_advanced(extracted_text))
            skills.extend(self.extract_skills_basic(extracted_text))
            
            # Remove duplicates and clean
            skills = list(set([skill.strip().lower() for skill in skills if skill.strip()]))
            
            # Extract competencies
            competencies = self.extract_competencies(extracted_text)
            
            # Identify potential roles
            roles = []
            role_keywords = {
                'developer': ['developer', 'programmer', 'engineer', 'coding'],
                'analyst': ['analyst', 'analysis', 'data', 'research'],
                'manager': ['manager', 'lead', 'supervisor', 'director'],
                'designer': ['designer', 'design', 'ui', 'ux'],
                'consultant': ['consultant', 'advisor', 'specialist']
            }
            
            text_lower = extracted_text.lower()
            for role, keywords in role_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    roles.append(role)
            
            # Generate skill vector
            skill_vector = self.generate_skill_vector(skills)
            
            # Generate AI insights
            ai_summary = self.generate_ai_summary(extracted_text, skills)
            ai_feedback = self.generate_ai_feedback(extracted_text, skills)
            ai_suggestions = self.generate_ai_suggestions(skills)
            
            # Calculate confidence score
            confidence_score = min(1.0, (len(skills) * 0.1 + len(competencies) * 0.05) / 2.0)
            
            return {
                "success": True,
                "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                "skills": skills,
                "competencies": competencies,
                "roles": roles,
                "skill_vector": skill_vector,
                "ai_summary": ai_summary,
                "ai_feedback": ai_feedback,
                "ai_suggestions": ai_suggestions,
                "confidence_score": confidence_score,
                "analysis_metadata": {
                    "models_used": self.models_loaded,
                    "total_skills": len(skills),
                    "total_competencies": len(competencies),
                    "text_length": len(extracted_text)
                }
            }
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return {"error": f"Resume analysis failed: {str(e)}"}

# Global analyzer instance
_analyzer_instance = None

def get_resume_analyzer() -> ResumeAnalyzer:
    """Get the global resume analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ResumeAnalyzer()
    return _analyzer_instance

if __name__ == "__main__":
    # Test the analyzer
    analyzer = get_resume_analyzer()
    print("Resume Analyzer initialized successfully")
    print(f"Models loaded: {analyzer.models_loaded}")
    print(f"Available features: NLTK={HAS_NLTK}, Transformers={HAS_TRANSFORMERS}, SentenceTransformers={HAS_SENTENCE_TRANSFORMERS}")
