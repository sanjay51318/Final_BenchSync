import asyncio
import json
import numpy as np
from typing import Dict, Any, List
import pypdf
import io
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Import ML libraries with error handling
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class ConsultantProfilingAgent:
    """Full ML-powered consultant profiling agent"""
    
    def __init__(self):
        self.setup_nltk()
        self.setup_models()
    
    def setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            print(f"NLTK setup failed: {e}")
            self.stop_words = set()
    
    def setup_models(self):
        """Initialize all ML models with fallbacks"""
        # Initialize models if libraries are available
        if HAS_TRANSFORMERS:
            try:
                print("Loading NER model for skill extraction...")
                self.ner_pipeline = pipeline(
                    "ner", 
                    model="dslim/bert-base-NER", 
                    aggregation_strategy="simple"
                )
                
                print("Loading classification model for competency recognition...")
                self.classifier_pipeline = pipeline(
                    "zero-shot-classification", 
                    model="facebook/bart-large-mnli"
                )
                
                print("Loading generation model for insights...")
                self.generator_pipeline = pipeline(
                    "text-generation", 
                    model="distilgpt2"
                )
                
                self.has_ml_models = True
            except Exception as e:
                print(f"ML model setup failed: {e}")
                self.has_ml_models = False
        else:
            print("Transformers not available, using fallback methods")
            self.has_ml_models = False
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                print("Loading embedding model for skill vectorization...")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.has_embeddings = True
            except Exception as e:
                print(f"Embedding model setup failed: {e}")
                self.has_embeddings = False
        else:
            self.has_embeddings = False
        
        # Competency labels for consultant evaluation
        self.competency_labels = [
            "leadership", "problem solving", "communication", "teamwork", 
            "adaptability", "critical thinking", "creativity", "project management",
            "client management", "business analysis", "technical architecture"
        ]
        
        # Fallback technical skills list
        self.technical_keywords = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "sql", "postgresql", "mysql", "mongodb", "redis",
            "machine learning", "data science", "artificial intelligence",
            "spring boot", "django", "flask", "fastapi",
            "microservices", "rest api", "graphql",
            "agile", "scrum", "devops", "ci/cd",
            "salesforce", "sap", "oracle", "microsoft dynamics",
            "tableau", "power bi", "looker", "qlik",
            "blockchain", "solidity", "ethereum"
        ]
    
    async def analyze_consultant_profile(self, profile_content: str, consultant_name: str) -> Dict[str, Any]:
        """
        Analyze consultant profile and extract comprehensive information
        """
        try:
            # Extract text if PDF
            if profile_content.startswith('%PDF'):
                text = self.extract_text_from_pdf(io.BytesIO(profile_content.encode()))
            else:
                text = profile_content
            
            if not text:
                return {"success": False, "error": "Failed to extract text from profile"}
            
            # Preprocess text
            preprocessed_text = self.preprocess_text(text)
            
            # Extract information using NLP or fallback methods
            if self.has_ml_models:
                extracted_info = self.extract_consultant_information_ml(preprocessed_text)
            else:
                extracted_info = self.extract_consultant_information_fallback(preprocessed_text)
            
            # Generate skill embeddings
            if self.has_embeddings:
                skill_vector = self.generate_skill_embeddings(extracted_info)
            else:
                skill_vector = np.array([0.1] * 384)  # Dummy 384-dimensional vector
            
            # Generate AI insights
            ai_insights = self.generate_consultant_insights(extracted_info, consultant_name)
            
            # Calculate experience level
            experience_years = self.extract_experience_years(text)
            
            return {
                "success": True,
                "consultant_name": consultant_name,
                "technical_skills": extracted_info["technical_skills"],
                "soft_skills": extracted_info["soft_skills"],
                "certifications": extracted_info["certifications"],
                "experience_years": experience_years,
                "competencies": extracted_info["competencies"],
                "project_experience": extracted_info["project_experience"],
                "skill_vector": skill_vector.tolist(),
                "ai_summary": ai_insights["summary"],
                "strengths": ai_insights["strengths"],
                "recommendations": ai_insights["recommendations"],
                "suitability_areas": ai_insights["suitability_areas"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Profile analysis failed: {str(e)}"}
    
    def extract_text_from_pdf(self, file_stream):
        """Extract text from PDF stream"""
        try:
            reader = pypdf.PdfReader(file_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\+\-\#\.\\/]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_consultant_information_ml(self, text: str) -> Dict[str, List[str]]:
        """Extract skills using ML models"""
        try:
            # Technical skills extraction using NER
            ner_results = self.ner_pipeline(text)
            technical_skills = []
            
            if ner_results:
                for entity in ner_results:
                    word = entity['word'].replace('##', '').strip()
                    if entity['entity_group'] in ['MISC', 'ORG'] and len(word) > 1:
                        technical_skills.append(word.title())
            
            # Add keyword-based extraction
            for skill in self.technical_keywords:
                if skill in text:
                    if skill.lower() in ["aws", "gcp", "sql", "api", "rest", "c++", "c#", ".net"]:
                        technical_skills.append(skill.upper())
                    else:
                        technical_skills.append(skill.title())
            
            technical_skills = sorted(list(set([s.strip() for s in technical_skills if len(s.strip()) > 1])))
            
            # Competency extraction using zero-shot classification
            try:
                competency_results = self.classifier_pipeline(text, candidate_labels=self.competency_labels, multi_label=True)
                competencies = [
                    comp for comp, score in zip(competency_results['labels'], competency_results['scores'])
                    if score > 0.7
                ]
            except Exception as e:
                print(f"Competency extraction failed: {e}")
                competencies = []
            
            # Fallback for other extractions
            return self.extract_common_information(text, technical_skills, competencies)
            
        except Exception as e:
            print(f"ML extraction failed: {e}")
            return self.extract_consultant_information_fallback(text)
    
    def extract_consultant_information_fallback(self, text: str) -> Dict[str, List[str]]:
        """Extract skills using keyword matching fallback"""
        technical_skills = []
        
        # Extract technical skills using keywords
        for skill in self.technical_keywords:
            if skill in text:
                if skill.lower() in ["aws", "gcp", "sql", "api", "rest", "c++", "c#", ".net"]:
                    technical_skills.append(skill.upper())
                else:
                    technical_skills.append(skill.title())
        
        technical_skills = sorted(list(set([s.strip() for s in technical_skills if len(s.strip()) > 1])))
        
        # Basic competency extraction
        competencies = []
        for comp in self.competency_labels:
            if comp in text:
                competencies.append(comp)
        
        return self.extract_common_information(text, technical_skills, competencies)
    
    def extract_common_information(self, text: str, technical_skills: List[str], competencies: List[str]) -> Dict[str, List[str]]:
        """Extract common information regardless of method"""
        
        # Certifications extraction
        certifications = []
        cert_patterns = [
            r'(aws certified|azure certified|google cloud certified)',
            r'(pmp|prince2|agile certified|scrum master)',
            r'(cissp|cism|comptia|cissp)',
            r'(oracle certified|microsoft certified|salesforce certified)'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            certifications.extend([match.title() for match in matches])
        
        # Project experience extraction
        project_keywords = [
            "led team", "managed project", "delivered solution", "implemented system",
            "client engagement", "stakeholder management", "requirements gathering",
            "system design", "architecture", "digital transformation"
        ]
        
        project_experience = []
        for keyword in project_keywords:
            if keyword in text:
                project_experience.append(keyword.title())
        
        # Soft skills (consultant-focused)
        soft_skills_keywords = [
            "leadership", "communication", "presentation", "negotiation",
            "client relationship", "business analysis", "strategic thinking",
            "problem solving", "analytical thinking", "team collaboration"
        ]
        
        soft_skills = []
        for skill in soft_skills_keywords:
            if skill in text:
                soft_skills.append(skill.title())
        
        return {
            "technical_skills": technical_skills[:15],  # Top 15 skills
            "soft_skills": soft_skills,
            "certifications": list(set(certifications)),
            "competencies": competencies[:10],  # Top 10 competencies
            "project_experience": list(set(project_experience))
        }
    
    def extract_experience_years(self, text: str) -> float:
        """Extract years of experience from text"""
        patterns = [
            r'(\d+)\+?\s*years?\s*of?\s*experience',
            r'(\d+)\+?\s*years?\s*in',
            r'experience:\s*(\d+)\+?\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    return float(matches[0])
                except:
                    continue
        
        return 0.0
    
    def generate_skill_embeddings(self, extracted_info: Dict[str, List[str]]) -> np.ndarray:
        """Generate embeddings from consultant skills and competencies"""
        text_for_embedding = " ".join(
            extracted_info["technical_skills"] + 
            extracted_info["soft_skills"] + 
            extracted_info["competencies"] +
            extracted_info["project_experience"]
        )
        
        if not text_for_embedding.strip():
            return np.zeros(384)  # Default sentence-transformer dimension
        
        try:
            return self.embedding_model.encode(text_for_embedding)
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return np.array([0.1] * 384)  # Fallback vector
    
    def generate_consultant_insights(self, extracted_info: Dict[str, List[str]], consultant_name: str) -> Dict[str, str]:
        """Generate AI-powered insights about the consultant"""
        
        technical_skills = extracted_info["technical_skills"]
        soft_skills = extracted_info["soft_skills"]
        competencies = extracted_info["competencies"]
        
        # Generate summary
        summary = f"{consultant_name} demonstrates expertise in {len(technical_skills)} technical areas. "
        if technical_skills:
            summary += f"Key technical strengths include {', '.join(technical_skills[:5])}. "
        if competencies:
            summary += f"Strong competencies in {', '.join(competencies[:3])}."
        
        # Identify strengths
        strengths = []
        if len(technical_skills) >= 8:
            strengths.append("Broad technical skill portfolio")
        if "leadership" in competencies:
            strengths.append("Leadership capabilities")
        if "client management" in [s.lower() for s in soft_skills]:
            strengths.append("Client-facing experience")
        if any("cloud" in skill.lower() for skill in technical_skills):
            strengths.append("Cloud technology expertise")
        
        # Generate recommendations
        recommendations = []
        if len(technical_skills) < 5:
            recommendations.append("Expand technical skill portfolio")
        if "communication" not in competencies:
            recommendations.append("Develop communication and presentation skills")
        if not any("leadership" in comp.lower() for comp in competencies):
            recommendations.append("Consider leadership development programs")
        
        # Suitability areas
        suitability_areas = []
        if any(skill in ["Python", "Machine Learning", "Data Science"] for skill in technical_skills):
            suitability_areas.append("Data & Analytics Projects")
        if any(skill in ["AWS", "Azure", "Docker", "Kubernetes"] for skill in technical_skills):
            suitability_areas.append("Cloud Transformation Projects")
        if "leadership" in competencies and len(technical_skills) >= 5:
            suitability_areas.append("Technical Leadership Roles")
        if any("salesforce" in skill.lower() for skill in technical_skills):
            suitability_areas.append("CRM Implementation Projects")
        
        return {
            "summary": summary,
            "strengths": strengths,
            "recommendations": recommendations,
            "suitability_areas": suitability_areas
        }
