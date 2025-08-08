#!/usr/bin/env python3
"""
Resume Analyzer Module
Integrated from Resume_Agent.ipynb for backend use
"""
import os
# Force PyTorch backend for transformers to avoid TensorFlow DLL issues
os.environ["TRANSFORMERS_BACKEND"] = "pt"
os.environ["USE_TF"] = "0"

import io
import re
import numpy as np
import pypdf
import torch
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import warnings
from datetime import datetime
warnings.filterwarnings("ignore")

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

stop_words = set(stopwords.words('english'))

class ResumeAnalyzer:
    def __init__(self):
        print("Loading AI models for resume analysis (PyTorch backend)...")
        
        # Force PyTorch device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load models with PyTorch backend explicitly
        print("Loading NER model 'dslim/bert-base-NER' for skill extraction")
        self.ner_pipeline = pipeline(
            "ner", 
            model="dslim/bert-base-NER", 
            aggregation_strategy="simple",
            framework="pt",  # Force PyTorch
            device=0 if torch.cuda.is_available() else -1
        )

        print("Loading Zero-Shot Classification model 'facebook/bart-large-mnli' for competency recognition")
        self.candidate_labels = ["leadership", "problem solving", "communication", "teamwork", "adaptability", "critical thinking", "creativity", "agile scrum"]
        self.classifier_pipeline = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli",
            framework="pt",  # Force PyTorch
            device=0 if torch.cuda.is_available() else -1
        )

        print("Loading Sentence-Transformer model 'all-MiniLM-L6-v2' for skill vectorization...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        print("Loading text generation model 'distilgpt2' for suggestions...")
        self.generator_pipeline = pipeline(
            "text-generation", 
            model="distilgpt2",
            framework="pt",  # Force PyTorch
            device=0 if torch.cuda.is_available() else -1
        )
        
        print("Resume analyzer models loaded successfully with PyTorch backend!")

    def extract_text_from_pdf(self, file_content):
        """Extract text from PDF file content"""
        text = ""
        try:
            file_stream = io.BytesIO(file_content)
            reader = pypdf.PdfReader(file_stream)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None
        return text

    def extract_text_from_txt(self, file_content):
        """Extract text from TXT file content"""
        try:
            if isinstance(file_content, bytes):
                text = file_content.decode('utf-8')
            else:
                text = str(file_content)
            return text
        except Exception as e:
            print(f"Error extracting text from TXT: {e}")
            return None

    def _text_preprocessing(self, text: str) -> str:
        """Preprocess text for analysis"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\+\-\#\.\/]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _tokenize_and_normalize(self, text: str) -> list:
        """Tokenize and normalize text"""
        tokens = word_tokenize(text)
        filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
        return filtered_tokens

    def _nlp_processing_huggingface(self, raw_text: str) -> dict:
        """Process text using Hugging Face models to extract skills, competencies, and roles"""
        print("Processing resume text with NLP models...")

        # Extract skills using NER
        ner_results = self.ner_pipeline(raw_text)
        extracted_skills = []

        if ner_results:
            for entity in ner_results:
                word = entity['word'].replace('##', '').strip()
                if entity['entity_group'] in ['MISC', 'ORG', 'LOC'] and len(word) > 1:
                    extracted_skills.append(word)

        # Add common technical skills
        common_skill_keywords = [
            "python", "java", "sql", "aws", "azure", "gcp", "docker", "kubernetes", "fastapi", "spring boot", "react", "angular", "vue.js",
            "machine learning", "deep learning", "data analysis", "javascript", "html", "css",
            "devops", "agile", "scrum", "project management", "tensorflow", "pytorch", "nlp",
            "etl", "api", "rest", "git", "linux", "cloud computing", "database", "postgresql",
            "mysql", "mongodb", "c++", "c#", ".net", "tableau", "power bi", "excel", "spark", "hadoop",
            "node.js", "express", "django", "flask", "redis", "elasticsearch", "jenkins", "terraform",
            "microservices", "graphql", "typescript", "vue", "sass", "webpack", "npm", "yarn"
        ]

        for skill_kw in common_skill_keywords:
            if re.search(r'\b' + re.escape(skill_kw) + r'\b', raw_text.lower()):
                if skill_kw.lower() in ["aws", "gcp", "sql", "nlp", "etl", "api", "rest", "c++", "c#", ".net"]:
                    extracted_skills.append(skill_kw.upper())
                else:
                    extracted_skills.append(skill_kw.capitalize())

        final_skills = sorted(list(set([s.strip() for s in extracted_skills if len(s.strip()) > 1])))

        # Extract competencies
        competency_results = self.classifier_pipeline(raw_text, candidate_labels=self.candidate_labels, multi_label=True)
        extracted_competencies = [
            competency for competency, score in zip(competency_results['labels'], competency_results['scores'])
            if score > 0.7
        ]

        # Extract potential roles
        mock_roles = []
        role_keywords = {
            "software engineer": "Software Engineer",
            "software developer": "Software Developer", 
            "data scientist": "Data Scientist",
            "data analyst": "Data Analyst",
            "project manager": "Project Manager",
            "devops engineer": "DevOps Engineer",
            "machine learning engineer": "ML Engineer",
            "frontend developer": "Frontend Developer",
            "backend developer": "Backend Developer",
            "full stack developer": "Full Stack Developer",
            "cloud engineer": "Cloud Engineer",
            "database administrator": "Database Administrator"
        }

        for keyword, role in role_keywords.items():
            if keyword in raw_text.lower():
                mock_roles.append(role)

        extracted_info = {
            "skills": final_skills,
            "competencies": sorted(list(set(extracted_competencies))),
            "roles": sorted(list(set(mock_roles)))
        }
        
        return extracted_info

    def _skill_vectorization_embeddings(self, extracted_info: dict) -> np.ndarray:
        """Generate skill vector embeddings"""
        text_for_embedding = " ".join(extracted_info["skills"] + extracted_info["competencies"] + extracted_info["roles"])

        if not text_for_embedding.strip():
            return np.zeros(self.embedding_model.get_sentence_embedding_dimension())

        skill_vector = self.embedding_model.encode(text_for_embedding)
        return skill_vector

    def _generative_ai_suggestions(self, context_data: dict) -> dict:
        """Generate AI suggestions and feedback"""
        skills_list = context_data.get('skills', [])
        competencies_list = context_data.get('competencies', [])
        roles_list = context_data.get('roles', [])

        # Generate AI summary
        ai_summary = f"This resume highlights strong skills in {', '.join(skills_list[:5]) if skills_list else 'various technical areas'}. "
        if competencies_list:
            ai_summary += f"Key competencies include {', '.join(competencies_list[:3])}. "
        if roles_list:
            ai_summary += f"Relevant experience includes {', '.join(roles_list)}."

        # Generate skill recommendations
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

        # Generate feedback
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

        # Generate AI advice using text generation
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
            print(f"Text generation error: {e}")
            ai_advice = "Focus on building expertise in your core skills while expanding into complementary areas"

        final_suggestions = f"Recommended skills to develop: {', '.join(skill_recommendations)}. {ai_advice}"

        return {
            "summary": ai_summary,
            "feedback": '. '.join(feedback_items) + '.',
            "suggestions": final_suggestions
        }

    def analyze_resume(self, file_content, filename):
        """Main function to analyze a resume"""
        try:
            # Extract text based on file type
            if filename.endswith('.pdf'):
                extracted_text = self.extract_text_from_pdf(file_content)
            elif filename.endswith('.txt'):
                extracted_text = self.extract_text_from_txt(file_content)
            else:
                return {"error": "Unsupported file type"}
                
            if not extracted_text:
                return {"error": "Failed to extract text from file"}

            # Preprocess text
            preprocessed_text = self._text_preprocessing(extracted_text)
            
            # Extract information using NLP
            extracted_info = self._nlp_processing_huggingface(preprocessed_text)
            
            # Generate skill vector
            skill_vector = self._skill_vectorization_embeddings(extracted_info)
            
            # Generate AI insights
            ai_insights = self._generative_ai_suggestions(extracted_info)

            # Return comprehensive analysis
            return {
                "filename": filename,
                "extracted_text": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text,
                "skills": extracted_info["skills"],
                "competencies": extracted_info["competencies"], 
                "roles": extracted_info["roles"],
                "skill_vector": skill_vector.tolist(),
                "ai_summary": ai_insights["summary"],
                "ai_feedback": ai_insights["feedback"],
                "ai_suggestions": ai_insights["suggestions"],
                "processing_time": datetime.now().isoformat(),
                "confidence_score": 0.85  # Mock confidence score
            }

        except Exception as e:
            return {"error": f"Resume analysis failed: {str(e)}"}

# Global analyzer instance
resume_analyzer = None

def get_resume_analyzer():
    """Get or create resume analyzer instance"""
    global resume_analyzer
    if resume_analyzer is None:
        resume_analyzer = ResumeAnalyzer()
    return resume_analyzer
