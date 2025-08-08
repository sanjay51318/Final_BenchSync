import asyncio
import json
import re
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

from database.models.consultant import Consultant
from database.models.resume_data import ResumeData, ConsultantSkill

logger = logging.getLogger(__name__)

class ResumeSkillExtractor:
    def __init__(self):
        self.skill_extractor = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the AI models for skill extraction"""
        if self.initialized:
            return
            
        try:
            # Load NER model for skill extraction
            model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"
            self.skill_extractor = pipeline(
                "ner", 
                model=model_name, 
                tokenizer=model_name,
                aggregation_strategy="simple"
            )
            self.initialized = True
            logger.info("Resume skill extractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize skill extractor: {e}")
            self.initialized = False

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from resume text using NER and pattern matching"""
        skills = set()
        
        # Technical skills patterns
        tech_patterns = [
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|PHP|Ruby|Go|Rust|Swift|Kotlin|TypeScript)\b',
            r'\b(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel)\b',
            r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|Oracle)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab)\b',
            r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy|Matplotlib)\b',
            r'\b(?:HTML|CSS|SASS|LESS|Bootstrap|Tailwind|Material-UI)\b',
            r'\b(?:REST|API|GraphQL|Microservices|DevOps|CI/CD|Agile|Scrum)\b'
        ]
        
        # Extract using patterns
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update([match.strip() for match in matches])
        
        # Extract using NER if available
        if self.initialized and self.skill_extractor:
            try:
                entities = self.skill_extractor(text)
                for entity in entities:
                    if entity['entity_group'] in ['MISC', 'ORG'] and len(entity['word']) > 2:
                        # Filter for technology-related entities
                        word = entity['word'].strip()
                        if self._is_technical_skill(word):
                            skills.add(word)
            except Exception as e:
                logger.warning(f"NER extraction failed: {e}")
        
        return list(skills)

    def _is_technical_skill(self, word: str) -> bool:
        """Check if a word is likely a technical skill"""
        tech_keywords = [
            'programming', 'development', 'framework', 'library', 'database',
            'cloud', 'api', 'service', 'platform', 'tool', 'technology'
        ]
        
        # Basic filters
        if len(word) < 2 or word.lower() in ['the', 'and', 'or', 'but', 'in', 'on', 'at']:
            return False
            
        # Check if it's a known technology pattern
        word_lower = word.lower()
        return any(keyword in word_lower for keyword in tech_keywords) or \
               any(char.isupper() for char in word) or \
               '.' in word or \
               word_lower in ['sql', 'api', 'ui', 'ux', 'ai', 'ml', 'ci', 'cd']

    def extract_experience_info(self, text: str) -> Dict[str, Any]:
        """Extract experience information from resume text"""
        experience_info = {
            'total_years': 0,
            'positions': [],
            'companies': [],
            'technologies_used': []
        }
        
        # Extract years of experience
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience\s*:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming)'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    years = max([int(match) for match in matches])
                    experience_info['total_years'] = years
                    break
                except ValueError:
                    continue
        
        # Extract job titles/positions
        position_patterns = [
            r'(?:senior|lead|principal|junior)?\s*(?:software|web|full.?stack|back.?end|front.?end)?\s*(?:engineer|developer|programmer|architect)',
            r'(?:data|machine learning|ai)\s*(?:scientist|engineer|analyst)',
            r'(?:devops|cloud|system)\s*(?:engineer|architect|administrator)',
            r'(?:project|product|technical)\s*(?:manager|lead)'
        ]
        
        for pattern in position_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            experience_info['positions'].extend([match.strip().title() for match in matches])
        
        return experience_info

    def extract_education_info(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text"""
        education = []
        
        # Degree patterns
        degree_patterns = [
            r'(?:bachelor|master|phd|doctorate|associate).*?(?:science|arts|engineering|technology)',
            r'(?:b\.s\.|m\.s\.|ph\.d\.|b\.a\.|m\.a\.).*?(?:computer|software|electrical|mechanical)',
            r'(?:btech|mtech|be|me)\s*(?:computer|software|electrical|information)'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'degree': match.strip().title(),
                    'field': 'Technology',
                    'year': ''
                })
        
        return education

    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different types"""
        categories = {
            'programming_languages': [],
            'frameworks': [],
            'databases': [],
            'cloud_platforms': [],
            'tools': [],
            'methodologies': [],
            'other': []
        }
        
        skill_mappings = {
            'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript'],
            'frameworks': ['react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle'],
            'cloud_platforms': ['aws', 'azure', 'gcp', 'google cloud', 'amazon web services'],
            'tools': ['docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab'],
            'methodologies': ['agile', 'scrum', 'devops', 'ci/cd', 'rest', 'api', 'microservices']
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized = False
            
            for category, keywords in skill_mappings.items():
                if any(keyword in skill_lower for keyword in keywords):
                    categories[category].append(skill)
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(skill)
        
        return categories

    async def process_resume(self, db: Session, consultant_id: int, resume_text: str, filename: str, file_path: str) -> Dict[str, Any]:
        """Process resume and extract all relevant information"""
        try:
            # Extract information
            skills = self.extract_skills_from_text(resume_text)
            experience_info = self.extract_experience_info(resume_text)
            education_info = self.extract_education_info(resume_text)
            categorized_skills = self.categorize_skills(skills)
            
            # Create or update resume data record
            existing_resume = db.query(ResumeData).filter(
                ResumeData.consultant_id == consultant_id
            ).first()
            
            if existing_resume:
                # Update existing record
                existing_resume.original_filename = filename
                existing_resume.file_path = file_path
                existing_resume.extracted_skills = skills
                existing_resume.extracted_experience = experience_info
                existing_resume.extracted_education = education_info
                existing_resume.processing_status = "processed"
                existing_resume.updated_at = datetime.utcnow()
                resume_data = existing_resume
            else:
                # Create new record
                resume_data = ResumeData(
                    consultant_id=consultant_id,
                    original_filename=filename,
                    file_path=file_path,
                    extracted_skills=skills,
                    extracted_experience=experience_info,
                    extracted_education=education_info,
                    processing_status="processed"
                )
                db.add(resume_data)
            
            # Update or add skills to consultant_skills table
            await self._update_consultant_skills(db, consultant_id, categorized_skills)
            
            # Update consultant main record
            consultant = db.query(Consultant).filter(Consultant.id == consultant_id).first()
            if consultant:
                # Merge skills with existing ones
                existing_tech_skills = consultant.technical_skills or []
                all_tech_skills = list(set(existing_tech_skills + skills))
                consultant.technical_skills = all_tech_skills
                
                # Update experience if extracted value is higher
                if experience_info['total_years'] > (consultant.years_of_experience or 0):
                    consultant.years_of_experience = experience_info['total_years']
                
                consultant.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                'success': True,
                'skills_extracted': len(skills),
                'new_skills': skills,
                'categorized_skills': categorized_skills,
                'experience_years': experience_info['total_years'],
                'education_count': len(education_info)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing resume for consultant {consultant_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _update_consultant_skills(self, db: Session, consultant_id: int, categorized_skills: Dict[str, List[str]]):
        """Update consultant skills without deleting existing ones"""
        for category, skills in categorized_skills.items():
            for skill in skills:
                # Check if skill already exists
                existing_skill = db.query(ConsultantSkill).filter(
                    ConsultantSkill.consultant_id == consultant_id,
                    ConsultantSkill.skill_name.ilike(skill)
                ).first()
                
                if not existing_skill:
                    # Add new skill
                    new_skill = ConsultantSkill(
                        consultant_id=consultant_id,
                        skill_name=skill.title(),
                        skill_category=category,
                        source="resume",
                        confidence_score=85,  # Medium confidence for extracted skills
                        proficiency_level="intermediate"  # Default level
                    )
                    db.add(new_skill)
                else:
                    # Update existing skill if it was manual entry
                    if existing_skill.source == "manual":
                        existing_skill.source = "resume_verified"
                        existing_skill.updated_at = datetime.utcnow()

# Global instance
resume_skill_extractor = ResumeSkillExtractor()
