"""
Resume Analysis Agent - Core AI Pipeline
Extracted from Resume_Agent.ipynb for MCP server integration
"""
import re
import os
import numpy as np
import pypdf
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
from typing import Dict, List, Any
import io

# Force PyTorch backend and disable TensorFlow
os.environ["TRANSFORMERS_BACKEND"] = "pt"
os.environ["USE_TF"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force CPU usage

# Import with error handling
HAS_AI_MODELS = False
try:
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    HAS_AI_MODELS = True
except Exception as e:
    logging.warning(f"AI models not available: {e}")
    HAS_AI_MODELS = False

logger = logging.getLogger(__name__)

class ResumeAnalysisAgent:
    """Core AI analysis engine from Resume_Agent.ipynb"""
    
    def __init__(self):
        self.models_loaded = False
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize the exact same models as in Resume_Agent.ipynb"""
        if not HAS_AI_MODELS:
            logger.warning("AI models not available - using fallback analysis")
            self.models_loaded = False
            return
            
        try:
            # Download NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            self.stop_words = set(stopwords.words('english'))
            
            logger.info("Loading NER model 'dslim/bert-base-NER' for skill extraction")
            self.ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
            
            logger.info("Loading Zero-Shot Classification model 'facebook/bart-large-mnli' for competency recognition")
            self.candidate_labels = ["leadership", "problem solving", "communication", "teamwork", "adaptability", "critical thinking", "creativity", "agile scrum"]
            self.classifier_pipeline = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            
            logger.info("Loading Sentence-Transformer model 'all-MiniLM-L6-v2' for skill vectorization...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("Loading text generation model 'distilgpt2' for suggestions...")
            self.generator_pipeline = pipeline("text-generation", model="distilgpt2")
            
            self.models_loaded = True
            logger.info("✅ All AI models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            self.models_loaded = False
    
    def extract_text_from_pdf(self, file_stream):
        """Extract text from PDF file"""
        text = ""
        try:
            reader = pypdf.PdfReader(file_stream)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
        return text
    
    def _text_preprocessing(self, text: str) -> str:
        """Exact copy from Resume_Agent.ipynb"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\+\-\#\.\/]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _tokenize_and_normalize(self, text: str) -> List[str]:
        """Exact copy from Resume_Agent.ipynb"""
        tokens = word_tokenize(text)
        filtered_tokens = [word for word in tokens if word not in self.stop_words and len(word) > 1]
        return filtered_tokens
    
    def _nlp_processing_huggingface(self, raw_text: str) -> Dict[str, Any]:
        """Exact copy from Resume_Agent.ipynb"""
        logger.info("--- NLP Processing (Hugging Face) ---")

        ner_results = self.ner_pipeline(raw_text)
        extracted_skills = []

        if ner_results:
            for entity in ner_results:
                word = entity['word'].replace('##', '').strip()
                if entity['entity_group'] in ['MISC', 'ORG', 'LOC'] and len(word) > 1:
                    extracted_skills.append(word)

        common_skill_keywords = [
            "python", "java", "sql", "aws", "azure", "gcp", "docker", "kubernetes", "fastapi", "spring boot", "react", "angular", "vue.js",
            "machine learning", "deep learning", "data analysis", "javascript", "html", "css",
            "devops", "agile", "scrum", "project management", "tensorflow", "pytorch", "nlp",
            "etl", "api", "rest", "git", "linux", "cloud computing", "database", "postgresql",
            "mysql", "mongodb", "c++", "c#", ".net", "tableau", "power bi", "excel", "spark", "hadoop"
        ]

        for skill_kw in common_skill_keywords:
            if re.search(r'\b' + re.escape(skill_kw) + r'\b', raw_text.lower()):
                if skill_kw.lower() in ["aws", "gcp", "sql", "nlp", "etl", "api", "rest", "c++", "c#", ".net"]:
                    extracted_skills.append(skill_kw.upper())
                else:
                    extracted_skills.append(skill_kw.capitalize())

        final_skills = sorted(list(set([s.strip() for s in extracted_skills if len(s.strip()) > 1])))

        competency_results = self.classifier_pipeline(raw_text, candidate_labels=self.candidate_labels, multi_label=True)
        extracted_competencies = [
            competency for competency, score in zip(competency_results['labels'], competency_results['scores'])
            if score > 0.75
        ]

        mock_roles = []
        role_keywords = {
            "software engineer": "Software Engineer",
            "software developer": "Software Developer",
            "data scientist": "Data Scientist",
            "data analyst": "Data Analyst",
            "project manager": "Project Manager",
            "devops engineer": "DevOps Engineer",
            "machine learning engineer": "ML Engineer"
        }

        for keyword, role in role_keywords.items():
            if keyword in raw_text.lower():
                mock_roles.append(role)

        extracted_info = {
            "skills": final_skills,
            "competencies": sorted(list(set(extracted_competencies))),
            "roles": sorted(list(set(mock_roles)))
        }
        logger.info(f"Extracted Info: {extracted_info}")
        return extracted_info
    
    def _skill_vectorization_embeddings(self, extracted_info: Dict[str, Any]) -> np.ndarray:
        """Exact copy from Resume_Agent.ipynb"""
        logger.info("--- Skill Vectorization/Embeddings ---")
        text_for_embedding = " ".join(extracted_info["skills"] + extracted_info["competencies"] + extracted_info["roles"])

        if not text_for_embedding.strip():
            logger.info("No text for embedding, returning zero vector.")
            return np.zeros(self.embedding_model.get_sentence_embedding_dimension())

        skill_vector = self.embedding_model.encode(text_for_embedding)
        logger.info(f"Generated Skill Vector (first 5 elements): {skill_vector[:5]}...")
        return skill_vector
    
    def _generative_ai_suggestions(self, context_data: Dict[str, Any]) -> Dict[str, str]:
        """Exact copy from Resume_Agent.ipynb"""
        skills_list = context_data.get('skills', [])
        competencies_list = context_data.get('competencies', [])
        roles_list = context_data.get('roles', [])

        ai_summary = f"This resume highlights strong skills in {', '.join(skills_list[:5]) if skills_list else 'various technical areas'}. "
        if competencies_list:
            ai_summary += f"Key competencies include {', '.join(competencies_list[:3])}. "
        if roles_list:
            ai_summary += f"Relevant experience includes {', '.join(roles_list)}."

        skill_recommendations = set()
        tech_skills = [s.lower() for s in skills_list]

        if any(skill in tech_skills for skill in ['python', 'java', 'javascript', 'programming']):
            skill_recommendations.update(['Docker', 'Kubernetes', 'Git Advanced', 'Unit Testing'])

        if any(skill in tech_skills for skill in ['machine learning', 'data science', 'data analysis']):
            skill_recommendations.update(['Apache Spark', 'Tableau', 'R Programming', 'Statistical Modeling'])

        if any(skill in tech_skills for skill in ['aws', 'cloud', 'azure', 'gcp']):
            skill_recommendations.update(['Terraform', 'CloudFormation', 'Serverless Architecture'])

        if any(skill in tech_skills for skill in ['database', 'sql', 'mysql', 'mongodb']):
            skill_recommendations.update(['Data Warehousing', 'ETL Tools', 'Apache Kafka'])

        if any(skill in tech_skills for skill in ['web', 'frontend', 'react', 'angular']):
            skill_recommendations.update(['TypeScript', 'GraphQL', 'Redux', 'Testing Frameworks'])

        if not skill_recommendations:
            skill_recommendations = {'Version Control', 'Agile Methodologies', 'Problem Solving', 'Technical Documentation'}

        skill_recommendations = list(skill_recommendations)[:6]

        feedback_items = []
        if len(skills_list) >= 5:
            feedback_items.append("Strong technical skill portfolio demonstrated")
        else:
            feedback_items.append("Consider expanding technical skill set")

        if competencies_list:
            feedback_items.append("Good balance of soft skills present")
        else:
            feedback_items.append("Include more leadership and communication skills")

        if roles_list:
            feedback_items.append("Clear career direction indicated")
        else:
            feedback_items.append("Consider highlighting specific role aspirations")

        try:
            prompt_text = f"Career development for {', '.join(roles_list[:1]) if roles_list else 'technology professional'}:"

            generated_result = self.generator_pipeline(
                prompt_text,
                max_new_tokens=60,
                num_return_sequences=1,
                do_sample=True,
                top_k=30,
                top_p=0.85,
                temperature=0.7,
                pad_token_id=self.generator_pipeline.tokenizer.eos_token_id,
                truncation=True,
                return_full_text=False
            )

            ai_advice = generated_result[0]['generated_text'].strip()
            ai_advice = re.sub(r'^\W+', '', ai_advice)
            ai_advice = re.sub(r'[^\w\s\.,!?-]', '', ai_advice)
            ai_advice = ' '.join(ai_advice.split()[:25])

            if len(ai_advice) < 15:
                ai_advice = "Focus on continuous learning and stay updated with industry trends"

        except Exception as e:
            logger.error(f"Text generation error: {e}")
            ai_advice = "Focus on building expertise in your core skills while expanding into complementary areas"

        final_suggestions = f"Recommended skills to develop: {', '.join(skill_recommendations)}. {ai_advice}"

        return {
            "summary": ai_summary,
            "feedback": '. '.join(feedback_items) + '.',
            "suggestions": final_suggestions
        }
    
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
        
        return {k: v for k, v in categories.items() if v}
    
    def analyze_resume_full_pipeline(self, resume_text: str, filename: str = "resume.txt") -> Dict[str, Any]:
        """Complete analysis pipeline using Resume_Agent.ipynb logic"""
        if not self.models_loaded:
            raise Exception("AI models not loaded")
        
        try:
            # Step 1: Preprocessing (exact copy from notebook)
            preprocessed_text = self._text_preprocessing(resume_text)
            tokens = self._tokenize_and_normalize(preprocessed_text)
            
            # Step 2: NLP Processing (exact copy from notebook)
            extracted_info = self._nlp_processing_huggingface(preprocessed_text)
            
            # Step 3: Skill Vectorization (exact copy from notebook)
            numerical_skill_vectors = self._skill_vectorization_embeddings(extracted_info)
            
            # Step 4: AI Suggestions (exact copy from notebook)
            ai_generated_insights = self._generative_ai_suggestions(extracted_info)
            
            # Return complete result in MCP format
            return {
                "success": True,
                "filename": filename,
                "skills": extracted_info["skills"],
                "soft_skills": extracted_info["competencies"],
                "competencies": extracted_info["competencies"],
                "roles": extracted_info["roles"],
                "skill_categories": self._categorize_skills(extracted_info["skills"]),
                "skill_vector": numerical_skill_vectors.tolist(),
                "ai_summary": ai_generated_insights["summary"],
                "ai_feedback": ai_generated_insights["feedback"],
                "ai_suggestions": ai_generated_insights["suggestions"],
                "confidence_score": min(0.9, len(extracted_info["skills"]) / 15.0),
                "total_skills": len(extracted_info["skills"]),
                "analysis_method": "Resume_Agent_AI_Pipeline",
                "extracted_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text
            }
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            raise e

    def analyze_from_file_upload(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Analyze resume from uploaded file content"""
        try:
            if filename.lower().endswith('.pdf'):
                # Extract text from PDF
                file_stream = io.BytesIO(file_content)
                resume_text = self.extract_text_from_pdf(file_stream)
                if not resume_text:
                    raise Exception("Failed to extract text from PDF")
            else:
                # Assume it's a text file
                resume_text = file_content.decode('utf-8')
            
            return self.analyze_resume_full_pipeline(resume_text, filename)
            
        except Exception as e:
            logger.error(f"File analysis failed: {e}")
            raise e
