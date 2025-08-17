#!/usr/bin/env python3
"""
Professional Pool Database Connection
PostgreSQL database connection for consultant management system
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models.professional_models import (
    Base, ConsultantProfile, ProjectOpportunity, OpportunityApplication, 
    OpportunitySkillGap, ConsultantAssignment, User, ConsultantSkill
)

# Set up logging
logger = logging.getLogger(__name__)

# Database setup - PostgreSQL configuration
DATABASE_URL = "postgresql://postgres:2005@localhost:5432/consultant_bench_db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_url():
    """Get database URL"""
    return DATABASE_URL

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Professional database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection
def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

class ProfessionalDatabase:
    """Database operations for professional consultant management"""
    
    def __init__(self):
        try:
            self.engine = engine
            self.SessionLocal = SessionLocal
            
            # Test database connection
            test_session = self.SessionLocal()
            test_session.close()
            print("✅ Database connection established successfully")
        except Exception as e:
            print(f"⚠️ Database connection issue: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def get_session(self):
        """Get database session"""
        if not hasattr(self, 'SessionLocal') or self.SessionLocal is None:
            raise AttributeError("SessionLocal not properly initialized")
        return self.SessionLocal()
    
    def get_all_consultants(self):
        """Get all consultants from PostgreSQL database"""
        try:
            from database.models.professional_models import User, ConsultantProfile
            
            session = self.get_session()
            try:
                # Get all consultant users with their profiles
                consultant_users = session.query(User).filter(User.role == 'consultant').all()
                
                consultants = []
                for user in consultant_users:
                    # Get consultant profile
                    profile = session.query(ConsultantProfile).filter(
                        ConsultantProfile.user_id == user.id
                    ).first()
                    
                    # Build consultant data
                    consultant_data = {
                        'id': str(profile.id) if profile else user.id,
                        'user_id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'department': user.department or 'Not specified',
                        'primary_skill': profile.primary_skill if profile else 'Not specified',
                        'experience_years': profile.experience_years if profile else 0,
                        'status': profile.current_status if profile else 'available',
                        'attendance_rate': profile.attendance_rate if profile else 0.0,
                        'training_status': profile.training_status if profile else 'not-started',
                        'availability_status': profile.current_status if profile else 'available',
                        'resume_uploaded': profile.resume_status == 'updated' if profile else False,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'updated_at': user.updated_at.isoformat() if user.updated_at else None
                    }
                    consultants.append(consultant_data)
                
                return consultants
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error getting consultants from PostgreSQL: {e}")
            return []
    
    def get_consultant(self, consultant_id):
        """Get consultant by ID from PostgreSQL"""
        try:
            from database.models.professional_models import User, ConsultantProfile
            
            session = self.get_session()
            try:
                # Try to find by profile ID first
                profile = session.query(ConsultantProfile).filter(
                    ConsultantProfile.id == int(consultant_id)
                ).first()
                
                if profile:
                    user = session.query(User).filter(User.id == profile.user_id).first()
                    if user:
                        return {
                            'id': str(profile.id),
                            'user_id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'department': user.department or 'Not specified',
                            'primary_skill': profile.primary_skill,
                            'experience_years': profile.experience_years,
                            'status': profile.current_status,
                            'attendance_rate': profile.attendance_rate,
                            'training_status': profile.training_status,
                            'availability_status': profile.current_status,
                            'resume_uploaded': profile.resume_status == 'updated',
                            'created_at': user.created_at.isoformat() if user.created_at else None,
                            'updated_at': user.updated_at.isoformat() if user.updated_at else None
                        }
                
                return None
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error getting consultant from PostgreSQL: {e}")
            return None
    
    def add_consultant(self, **kwargs):
        """Add new consultant to PostgreSQL database"""
        try:
            from database.models.professional_models import User, ConsultantProfile
            import uuid
            from datetime import datetime
            
            session = self.get_session()
            try:
                # Check if user already exists
                existing_user = session.query(User).filter(User.email == kwargs.get('email')).first()
                if existing_user:
                    return existing_user.id
                
                # Create new user
                new_user = User(
                    id=str(uuid.uuid4()),
                    name=kwargs.get('name', ''),
                    email=kwargs.get('email', ''),
                    password_hash='password123',  # Default password
                    role='consultant',
                    department=kwargs.get('department', ''),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(new_user)
                session.flush()  # Get the user ID
                
                # Create consultant profile
                new_profile = ConsultantProfile(
                    user_id=new_user.id,
                    primary_skill=kwargs.get('primary_skill', ''),
                    experience_years=kwargs.get('experience_years', 0),
                    resume_status=kwargs.get('resume_status', 'pending'),
                    attendance_rate=kwargs.get('attendance_rate', 0.0),
                    training_status=kwargs.get('training_status', 'not-started'),
                    opportunities_count=0,
                    current_status=kwargs.get('availability_status', 'available'),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(new_profile)
                session.commit()
                
                return new_profile.id
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error adding consultant to PostgreSQL: {e}")
            return None

    def update_consultant(self, consultant_id, **kwargs):
        """Update consultant in PostgreSQL"""
        try:
            from database.models.professional_models import User, ConsultantProfile
            
            session = self.get_session()
            try:
                # Find consultant profile
                profile = session.query(ConsultantProfile).filter(
                    ConsultantProfile.id == int(consultant_id)
                ).first()
                
                if not profile:
                    return False
                
                # Update profile fields
                if 'primary_skill' in kwargs:
                    profile.primary_skill = kwargs['primary_skill']
                if 'experience_years' in kwargs:
                    profile.experience_years = kwargs['experience_years']
                if 'training_status' in kwargs:
                    profile.training_status = kwargs['training_status']
                if 'current_status' in kwargs:
                    profile.current_status = kwargs['current_status']
                if 'attendance_rate' in kwargs:
                    profile.attendance_rate = kwargs['attendance_rate']
                
                # Update user fields
                user = session.query(User).filter(User.id == profile.user_id).first()
                if user:
                    if 'name' in kwargs:
                        user.name = kwargs['name']
                    if 'department' in kwargs:
                        user.department = kwargs['department']
                
                session.commit()
                return True
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error updating consultant in PostgreSQL: {e}")
            return False

    def remove_consultant(self, consultant_id):
        """Remove consultant from PostgreSQL"""
        try:
            from database.models.professional_models import User, ConsultantProfile
            
            session = self.get_session()
            try:
                # Find and remove consultant profile
                profile = session.query(ConsultantProfile).filter(
                    ConsultantProfile.id == int(consultant_id)
                ).first()
                
                if profile:
                    session.delete(profile)
                    session.commit()
                    return True
                    
                return False
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error removing consultant from PostgreSQL: {e}")
            return False

    def get_consultant_skills(self, consultant_id):
        """Get consultant skills"""
        try:
            # First try to get from database
            return self.get_consultant_skills_from_db(consultant_id)
        except Exception as e:
            print(f"Error getting consultant skills: {e}")
            return []
    
    def add_consultant_skill(self, consultant_id, skill_name, proficiency_level, skill_category):
        """Add skill to consultant"""
        try:
            from database.models.professional_models import ConsultantSkill
            
            if hasattr(self, 'SessionLocal') and self.SessionLocal:
                session = self.SessionLocal()
                try:
                    # Check if skill already exists
                    existing_skill = session.query(ConsultantSkill).filter(
                        ConsultantSkill.consultant_id == consultant_id,
                        ConsultantSkill.skill_name == skill_name
                    ).first()
                    
                    if existing_skill:
                        # Update existing skill
                        existing_skill.proficiency_level = proficiency_level
                        existing_skill.skill_category = skill_category
                        existing_skill.updated_at = datetime.now()
                    else:
                        # Create new skill
                        skill = ConsultantSkill(
                            consultant_id=consultant_id,
                            skill_name=skill_name,
                            skill_category=skill_category,
                            proficiency_level=proficiency_level,
                            source='manual'
                        )
                        session.add(skill)
                    
                    session.commit()
                    print(f"✅ Added/Updated skill {skill_name} for consultant {consultant_id}")
                    return True
                finally:
                    session.close()
            else:
                print(f"Warning: Database not available, skill {skill_name} not persisted")
                return True
        except Exception as e:
            print(f"Error adding consultant skill: {e}")
            raise e

    def remove_consultant_skills(self, consultant_id):
        """Remove all skills for consultant"""
        try:
            from database.models.professional_models import ConsultantSkill
            
            if hasattr(self, 'SessionLocal') and self.SessionLocal:
                session = self.SessionLocal()
                try:
                    # Remove all skills for consultant
                    session.query(ConsultantSkill).filter(
                        ConsultantSkill.consultant_id == consultant_id
                    ).delete()
                    session.commit()
                    print(f"✅ Removed all skills for consultant {consultant_id}")
                    return True
                finally:
                    session.close()
            else:
                print(f"Warning: Database not available, skills for consultant {consultant_id} not removed")
                return True
        except Exception as e:
            print(f"Error removing consultant skills: {e}")
            raise e

    def get_consultant_skills_from_db(self, consultant_id):
        """Get consultant skills from database"""
        try:
            from database.models.professional_models import ConsultantSkill
            
            if hasattr(self, 'SessionLocal') and self.SessionLocal:
                session = self.SessionLocal()
                try:
                    skills = session.query(ConsultantSkill).filter(
                        ConsultantSkill.consultant_id == consultant_id
                    ).all()
                    
                    return [{
                        'skill_name': skill.skill_name,
                        'skill_category': skill.skill_category,
                        'proficiency_level': skill.proficiency_level,
                        'years_experience': skill.years_experience or 0,
                        'source': skill.source,
                        'confidence_score': skill.confidence_score or 0,
                        'is_primary': skill.is_primary or False,
                        'created_at': skill.created_at.isoformat() if skill.created_at else None,
                        'updated_at': skill.updated_at.isoformat() if skill.updated_at else None
                    } for skill in skills]
                    
                finally:
                    session.close()
            else:
                # Fallback to mock data if database not available
                return self.get_consultant_skills(consultant_id)
                
        except Exception as e:
            print(f"Error getting consultant skills from database: {e}")
            # Fallback to mock data
            return self.get_consultant_skills(consultant_id)

    def update_consultant_skill(self, consultant_id, skill_name, proficiency_level=None, years_experience=None, is_primary=None):
        """Update a specific consultant skill"""
        try:
            from database.models.professional_models import ConsultantSkill
            
            if hasattr(self, 'SessionLocal') and self.SessionLocal:
                session = self.SessionLocal()
                try:
                    skill = session.query(ConsultantSkill).filter(
                        ConsultantSkill.consultant_id == consultant_id,
                        ConsultantSkill.skill_name == skill_name
                    ).first()
                    
                    if skill:
                        if proficiency_level is not None:
                            skill.proficiency_level = proficiency_level
                        if years_experience is not None:
                            skill.years_experience = years_experience
                        if is_primary is not None:
                            skill.is_primary = is_primary
                        skill.updated_at = datetime.now()
                        
                        session.commit()
                        print(f"✅ Updated skill {skill_name} for consultant {consultant_id}")
                        return True
                    else:
                        print(f"⚠️ Skill {skill_name} not found for consultant {consultant_id}")
                        return False
                        
                finally:
                    session.close()
            else:
                print(f"Warning: Database not available, skill {skill_name} not updated")
                return True
                
        except Exception as e:
            print(f"Error updating consultant skill: {e}")
            raise e

    def add_skills_from_resume(self, consultant_id, extracted_skills, source='resume'):
        """Add skills extracted from resume analysis"""
        try:
            from database.models.professional_models import ConsultantSkill
            
            if hasattr(self, 'SessionLocal') and self.SessionLocal:
                session = self.SessionLocal()
                try:
                    added_skills = []
                    for skill_data in extracted_skills:
                        skill_name = skill_data.get('skill_name', '')
                        confidence = skill_data.get('confidence_score', 80)
                        proficiency = skill_data.get('proficiency_level', 'intermediate')
                        category = skill_data.get('category', 'technical')
                        
                        if skill_name:
                            # Check if skill already exists
                            existing_skill = session.query(ConsultantSkill).filter(
                                ConsultantSkill.consultant_id == consultant_id,
                                ConsultantSkill.skill_name == skill_name
                            ).first()
                            
                            if not existing_skill:
                                # Create new skill
                                skill = ConsultantSkill(
                                    consultant_id=consultant_id,
                                    skill_name=skill_name,
                                    skill_category=category,
                                    proficiency_level=proficiency,
                                    source=source,
                                    confidence_score=confidence
                                )
                                session.add(skill)
                                added_skills.append(skill_name)
                            else:
                                # Update if source is more reliable
                                if source == 'resume' and existing_skill.source == 'manual':
                                    existing_skill.confidence_score = max(existing_skill.confidence_score or 0, confidence)
                                    existing_skill.updated_at = datetime.now()
                    
                    session.commit()
                    print(f"✅ Added {len(added_skills)} skills from {source} for consultant {consultant_id}")
                    return added_skills
                    
                finally:
                    session.close()
            else:
                print(f"Warning: Database not available, skills from {source} not persisted")
                return []
                
        except Exception as e:
            print(f"Error adding skills from {source}: {e}")
            raise e

    def get_consultant_skills_from_db(self, consultant_id):
        """Get consultant skills from PostgreSQL database"""
        db = SessionLocal()
        try:
            from database.models.professional_models import ConsultantSkill
            
            skills = db.query(ConsultantSkill).filter(
                ConsultantSkill.consultant_id == consultant_id
            ).order_by(ConsultantSkill.confidence_score.desc()).all()
            
            skill_data = []
            for skill in skills:
                skill_data.append({
                    'id': skill.id,
                    'skill_name': skill.skill_name,
                    'category': skill.skill_category,
                    'proficiency_level': skill.proficiency_level,
                    'confidence_score': skill.confidence_score,
                    'source': skill.source,
                    'years_experience': skill.years_experience,
                    'is_primary': skill.is_primary,
                    'created_at': skill.created_at.isoformat() if skill.created_at else None,
                    'updated_at': skill.updated_at.isoformat() if skill.updated_at else None
                })
            
            return skill_data
            
        except Exception as e:
            logger.error(f"Error getting consultant skills from DB: {e}")
            return []
        finally:
            db.close()
    
    def get_resume_analysis_from_db(self, consultant_id):
        """Get resume analysis from PostgreSQL database"""
        db = SessionLocal()
        try:
            from database.models.professional_models import ResumeAnalysis
            
            analysis = db.query(ResumeAnalysis).filter(
                ResumeAnalysis.consultant_id == consultant_id
            ).order_by(ResumeAnalysis.created_at.desc()).first()
            
            if analysis:
                return {
                    'id': analysis.id,
                    'consultant_id': analysis.consultant_id,
                    'file_name': analysis.file_name,
                    'extracted_text': analysis.extracted_text[:1000] + "..." if len(analysis.extracted_text or "") > 1000 else analysis.extracted_text,
                    'skills': analysis.extracted_skills or [],
                    'soft_skills': analysis.extracted_competencies or [],
                    'competencies': analysis.extracted_competencies or [],
                    'roles': analysis.identified_roles or [],
                    'skill_vector': analysis.skill_vector or [],
                    'ai_summary': analysis.ai_summary,
                    'ai_feedback': analysis.ai_feedback,
                    'ai_suggestions': analysis.ai_suggestions,
                    'confidence_score': analysis.confidence_score,
                    'analysis_method': 'Resume_Agent_AI_Pipeline',
                    'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
                    'updated_at': analysis.updated_at.isoformat() if analysis.updated_at else None
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting resume analysis from DB: {e}")
            return None
        finally:
            db.close()
    
    def sync_consultant_data_with_analysis(self, consultant_id):
        """Synchronize consultant profile with latest resume analysis"""
        db = SessionLocal()
        try:
            from database.models.professional_models import ConsultantProfile, ResumeAnalysis
            
            # Get latest resume analysis
            analysis = db.query(ResumeAnalysis).filter(
                ResumeAnalysis.consultant_id == consultant_id
            ).order_by(ResumeAnalysis.created_at.desc()).first()
            
            if analysis:
                # Update consultant profile with analysis data
                consultant = db.query(ConsultantProfile).filter(
                    ConsultantProfile.id == consultant_id
                ).first()
                
                if consultant:
                    # Update primary skill from analysis
                    if analysis.extracted_skills:
                        consultant.primary_skill = analysis.extracted_skills[0]
                    
                    # Update resume status
                    consultant.resume_status = 'updated'
                    consultant.updated_at = datetime.now()
                    
                    db.commit()
                    
                    logger.info(f"✅ Consultant {consultant_id} profile synchronized with resume analysis")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error syncing consultant data: {e}")
            return False
        finally:
            db.close()
    
    def get_all_consultants_with_real_skills(self):
        """Get all consultants with their real skills from database"""
        db = SessionLocal()
        try:
            from database.models.professional_models import ConsultantProfile, User, ConsultantSkill, ResumeAnalysis
            
            consultants = []
            profiles = db.query(ConsultantProfile).join(User).all()
            
            for profile in profiles:
                # Get real skills from database
                skills = db.query(ConsultantSkill).filter(
                    ConsultantSkill.consultant_id == profile.id
                ).order_by(ConsultantSkill.confidence_score.desc()).limit(10).all()
                
                # Get latest resume analysis
                analysis = db.query(ResumeAnalysis).filter(
                    ResumeAnalysis.consultant_id == profile.id
                ).order_by(ResumeAnalysis.created_at.desc()).first()
                
                consultant_data = {
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'name': profile.user.name,
                    'email': profile.user.email,
                    'primary_skill': profile.primary_skill,
                    'experience_years': profile.experience_years,
                    'current_status': profile.current_status,
                    'resume_status': profile.resume_status,
                    'real_skills': [
                        {
                            'skill_name': skill.skill_name,
                            'category': skill.skill_category,
                            'proficiency_level': skill.proficiency_level,
                            'confidence_score': skill.confidence_score,
                            'source': skill.source
                        } for skill in skills
                    ],
                    'ai_summary': analysis.ai_summary if analysis else None,
                    'confidence_score': analysis.confidence_score if analysis else 0.0,
                    'total_skills': len(skills),
                    'has_resume_analysis': analysis is not None,
                    'created_at': profile.created_at.isoformat() if profile.created_at else None,
                    'updated_at': profile.updated_at.isoformat() if profile.updated_at else None
                }
                
                consultants.append(consultant_data)
            
            return consultants
            
        except Exception as e:
            logger.error(f"Error getting consultants with real skills: {e}")
            return []
        finally:
            db.close()

    def get_consultant_assignments(self, consultant_id):
        """Get consultant assignments from PostgreSQL database"""
        session = SessionLocal()
        try:
            # Query active assignments from database
            assignments = session.query(ConsultantAssignment).filter(
                ConsultantAssignment.consultant_id == consultant_id,
                ConsultantAssignment.status == 'active'
            ).all()
            
            assignment_list = []
            for assignment in assignments:
                # Get opportunity details
                opportunity = session.query(ProjectOpportunity).filter(
                    ProjectOpportunity.id == assignment.opportunity_id
                ).first()
                
                if opportunity:
                    assignment_data = {
                        'opportunity_id': assignment.opportunity_id,
                        'opportunity_name': opportunity.title,
                        'client_name': opportunity.client_name or opportunity.company,
                        'status': assignment.status,
                        'assigned_date': assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                        'start_date': assignment.start_date.isoformat() if assignment.start_date else None
                    }
                    assignment_list.append(assignment_data)
            
            print(f"Found {len(assignment_list)} assignments for consultant {consultant_id}")
            return assignment_list
            
        except Exception as e:
            print(f"Error getting consultant assignments: {e}")
            return []
        finally:
            session.close()
    
    def get_all_opportunities(self):
        """Get all opportunities from PostgreSQL database"""
        try:
            from database.models.professional_models import ProjectOpportunity
            
            session = self.get_session()
            try:
                # Get all opportunities from database
                opportunities = session.query(ProjectOpportunity).all()
                
                opportunity_list = []
                for opp in opportunities:
                    opportunity_data = {
                        'id': str(opp.id),
                        'title': opp.title,
                        'company': opp.company,
                        'client_name': opp.client_name or opp.company,
                        'description': opp.description,
                        'required_skills': opp.required_skills or [],
                        'experience_required': opp.experience_required,
                        'experience_level': opp.experience_level,
                        'location': opp.location,
                        'status': opp.status,
                        'project_duration': opp.project_duration,
                        'budget_range': opp.budget_range,
                        'start_date': opp.start_date,
                        'end_date': opp.end_date,
                        'created_at': opp.created_at.isoformat() if opp.created_at else None,
                        'created_date': opp.created_date or (opp.created_at.strftime('%Y-%m-%d') if opp.created_at else None)
                    }
                    opportunity_list.append(opportunity_data)
                
                # If no opportunities exist, create some initial ones
                if not opportunity_list:
                    self._create_initial_opportunities_postgres(session)
                    # Re-fetch after creating initial opportunities
                    opportunities = session.query(ProjectOpportunity).all()
                    for opp in opportunities:
                        opportunity_data = {
                            'id': str(opp.id),
                            'title': opp.title,
                            'company': opp.company,
                            'client_name': opp.client_name or opp.company,
                            'description': opp.description,
                            'required_skills': opp.required_skills or [],
                            'experience_required': opp.experience_required,
                            'experience_level': opp.experience_level,
                            'location': opp.location,
                            'status': opp.status,
                            'project_duration': opp.project_duration,
                            'budget_range': opp.budget_range,
                            'start_date': opp.start_date,
                            'end_date': opp.end_date,
                            'created_at': opp.created_at.isoformat() if opp.created_at else None,
                            'created_date': opp.created_date or (opp.created_at.strftime('%Y-%m-%d') if opp.created_at else None)
                        }
                        opportunity_list.append(opportunity_data)
                
                return opportunity_list
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error getting opportunities from PostgreSQL: {e}")
            return []
    
    def _create_initial_opportunities_postgres(self, session):
        """Create initial opportunities in PostgreSQL database"""
        try:
            from database.models.professional_models import ProjectOpportunity
            from datetime import datetime
            
            current_time = datetime.now()
            
            initial_opportunities = [
                {
                    'title': 'Senior React Developer',
                    'company': 'TechCorp',
                    'client_name': 'TechCorp Inc.',
                    'description': 'Build modern web applications with React and TypeScript. Work with a dynamic team to create cutting-edge solutions.',
                    'required_skills': ['React', 'JavaScript', 'Node.js', 'TypeScript', 'HTML', 'CSS'],
                    'experience_required': 5,
                    'experience_level': 'senior',
                    'location': 'Remote',
                    'status': 'open',
                    'project_duration': '6 months',
                    'budget_range': '$80k-100k',
                    'start_date': '2024-02-01',
                    'end_date': '2024-08-01',
                    'created_date': current_time.strftime('%Y-%m-%d')
                },
                {
                    'title': 'Data Scientist',
                    'company': 'DataCorp',
                    'client_name': 'DataCorp Ltd.',
                    'description': 'Machine learning and analytics projects. Develop predictive models and data pipelines.',
                    'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL', 'Pandas', 'NumPy'],
                    'experience_required': 3,
                    'experience_level': 'intermediate',
                    'location': 'Hybrid',
                    'status': 'open',
                    'project_duration': '8 months',
                    'budget_range': '$70k-90k',
                    'start_date': '2024-03-15',
                    'end_date': '2024-11-15',
                    'created_date': current_time.strftime('%Y-%m-%d')
                },
                {
                    'title': 'DevOps Engineer',
                    'company': 'CloudTech',
                    'client_name': 'CloudTech Solutions',
                    'description': 'Infrastructure automation and deployment pipelines. AWS/Azure cloud experience required.',
                    'required_skills': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Python'],
                    'experience_required': 4,
                    'experience_level': 'senior',
                    'location': 'On-site',
                    'status': 'open',
                    'project_duration': '12 months',
                    'budget_range': '$90k-120k',
                    'start_date': '2024-01-15',
                    'end_date': '2025-01-15',
                    'created_date': current_time.strftime('%Y-%m-%d')
                }
            ]
            
            for opp_data in initial_opportunities:
                opportunity = ProjectOpportunity(**opp_data)
                session.add(opportunity)
            
            session.commit()
            print(f"✅ Created {len(initial_opportunities)} initial opportunities in PostgreSQL")
            
        except Exception as e:
            session.rollback()
            print(f"Error creating initial opportunities: {e}")

    def add_opportunity(self, opportunity_data):
        """Add new opportunity to PostgreSQL database"""
        try:
            from database.models.professional_models import ProjectOpportunity
            from datetime import datetime
            
            session = self.get_session()
            try:
                # Ensure required_skills is a list
                required_skills = opportunity_data.get('required_skills', [])
                if isinstance(required_skills, str):
                    required_skills = [skill.strip() for skill in required_skills.split(',') if skill.strip()]
                
                # Create new opportunity
                new_opportunity = ProjectOpportunity(
                    title=opportunity_data['title'],
                    company=opportunity_data['company'],
                    client_name=opportunity_data.get('client_name', opportunity_data['company']),
                    description=opportunity_data.get('description', ''),
                    required_skills=required_skills,
                    experience_required=int(opportunity_data.get('experience_required', 0)),
                    experience_level=opportunity_data.get('experience_level', 'intermediate'),
                    location=opportunity_data.get('location', ''),
                    status=opportunity_data.get('status', 'open'),
                    project_duration=opportunity_data.get('project_duration', ''),
                    budget_range=opportunity_data.get('budget_range', ''),
                    start_date=opportunity_data.get('start_date', ''),
                    end_date=opportunity_data.get('end_date', ''),
                    created_date=datetime.now().strftime('%Y-%m-%d')
                )
                
                session.add(new_opportunity)
                session.commit()
                
                return {
                    'id': str(new_opportunity.id),
                    'title': new_opportunity.title,
                    'company': new_opportunity.company,
                    'client_name': new_opportunity.client_name,
                    'description': new_opportunity.description,
                    'required_skills': new_opportunity.required_skills,
                    'experience_required': new_opportunity.experience_required,
                    'experience_level': new_opportunity.experience_level,
                    'location': new_opportunity.location,
                    'status': new_opportunity.status,
                    'project_duration': new_opportunity.project_duration,
                    'budget_range': new_opportunity.budget_range,
                    'start_date': new_opportunity.start_date,
                    'end_date': new_opportunity.end_date,
                    'created_at': new_opportunity.created_at.isoformat() if new_opportunity.created_at else None,
                    'created_date': new_opportunity.created_date
                }
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error adding opportunity to PostgreSQL: {e}")
            return None

    def _create_initial_opportunities(self):
        """Create initial opportunities for demo"""
        try:
            if not hasattr(self, 'opportunities_store'):
                self.opportunities_store = {}
            
            # Only create if store is empty
            if not self.opportunities_store:
                from datetime import datetime
                current_time = datetime.now()
                
                initial_opportunities = [
                    {
                        'id': '1',
                        'title': 'Senior React Developer',
                        'company': 'TechCorp',
                        'client_name': 'TechCorp Inc.',
                        'description': 'Build modern web applications with React and TypeScript',
                        'required_skills': ['React', 'JavaScript', 'Node.js', 'TypeScript'],
                        'experience_required': 5,
                        'experience_level': 'senior',
                        'location': 'Remote',
                        'status': 'open',
                        'project_duration': '6 months',
                        'budget_range': '$80k-100k',
                        'start_date': '2024-02-01',
                        'end_date': '2024-08-01',
                        'created_at': current_time.strftime('%Y-%m-%d'),
                        'created_date': current_time.strftime('%Y-%m-%d')
                    },
                    {
                        'id': '2',
                        'title': 'Data Scientist',
                        'company': 'DataCorp',
                        'client_name': 'DataCorp Ltd.',
                        'description': 'Machine learning and analytics projects',
                        'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL'],
                        'experience_required': 3,
                        'experience_level': 'mid',
                        'location': 'New York',
                        'status': 'open',
                        'project_duration': '4 months',
                        'budget_range': '$60k-80k',
                        'start_date': '2024-02-15',
                        'end_date': '2024-06-15',
                        'created_at': current_time.strftime('%Y-%m-%d'),
                        'created_date': current_time.strftime('%Y-%m-%d')
                    },
                    {
                        'id': '3',
                        'title': 'DevOps Engineer',
                        'company': 'CloudTech',
                        'client_name': 'CloudTech Solutions',
                        'description': 'AWS infrastructure and CI/CD pipeline management',
                        'required_skills': ['AWS', 'Docker', 'Kubernetes', 'CI/CD'],
                        'experience_required': 4,
                        'experience_level': 'mid',
                        'location': 'San Francisco',
                        'status': 'open',
                        'project_duration': '8 months',
                        'budget_range': '$90k-120k',
                        'start_date': '2024-03-01',
                        'end_date': '2024-11-01',
                        'created_at': current_time.strftime('%Y-%m-%d'),
                        'created_date': current_time.strftime('%Y-%m-%d')
                    }
                ]
                
                for opportunity in initial_opportunities:
                    self.opportunities_store[opportunity['id']] = opportunity
                
                print("✅ Created initial opportunities for demo")
        except Exception as e:
            print(f"Error creating initial opportunities: {e}")
    
    def _create_initial_applications(self, opportunity_id):
        """Create initial applications for demo"""
        try:
            if not hasattr(self, 'applications_store'):
                self.applications_store = {}
            
            from datetime import datetime
            current_time = datetime.now()
            
            # Create initial applications based on opportunity_id
            if str(opportunity_id) == '1':  # React Developer opportunity
                initial_applications = [
                    {
                        'id': 'app_1_1',
                        'consultant_id': '1',
                        'consultant_name': 'John Doe',
                        'consultant_email': 'john.doe@company.com',
                        'consultant_skills': ['React', 'JavaScript', 'Node.js', 'HTML', 'CSS'],
                        'experience_years': 5,
                        'status': 'pending',
                        'applied_date': current_time.strftime('%Y-%m-%d'),
                        'applied_at': current_time.strftime('%Y-%m-%dT%H:%M:%S'),
                        'match_score': 85,
                        'cover_letter': 'I am excited about this React Developer position...',
                        'proposed_rate': '$75/hour',
                        'availability_start': '2024-02-01'
                    },
                    {
                        'id': 'app_1_2',
                        'consultant_id': '2',
                        'consultant_name': 'Jane Smith',
                        'consultant_email': 'jane.smith@company.com',
                        'consultant_skills': ['Python', 'React', 'JavaScript', 'Data Analysis'],
                        'experience_years': 8,
                        'status': 'accepted',
                        'applied_date': current_time.strftime('%Y-%m-%d'),
                        'applied_at': current_time.strftime('%Y-%m-%dT%H:%M:%S'),
                        'match_score': 75,
                        'cover_letter': 'With my background in both React and Python...',
                        'proposed_rate': '$80/hour',
                        'availability_start': '2024-01-25'
                    }
                ]
            elif str(opportunity_id) == '2':  # Data Scientist opportunity
                initial_applications = [
                    {
                        'id': 'app_2_1',
                        'consultant_id': '2',
                        'consultant_name': 'Jane Smith',
                        'consultant_email': 'jane.smith@company.com',
                        'consultant_skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL', 'Data Science'],
                        'experience_years': 8,
                        'status': 'pending',
                        'applied_date': current_time.strftime('%Y-%m-%d'),
                        'applied_at': current_time.strftime('%Y-%m-%dT%H:%M:%S'),
                        'match_score': 95,
                        'cover_letter': 'I have extensive experience in machine learning...',
                        'proposed_rate': '$90/hour',
                        'availability_start': '2024-02-05'
                    }
                ]
            elif str(opportunity_id) == '3':  # DevOps opportunity
                initial_applications = [
                    {
                        'id': 'app_3_1',
                        'consultant_id': '1',
                        'consultant_name': 'John Doe',
                        'consultant_email': 'john.doe@company.com',
                        'consultant_skills': ['React', 'JavaScript', 'Node.js', 'Docker'],
                        'experience_years': 5,
                        'status': 'declined',
                        'applied_date': current_time.strftime('%Y-%m-%d'),
                        'match_score': 40
                    }
                ]
            else:
                initial_applications = []
            
            if initial_applications:
                self.applications_store[str(opportunity_id)] = initial_applications
                print(f"✅ Created initial applications for opportunity {opportunity_id}")
        except Exception as e:
            print(f"Error creating initial applications: {e}")
    
    def get_opportunity_applications(self, opportunity_id):
        """Get applications for a specific opportunity from PostgreSQL database"""
        session = SessionLocal()
        try:
            # Query applications from database
            applications = session.query(OpportunityApplication).filter(
                OpportunityApplication.opportunity_id == opportunity_id
            ).all()
            
            application_list = []
            for app in applications:
                # Get consultant details
                consultant = session.query(ConsultantProfile).filter(
                    ConsultantProfile.id == app.consultant_id
                ).first()
                
                if consultant:
                    # Get consultant skills
                    skills = session.query(ConsultantSkill).filter(
                        ConsultantSkill.consultant_id == app.consultant_id
                    ).all()
                    
                    consultant_skills = [skill.skill_name for skill in skills]
                    
                    application_data = {
                        'id': app.id,
                        'consultant_id': str(app.consultant_id),
                        'consultant_name': consultant.user.name if consultant.user else 'Unknown',
                        'consultant_email': consultant.user.email if consultant.user else 'Unknown',
                        'consultant_skills': consultant_skills,
                        'experience_years': consultant.experience_years or 0,
                        'status': app.status,
                        'applied_date': app.created_at.strftime('%Y-%m-%d') if app.created_at else '',
                        'applied_at': app.created_at.isoformat() if app.created_at else '',
                        'match_score': app.match_score or 0,
                        'cover_letter': app.cover_letter or 'No cover letter provided',
                        'opportunity_id': str(app.opportunity_id)
                    }
                    application_list.append(application_data)
            
            print(f"Found {len(application_list)} applications for opportunity {opportunity_id}")
            return application_list
            
        except Exception as e:
            print(f"Error getting opportunity applications from PostgreSQL: {e}")
            return []
        finally:
            session.close()
    
    def add_application(self, opportunity_id, consultant_id, consultant_email, status='pending', 
                       cover_letter=None, proposed_rate=None, availability_start=None):
        """Add new application to PostgreSQL database"""
        session = SessionLocal()
        try:
            # Generate new application ID
            import uuid
            application_id = f"app_{opportunity_id}_{uuid.uuid4().hex[:8]}"
            
            # Calculate match score based on skills
            consultant_skills = self.get_consultant_skills(consultant_id)
            opportunity = session.query(ProjectOpportunity).filter(
                ProjectOpportunity.id == opportunity_id
            ).first()
            
            match_score = 80  # Default score
            if opportunity and opportunity.required_skills:
                skill_names = [skill['skill_name'].lower() for skill in consultant_skills]
                required_skills = opportunity.required_skills
                matched_count = sum(1 for req_skill in required_skills 
                                  if any(req_skill.lower() == skill.lower() for skill in skill_names))
                match_score = (matched_count / len(required_skills)) * 100 if required_skills else 80
            
            # Create application record
            application = OpportunityApplication(
                id=application_id,
                consultant_id=consultant_id,
                opportunity_id=opportunity_id,
                status=status,
                cover_letter=cover_letter,
                application_data={
                    'consultant_email': consultant_email,
                    'proposed_rate': proposed_rate,
                    'availability_start': availability_start
                },
                match_score=match_score,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(application)
            session.commit()
            session.refresh(application)
            
            print(f"Successfully added application {application_id} to PostgreSQL")
            print(f"Application details: cover_letter={cover_letter}, proposed_rate={proposed_rate}")
            
            return application_id
            
        except Exception as e:
            session.rollback()
            print(f"Error adding application to PostgreSQL: {e}")
            raise e
        finally:
            session.close()
    
    def get_application_by_id(self, application_id):
        """Get application details by ID"""
        session = SessionLocal()
        try:
            application = session.query(OpportunityApplication).filter(
                OpportunityApplication.id == application_id
            ).first()
            
            if application:
                return {
                    'id': application.id,
                    'opportunity_id': application.opportunity_id,
                    'consultant_id': application.consultant_id,
                    'status': application.status,
                    'cover_letter': application.cover_letter,
                    'application_data': application.application_data,
                    'match_score': application.match_score,
                    'created_at': application.created_at,
                    'updated_at': application.updated_at
                }
            return None
            
        except Exception as e:
            print(f"Error getting application: {e}")
            return None
        finally:
            session.close()
    
    def update_application_status(self, application_id, status):
        """Update application status"""
        session = SessionLocal()
        try:
            print(f"Updating application {application_id} status to {status}")
            
            # Find and update the application in PostgreSQL
            application = session.query(OpportunityApplication).filter(
                OpportunityApplication.id == application_id
            ).first()
            
            if application:
                application.status = status
                application.updated_at = datetime.utcnow()
                session.commit()
                print(f"Successfully updated application {application_id} to status {status}")
                return True
            else:
                print(f"Application {application_id} not found")
                return False
                
        except Exception as e:
            session.rollback()
            print(f"Error updating application status: {e}")
            raise e
        finally:
            session.close()
    
    def update_consultant_status(self, consultant_id, status=None, availability_status=None):
        """Update consultant status and availability"""
        session = SessionLocal()
        try:
            print(f"Updating consultant {consultant_id}: status={status}, availability_status={availability_status}")
            
            # Find and update the consultant in PostgreSQL
            consultant = session.query(ConsultantProfile).filter(
                ConsultantProfile.id == consultant_id
            ).first()
            
            if consultant:
                # Update current_status field (availability_status maps to current_status)
                if status:
                    consultant.current_status = status
                elif availability_status:
                    # Map availability_status to current_status
                    status_mapping = {
                        'busy': 'on_project',
                        'active': 'on_project', 
                        'available': 'available'
                    }
                    consultant.current_status = status_mapping.get(availability_status, availability_status)
                
                consultant.updated_at = datetime.utcnow()
                session.commit()
                print(f"Successfully updated consultant {consultant_id} current_status to {consultant.current_status}")
                return True
            else:
                print(f"Consultant {consultant_id} not found")
                return False
                
        except Exception as e:
            session.rollback()
            print(f"Error updating consultant status: {e}")
            raise e
        finally:
            session.close()
    
    def add_consultant_assignment(self, consultant_id, opportunity_id):
        """Add consultant assignment to opportunity"""
        session = SessionLocal()
        try:
            print(f"Assigning consultant {consultant_id} to opportunity {opportunity_id}")
            
            # Check if assignment already exists
            existing = session.query(ConsultantAssignment).filter(
                ConsultantAssignment.consultant_id == consultant_id,
                ConsultantAssignment.opportunity_id == opportunity_id,
                ConsultantAssignment.status == 'active'
            ).first()
            
            if existing:
                print(f"Assignment already exists: {existing.id}")
                return existing.id
            
            # Create new assignment
            assignment = ConsultantAssignment(
                consultant_id=consultant_id,
                opportunity_id=opportunity_id,
                status='active',
                assigned_date=datetime.utcnow(),
                start_date=datetime.utcnow()
            )
            
            session.add(assignment)
            session.commit()
            session.refresh(assignment)
            
            print(f"Successfully created assignment {assignment.id}")
            return assignment.id
                
        except Exception as e:
            session.rollback()
            print(f"Error adding consultant assignment: {e}")
            raise e
        finally:
            session.close()
    
    def increment_opportunity_accepted_count(self, opportunity_id):
        """Increment the accepted count for an opportunity"""
        try:
            print(f"Incrementing accepted count for opportunity {opportunity_id}")
            return True
        except Exception as e:
            print(f"Error incrementing opportunity accepted count: {e}")
            raise e
    
    def add_opportunity(self, **kwargs):
        """Add new opportunity to PostgreSQL database"""
        try:
            from database.models.professional_models import ProjectOpportunity
            from datetime import datetime
            
            session = self.get_session()
            try:
                print(f"Adding opportunity to PostgreSQL: {kwargs}")
                
                # Ensure required_skills is a list
                required_skills = kwargs.get('required_skills', [])
                if isinstance(required_skills, str):
                    required_skills = [skill.strip() for skill in required_skills.split(',') if skill.strip()]
                
                # Create new opportunity
                new_opportunity = ProjectOpportunity(
                    title=kwargs.get('title', ''),
                    company=kwargs.get('company', ''),
                    client_name=kwargs.get('client_name', kwargs.get('company', '')),
                    description=kwargs.get('description', ''),
                    required_skills=required_skills,
                    experience_required=int(kwargs.get('experience_required', 0)),
                    experience_level=self._get_experience_level(kwargs.get('experience_required', 0)),
                    location=kwargs.get('location', ''),
                    status=kwargs.get('status', 'open'),
                    project_duration=kwargs.get('project_duration', 'TBD'),
                    budget_range=kwargs.get('budget_range', 'TBD'),
                    start_date=kwargs.get('start_date', datetime.now().strftime('%Y-%m-%d')),
                    end_date=kwargs.get('end_date', 'TBD'),
                    created_date=datetime.now().strftime('%Y-%m-%d')
                )
                
                session.add(new_opportunity)
                session.commit()
                
                print(f"✅ Opportunity '{kwargs.get('title', '')}' created with ID: {new_opportunity.id}")
                return str(new_opportunity.id)
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error adding opportunity to PostgreSQL: {e}")
            raise e
    
    def _get_experience_level(self, experience_years):
        """Determine experience level based on years"""
        if experience_years >= 5:
            return 'senior'
        elif experience_years >= 3:
            return 'intermediate'
        else:
            return 'junior'

    def get_consultant_training(self, consultant_id):
        """Get consultant training enrollments"""
        try:
            # Initialize training storage if it doesn't exist
            if not hasattr(self, '_training_enrollments'):
                self._training_enrollments = {}
            
            # Mock training data for existing consultants
            default_training_data = {
                '1': [
                    {
                        'id': 1,
                        'program_name': 'Advanced React Patterns',
                        'progress_percentage': 75,
                        'status': 'in_progress',
                        'category': 'Frontend Development',
                        'enrollment_date': '2024-01-15',
                        'estimated_completion': '2024-03-15'
                    }
                ],
                '2': [
                    {
                        'id': 2,
                        'program_name': 'Deep Learning Specialization',
                        'progress_percentage': 100,
                        'status': 'completed',
                        'category': 'Machine Learning',
                        'enrollment_date': '2023-10-01',
                        'estimated_completion': '2024-01-01'
                    }
                ]
            }
            
            # Get dynamic enrollments for this consultant
            consultant_str = str(consultant_id)
            dynamic_enrollments = self._training_enrollments.get(consultant_str, [])
            default_enrollments = default_training_data.get(consultant_str, [])
            
            # Combine default and dynamic enrollments
            all_enrollments = default_enrollments + dynamic_enrollments
            return all_enrollments
            
        except Exception as e:
            print(f"Error getting consultant training: {e}")
            return []
    
    def store_training_enrollment(self, consultant_id, training_program, provider=None, duration_hours=None, progress_percentage=5):
        """Store a new training enrollment for a consultant"""
        try:
            # Initialize training storage if it doesn't exist
            if not hasattr(self, '_training_enrollments'):
                self._training_enrollments = {}
            
            consultant_str = str(consultant_id)
            if consultant_str not in self._training_enrollments:
                self._training_enrollments[consultant_str] = []
            
            # Generate enrollment ID
            enrollment_id = len(self._training_enrollments[consultant_str]) + 100
            
            # Create new enrollment
            new_enrollment = {
                'id': enrollment_id,
                'program_name': training_program,
                'progress_percentage': progress_percentage,
                'status': 'enrolled' if progress_percentage < 10 else 'in_progress',
                'category': provider or 'Professional Development',
                'enrollment_date': datetime.now().strftime('%Y-%m-%d'),
                'estimated_completion': (datetime.now() + timedelta(days=duration_hours or 30)).strftime('%Y-%m-%d') if duration_hours else None,
                'duration_hours': duration_hours
            }
            
            # Add to storage
            self._training_enrollments[consultant_str].append(new_enrollment)
            
            return {
                'success': True,
                'enrollment_id': f"enroll_{consultant_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'enrollment_details': new_enrollment
            }
            
        except Exception as e:
            print(f"Error storing training enrollment: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_training_progress(self, consultant_id, training_program, progress_percentage):
        """Update progress for a specific training program"""
        try:
            # Initialize training storage if it doesn't exist
            if not hasattr(self, '_training_enrollments'):
                self._training_enrollments = {}
                
            consultant_str = str(consultant_id)
            enrollments = self._training_enrollments.get(consultant_str, [])
            
            # Find and update the training program
            updated = False
            for enrollment in enrollments:
                if enrollment['program_name'] == training_program:
                    enrollment['progress_percentage'] = progress_percentage
                    if progress_percentage >= 100:
                        enrollment['status'] = 'completed'
                    elif progress_percentage >= 10:
                        enrollment['status'] = 'in_progress'
                    updated = True
                    break
            
            if updated:
                return {
                    'success': True,
                    'consultant_id': consultant_id,
                    'training_program': training_program,
                    'progress_percentage': progress_percentage
                }
            else:
                return {'success': False, 'error': 'Training program not found'}
                
        except Exception as e:
            print(f"Error updating training progress: {e}")
            return {'success': False, 'error': str(e)}
    
    # Resume Analysis Methods
    def store_resume_analysis_with_skills(self, consultant_id, file_name, extracted_text, analysis_result):
        """Store complete resume analysis and sync skills to consultant profile"""
        try:
            # Store resume analysis
            resume_analysis_id = self.store_resume_analysis(
                consultant_id=consultant_id,
                file_name=file_name,
                extracted_text=extracted_text,
                extracted_skills=analysis_result.get('skills', []),
                extracted_competencies=analysis_result.get('soft_skills', []),
                identified_roles=analysis_result.get('roles', []),
                ai_summary=analysis_result.get('ai_summary', ''),
                ai_feedback=analysis_result.get('ai_feedback', ''),
                ai_suggestions=analysis_result.get('ai_suggestions', ''),
                confidence_score=analysis_result.get('confidence_score', 0.0),
                skill_vector=analysis_result.get('skill_vector', []),
                analysis_method=analysis_result.get('analysis_method', 'AI')
            )
            
            # Sync skills to consultant profile
            skills_to_add = []
            
            # Add technical skills
            for skill in analysis_result.get('skills', []):
                skills_to_add.append({
                    'skill_name': skill,
                    'category': 'technical',
                    'proficiency_level': 'intermediate',
                    'confidence_score': 85,
                    'source': 'resume_ai_analysis'
                })
            
            # Add soft skills/competencies
            for competency in analysis_result.get('soft_skills', []):
                skills_to_add.append({
                    'skill_name': competency,
                    'category': 'soft',
                    'proficiency_level': 'intermediate',
                    'confidence_score': 80,
                    'source': 'resume_ai_analysis'
                })
            
            # Store skills in PostgreSQL
            added_skills = self.add_skills_from_resume(
                consultant_id, 
                skills_to_add, 
                'resume_ai_analysis'
            )
            
            # Synchronize consultant profile with analysis
            sync_success = self.sync_consultant_data_with_analysis(consultant_id)
            
            logger.info(f"✅ Stored Resume_Agent analysis for consultant {consultant_id}: {len(added_skills)} skills added")
            logger.info(f"✅ Consultant profile synchronized: {sync_success}")
            
            return {
                "success": True,
                "resume_analysis_id": resume_analysis_id,
                "skills_added": len(added_skills),
                "skills_list": added_skills,
                "sync_completed": sync_success,
                "analysis_method": analysis_result.get('analysis_method', 'Resume_Agent_AI'),
                "confidence_score": analysis_result.get('confidence_score', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Failed to store resume analysis with skills: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def store_resume_analysis(self, consultant_id, file_name, extracted_text, extracted_skills, 
                             extracted_competencies, identified_roles, ai_summary, ai_feedback, 
                             ai_suggestions, confidence_score, skill_vector, analysis_method):
        """Store detailed resume analysis results in PostgreSQL"""
        db = SessionLocal()
        try:
            from database.models.professional_models import ResumeAnalysis
            
            # Create new resume analysis record
            analysis = ResumeAnalysis(
                consultant_id=consultant_id,
                file_name=file_name,
                extracted_text=extracted_text,
                extracted_skills=extracted_skills,
                extracted_competencies=extracted_competencies,
                identified_roles=identified_roles,
                skill_vector=skill_vector,
                ai_summary=ai_summary,
                ai_feedback=ai_feedback,
                ai_suggestions=ai_suggestions,
                confidence_score=confidence_score,
                analysis_version='Resume_Agent_v1.0',
                processing_time=0.0  # Could be measured in future
            )
            
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
            logger.info(f"✅ Resume analysis stored in PostgreSQL for consultant {consultant_id}")
            logger.info(f"   - File: {file_name}")
            logger.info(f"   - Method: {analysis_method}")
            logger.info(f"   - Technical skills: {len(extracted_skills) if extracted_skills else 0}")
            logger.info(f"   - Soft skills: {len(extracted_competencies) if extracted_competencies else 0}")
            logger.info(f"   - Confidence: {confidence_score}")
            
            return analysis.id
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error storing resume analysis: {e}")
            raise e
        finally:
            db.close()
    
    def get_resume_analysis_by_consultant_id(self, consultant_id):
        """Get resume analysis by consultant ID from PostgreSQL database"""
        try:
            # Use the new database method
            analysis = self.get_resume_analysis_from_db(consultant_id)
            
            if analysis:
                return analysis
            
            # If no real analysis found, return None instead of dummy data
            logger.info(f"No resume analysis found for consultant {consultant_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting resume analysis: {e}")
            return None

if __name__ == "__main__":
    test_connection()
    init_database()
