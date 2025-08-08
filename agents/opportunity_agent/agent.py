#!/usr/bin/env python3
"""
Opportunity Agent - AI-Powered Opportunity Management System
Uses Hugging Face models for intelligent opportunity matching and recommendations
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np

# AI/ML dependencies
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Database dependencies
from database.professional_connection import SessionLocal
from database.models.professional_models import (
    ProjectOpportunity, OpportunityApplication, ConsultantProfile, User
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpportunityAgent:
    """AI-Powered Opportunity Agent for intelligent matching and management"""
    
    def __init__(self):
        """Initialize the Opportunity Agent with AI models"""
        logger.info("Initializing Opportunity Agent with AI capabilities...")
        
        self.models_loaded = False
        self.similarity_model = None
        self.classification_model = None
        self.text_generator = None
        
        # Skill categories for analysis
        self.skill_categories = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'sklearn', 'tableau', 'powerbi'],
            'mobile': ['android', 'ios', 'react native', 'flutter', 'xamarin'],
            'devops': ['ci/cd', 'jenkins', 'gitlab', 'github actions', 'ansible']
        }
        
        # Experience level mapping
        self.experience_levels = {
            'junior': ['junior', 'entry', 'graduate', '0-2 years', 'fresher'],
            'mid': ['mid', 'intermediate', '2-5 years', 'experienced'],
            'senior': ['senior', 'lead', '5+ years', 'expert', 'principal'],
            'architect': ['architect', 'principal', 'staff', '10+ years']
        }
        
        # Initialize AI models
        self._initialize_ai_models()

    async def initialize(self):
        """Initialize AI models asynchronously (for FastAPI startup)"""
        try:
            logger.info("Async initialization of opportunity agent...")
            # AI models are already initialized in __init__
            logger.info("Opportunity agent async initialization complete")
        except Exception as e:
            logger.warning(f"Async initialization warning: {e}")
    
    def _initialize_ai_models(self):
        """Initialize AI models for opportunity analysis"""
        try:
            if HAS_TRANSFORMERS:
                logger.info("Loading AI models for opportunity analysis...")
                
                # Sentence Transformer for similarity matching
                try:
                    self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
                    logger.info("✅ SentenceTransformer loaded for opportunity matching")
                except Exception as e:
                    logger.warning(f"Failed to load SentenceTransformer: {e}")
                
                # Text classification for skill analysis
                try:
                    self.classification_model = pipeline(
                        "zero-shot-classification",
                        model="facebook/bart-large-mnli",
                        framework="pt",
                        device=-1  # CPU
                    )
                    logger.info("✅ BART classifier loaded for skill analysis")
                except Exception as e:
                    logger.warning(f"Failed to load BART classifier: {e}")
                
                # Text generation for recommendations
                try:
                    self.text_generator = pipeline(
                        "text-generation",
                        model="distilgpt2",
                        framework="pt",
                        device=-1  # CPU
                    )
                    logger.info("✅ GPT-2 generator loaded for recommendations")
                except Exception as e:
                    logger.warning(f"Failed to load GPT-2: {e}")
            
            self.models_loaded = any([
                self.similarity_model is not None,
                self.classification_model is not None,
                self.text_generator is not None
            ])
            
            logger.info(f"Opportunity Agent initialized. AI models loaded: {self.models_loaded}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
            self.models_loaded = False
    
    def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new opportunity with AI-enhanced analysis"""
        try:
            # Validate required fields
            required_fields = ['title', 'description', 'client_name', 'required_skills']
            for field in required_fields:
                if field not in opportunity_data:
                    return {"error": f"Missing required field: {field}"}
            
            # AI-enhanced processing
            if self.models_loaded:
                # Analyze and enhance the opportunity description
                enhanced_data = self._analyze_opportunity_with_ai(opportunity_data)
                opportunity_data.update(enhanced_data)
            
            # Store in database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Insert opportunity
                insert_query = """
                INSERT INTO opportunities (
                    title, description, client_name, required_skills, experience_level,
                    project_duration, budget_range, start_date, end_date, status,
                    skill_vector, ai_score, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                
                values = (
                    opportunity_data['title'],
                    opportunity_data['description'],
                    opportunity_data['client_name'],
                    opportunity_data['required_skills'],
                    opportunity_data.get('experience_level', 'mid'),
                    opportunity_data.get('project_duration', '3-6 months'),
                    opportunity_data.get('budget_range', 'Competitive'),
                    opportunity_data.get('start_date'),
                    opportunity_data.get('end_date'),
                    opportunity_data.get('status', 'open'),
                    opportunity_data.get('skill_vector', []),
                    opportunity_data.get('ai_score', 0.5),
                    datetime.now(),
                    datetime.now()
                )
                
                cursor.execute(insert_query, values)
                opportunity_id = cursor.fetchone()[0]
                conn.commit()
            
            # Find matching consultants
            matching_consultants = self.find_matching_consultants(opportunity_id)
            
            return {
                "success": True,
                "opportunity_id": opportunity_id,
                "message": "Opportunity created successfully",
                "matching_consultants": len(matching_consultants),
                "ai_enhanced": self.models_loaded
            }
            
        except Exception as e:
            logger.error(f"Error creating opportunity: {e}")
            return {"error": f"Failed to create opportunity: {str(e)}"}
    
    def _analyze_opportunity_with_ai(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze and enhance opportunity data"""
        enhanced_data = {}
        
        try:
            description = opportunity_data.get('description', '')
            required_skills = opportunity_data.get('required_skills', [])
            
            # Generate skill vector using SentenceTransformer
            if self.similarity_model:
                combined_text = f"{description} {' '.join(required_skills)}"
                skill_vector = self.similarity_model.encode(combined_text).tolist()
                enhanced_data['skill_vector'] = skill_vector
            
            # Classify experience level using BART
            if self.classification_model and description:
                experience_candidates = ['junior', 'mid-level', 'senior', 'architect']
                result = self.classification_model(description, experience_candidates)
                if result['scores'][0] > 0.5:
                    enhanced_data['ai_experience_level'] = result['labels'][0]
            
            # Calculate AI score based on description quality
            ai_score = self._calculate_opportunity_score(opportunity_data)
            enhanced_data['ai_score'] = ai_score
            
            # Generate AI recommendations
            recommendations = self._generate_ai_recommendations(opportunity_data)
            enhanced_data['ai_recommendations'] = recommendations
            
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
        
        return enhanced_data
    
    def _calculate_opportunity_score(self, opportunity_data: Dict[str, Any]) -> float:
        """Calculate AI-based opportunity score"""
        score = 0.5  # Base score
        
        description = opportunity_data.get('description', '')
        required_skills = opportunity_data.get('required_skills', [])
        
        # Description quality
        if len(description) > 100:
            score += 0.1
        if len(description) > 300:
            score += 0.1
        
        # Skills specificity
        if len(required_skills) >= 3:
            score += 0.1
        if len(required_skills) >= 5:
            score += 0.1
        
        # Budget information
        if 'budget_range' in opportunity_data and opportunity_data['budget_range'] != 'Competitive':
            score += 0.1
        
        # Timeline clarity
        if 'start_date' in opportunity_data and 'end_date' in opportunity_data:
            score += 0.1
        
        return min(1.0, score)
    
    def _generate_ai_recommendations(self, opportunity_data: Dict[str, Any]) -> str:
        """Generate AI-powered recommendations for the opportunity"""
        try:
            if self.text_generator:
                required_skills = opportunity_data.get('required_skills', [])
                prompt = f"Opportunity recommendations for project requiring {', '.join(required_skills[:3])}:"
                
                result = self.text_generator(
                    prompt,
                    max_length=80,
                    num_return_sequences=1,
                    temperature=0.7,
                    pad_token_id=self.text_generator.tokenizer.eos_token_id
                )
                
                generated_text = result[0]['generated_text'][len(prompt):].strip()
                return generated_text if len(generated_text) > 10 else "Consider detailed skill requirements for better matching"
            
        except Exception as e:
            logger.warning(f"AI recommendation generation failed: {e}")
        
        return "Ensure clear skill requirements and project timeline for optimal consultant matching"
    
    def find_matching_consultants(self, opportunity_id: int) -> List[Dict[str, Any]]:
        """Find consultants matching an opportunity using AI similarity"""
        try:
            # Get opportunity details
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Fetch opportunity
                cursor.execute("""
                    SELECT title, description, required_skills, skill_vector, experience_level
                    FROM opportunities WHERE id = %s
                """, (opportunity_id,))
                
                opportunity = cursor.fetchone()
                if not opportunity:
                    return []
                
                title, description, required_skills, skill_vector, exp_level = opportunity
                
                # Fetch all consultants with their skills
                cursor.execute("""
                    SELECT id, name, email, skills, skill_vector, experience_level, bench_status
                    FROM consultants WHERE bench_status = 'available'
                """)
                
                consultants = cursor.fetchall()
            
            matching_consultants = []
            
            for consultant in consultants:
                cons_id, name, email, cons_skills, cons_skill_vector, cons_exp, bench_status = consultant
                
                # Calculate match score
                match_score = self._calculate_match_score(
                    required_skills, cons_skills,
                    skill_vector, cons_skill_vector,
                    exp_level, cons_exp
                )
                
                if match_score > 0.3:  # Threshold for matching
                    matching_consultants.append({
                        'consultant_id': cons_id,
                        'name': name,
                        'email': email,
                        'match_score': round(match_score, 2),
                        'skills': cons_skills,
                        'experience_level': cons_exp
                    })
            
            # Sort by match score
            matching_consultants.sort(key=lambda x: x['match_score'], reverse=True)
            
            return matching_consultants[:10]  # Top 10 matches
            
        except Exception as e:
            logger.error(f"Error finding matching consultants: {e}")
            return []
    
    def _calculate_match_score(self, req_skills, cons_skills, req_vector, cons_vector, req_exp, cons_exp):
        """Calculate match score between opportunity and consultant"""
        score = 0.0
        
        try:
            # Skill overlap score (40% weight)
            if req_skills and cons_skills:
                # Convert to sets for comparison
                if isinstance(req_skills, list):
                    req_set = set([s.lower().strip() for s in req_skills])
                else:
                    req_set = set([s.lower().strip() for s in req_skills.split(',')])
                
                if isinstance(cons_skills, list):
                    cons_set = set([s.lower().strip() for s in cons_skills])
                else:
                    cons_set = set([s.lower().strip() for s in cons_skills.split(',')])
                
                overlap = len(req_set.intersection(cons_set))
                total_required = len(req_set)
                
                if total_required > 0:
                    skill_score = overlap / total_required
                    score += skill_score * 0.4
            
            # Vector similarity score (40% weight)
            if req_vector and cons_vector and self.similarity_model:
                try:
                    if isinstance(req_vector, list) and isinstance(cons_vector, list):
                        req_arr = np.array(req_vector).reshape(1, -1)
                        cons_arr = np.array(cons_vector).reshape(1, -1)
                        
                        similarity = cosine_similarity(req_arr, cons_arr)[0][0]
                        score += similarity * 0.4
                except:
                    pass
            
            # Experience level score (20% weight)
            exp_score = self._compare_experience_levels(req_exp, cons_exp)
            score += exp_score * 0.2
            
        except Exception as e:
            logger.warning(f"Error calculating match score: {e}")
        
        return min(1.0, max(0.0, score))
    
    def _compare_experience_levels(self, required_level, consultant_level):
        """Compare experience levels and return compatibility score"""
        level_hierarchy = {'junior': 1, 'mid': 2, 'senior': 3, 'architect': 4}
        
        req_level = level_hierarchy.get(required_level, 2)
        cons_level = level_hierarchy.get(consultant_level, 2)
        
        if cons_level >= req_level:
            return 1.0  # Consultant meets or exceeds requirement
        elif cons_level == req_level - 1:
            return 0.7  # One level below
        else:
            return 0.3  # More than one level below
    
    def get_all_opportunities(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """Get all opportunities with optional status filter"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if status_filter:
                    query = "SELECT * FROM opportunities WHERE status = %s ORDER BY created_at DESC"
                    cursor.execute(query, (status_filter,))
                else:
                    query = "SELECT * FROM opportunities ORDER BY created_at DESC"
                    cursor.execute(query)
                
                opportunities = cursor.fetchall()
                
                # Convert to dict format
                opportunity_list = []
                for opp in opportunities:
                    opportunity_dict = {
                        'id': opp[0],
                        'title': opp[1],
                        'description': opp[2],
                        'client_name': opp[3],
                        'required_skills': opp[4],
                        'experience_level': opp[5],
                        'project_duration': opp[6],
                        'budget_range': opp[7],
                        'start_date': opp[8].isoformat() if opp[8] else None,
                        'end_date': opp[9].isoformat() if opp[9] else None,
                        'status': opp[10],
                        'ai_score': opp[12] if len(opp) > 12 else 0.5,
                        'created_at': opp[13].isoformat() if len(opp) > 13 and opp[13] else None,
                        'updated_at': opp[14].isoformat() if len(opp) > 14 and opp[14] else None
                    }
                    opportunity_list.append(opportunity_dict)
                
                return opportunity_list
                
        except Exception as e:
            logger.error(f"Error getting opportunities: {e}")
            return []
    
    def get_opportunities_for_consultant(self, consultant_email: str) -> List[Dict[str, Any]]:
        """Get personalized opportunities for a specific consultant using AI matching"""
        try:
            # Get consultant details
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, skills, skill_vector, experience_level, bench_status
                    FROM consultants WHERE email = %s
                """, (consultant_email,))
                
                consultant = cursor.fetchone()
                if not consultant:
                    return []
                
                cons_id, cons_skills, cons_skill_vector, cons_exp, bench_status = consultant
                
                # Get all open opportunities
                cursor.execute("""
                    SELECT id, title, description, required_skills, skill_vector, 
                           experience_level, client_name, project_duration, budget_range,
                           start_date, end_date, ai_score
                    FROM opportunities WHERE status = 'open'
                    ORDER BY created_at DESC
                """)
                
                opportunities = cursor.fetchall()
            
            # Calculate match scores for each opportunity
            personalized_opportunities = []
            
            for opp in opportunities:
                opp_id, title, desc, req_skills, req_vector, req_exp, client, duration, budget, start_date, end_date, ai_score = opp
                
                match_score = self._calculate_match_score(
                    req_skills, cons_skills,
                    req_vector, cons_skill_vector,
                    req_exp, cons_exp
                )
                
                # Only include opportunities with reasonable match
                if match_score > 0.2:
                    opportunity_data = {
                        'id': opp_id,
                        'title': title,
                        'description': desc,
                        'client_name': client,
                        'required_skills': req_skills,
                        'experience_level': req_exp,
                        'project_duration': duration,
                        'budget_range': budget,
                        'start_date': start_date.isoformat() if start_date else None,
                        'end_date': end_date.isoformat() if end_date else None,
                        'match_score': round(match_score, 2),
                        'ai_score': ai_score or 0.5,
                        'match_level': self._get_match_level(match_score)
                    }
                    personalized_opportunities.append(opportunity_data)
            
            # Sort by match score
            personalized_opportunities.sort(key=lambda x: x['match_score'], reverse=True)
            
            return personalized_opportunities[:20]  # Top 20 matches
            
        except Exception as e:
            logger.error(f"Error getting opportunities for consultant: {e}")
            return []
    
    def _get_match_level(self, match_score: float) -> str:
        """Convert match score to human-readable level"""
        if match_score >= 0.8:
            return "Excellent Match"
        elif match_score >= 0.6:
            return "Good Match"
        elif match_score >= 0.4:
            return "Fair Match"
        else:
            return "Potential Match"
    
    def update_opportunity_status(self, opportunity_id: int, new_status: str) -> Dict[str, Any]:
        """Update opportunity status"""
        try:
            valid_statuses = ['open', 'in_progress', 'filled', 'cancelled', 'on_hold']
            if new_status not in valid_statuses:
                return {"error": f"Invalid status. Must be one of: {valid_statuses}"}
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE opportunities 
                    SET status = %s, updated_at = %s 
                    WHERE id = %s
                """, (new_status, datetime.now(), opportunity_id))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    return {"success": True, "message": "Opportunity status updated"}
                else:
                    return {"error": "Opportunity not found"}
                    
        except Exception as e:
            logger.error(f"Error updating opportunity status: {e}")
            return {"error": f"Failed to update status: {str(e)}"}
    
    def get_opportunity_analytics(self) -> Dict[str, Any]:
        """Get analytics and insights about opportunities using AI"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Basic metrics
                cursor.execute("SELECT COUNT(*) FROM opportunities")
                total_opportunities = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM opportunities WHERE status = 'open'")
                open_opportunities = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM opportunities WHERE status = 'filled'")
                filled_opportunities = cursor.fetchone()[0]
                
                # Top skills demand
                cursor.execute("""
                    SELECT required_skills, COUNT(*) as demand_count
                    FROM opportunities 
                    WHERE status = 'open'
                    GROUP BY required_skills
                    ORDER BY demand_count DESC
                    LIMIT 10
                """)
                skills_demand = cursor.fetchall()
                
                # Average AI scores
                cursor.execute("SELECT AVG(ai_score) FROM opportunities WHERE ai_score IS NOT NULL")
                avg_ai_score = cursor.fetchone()[0] or 0.5
                
                return {
                    "total_opportunities": total_opportunities,
                    "open_opportunities": open_opportunities,
                    "filled_opportunities": filled_opportunities,
                    "fill_rate": round((filled_opportunities / total_opportunities * 100), 2) if total_opportunities > 0 else 0,
                    "average_ai_score": round(avg_ai_score, 2),
                    "top_skills_demand": [{"skill": skill, "demand": count} for skill, count in skills_demand[:5]],
                    "ai_models_active": self.models_loaded
                }
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": "Failed to get analytics"}

# Global opportunity agent instance
_opportunity_agent_instance = None

def get_opportunity_agent() -> OpportunityAgent:
    """Get the global opportunity agent instance"""
    global _opportunity_agent_instance
    if _opportunity_agent_instance is None:
        _opportunity_agent_instance = OpportunityAgent()
    return _opportunity_agent_instance

if __name__ == "__main__":
    # Test the opportunity agent
    agent = get_opportunity_agent()
    print("Opportunity Agent initialized successfully!")
    print(f"AI models loaded: {agent.models_loaded}")
