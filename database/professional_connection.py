#!/usr/bin/env python3
"""
Professional Pool Database Connection
PostgreSQL database connection for consultant management system
"""
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.models.professional_models import Base

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
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def get_all_consultants(self):
        """Get all consultants"""
        try:
            with self.get_session() as session:
                # For now, return mock data since we're transitioning
                # This will be replaced with actual SQLAlchemy queries
                return [
                    {
                        'id': '1',
                        'name': 'John Doe',
                        'email': 'john.doe@company.com',
                        'phone': '+1-555-0123',
                        'location': 'New York, NY',
                        'experience_years': 5,
                        'department': 'Engineering',
                        'primary_skill': 'React',
                        'status': 'active',
                        'attendance_rate': 95,
                        'training_status': 'in-progress',
                        'availability_status': 'available'
                    },
                    {
                        'id': '2',
                        'name': 'Jane Smith',
                        'email': 'jane.smith@company.com',
                        'phone': '+1-555-0124',
                        'location': 'San Francisco, CA',
                        'experience_years': 8,
                        'department': 'Data Science',
                        'primary_skill': 'Python',
                        'status': 'active',
                        'attendance_rate': 88,
                        'training_status': 'completed',
                        'availability_status': 'busy'
                    }
                ]
        except Exception as e:
            print(f"Error getting consultants: {e}")
            return []
    
    def get_consultant(self, consultant_id):
        """Get consultant by ID"""
        consultants = self.get_all_consultants()
        return next((c for c in consultants if c['id'] == str(consultant_id)), None)
    
    def add_consultant(self, **kwargs):
        """Add new consultant"""
        try:
            # Generate new ID
            consultants = self.get_all_consultants()
            new_id = max([int(c['id']) for c in consultants], default=0) + 1
            
            # For now, just return the new ID
            # In production, this would insert into database
            print(f"Adding consultant: {kwargs}")
            return new_id
        except Exception as e:
            print(f"Error adding consultant: {e}")
            raise e
    
    def update_consultant(self, consultant_id, **kwargs):
        """Update consultant"""
        try:
            print(f"Updating consultant {consultant_id}: {kwargs}")
            return True
        except Exception as e:
            print(f"Error updating consultant: {e}")
            raise e
    
    def remove_consultant(self, consultant_id):
        """Remove consultant"""
        try:
            print(f"Removing consultant {consultant_id}")
            return True
        except Exception as e:
            print(f"Error removing consultant: {e}")
            raise e
    
    def get_consultant_skills(self, consultant_id):
        """Get consultant skills"""
        try:
            # Mock data for development
            skills_data = {
                '1': [
                    {'skill_name': 'React', 'skill_type': 'technical', 'proficiency_level': 'advanced'},
                    {'skill_name': 'JavaScript', 'skill_type': 'technical', 'proficiency_level': 'advanced'},
                    {'skill_name': 'Node.js', 'skill_type': 'technical', 'proficiency_level': 'intermediate'},
                    {'skill_name': 'Leadership', 'skill_type': 'soft', 'proficiency_level': 'intermediate'}
                ],
                '2': [
                    {'skill_name': 'Python', 'skill_type': 'technical', 'proficiency_level': 'expert'},
                    {'skill_name': 'Machine Learning', 'skill_type': 'technical', 'proficiency_level': 'advanced'},
                    {'skill_name': 'TensorFlow', 'skill_type': 'technical', 'proficiency_level': 'intermediate'},
                    {'skill_name': 'Communication', 'skill_type': 'soft', 'proficiency_level': 'advanced'}
                ]
            }
            return skills_data.get(str(consultant_id), [])
        except Exception as e:
            print(f"Error getting consultant skills: {e}")
            return []
    
    def add_consultant_skill(self, consultant_id, skill_name, proficiency_level, skill_type):
        """Add skill to consultant"""
        try:
            print(f"Adding skill {skill_name} to consultant {consultant_id}")
            return True
        except Exception as e:
            print(f"Error adding consultant skill: {e}")
            raise e
    
    def remove_consultant_skills(self, consultant_id):
        """Remove all skills for consultant"""
        try:
            print(f"Removing all skills for consultant {consultant_id}")
            return True
        except Exception as e:
            print(f"Error removing consultant skills: {e}")
            raise e
    
    def get_consultant_assignments(self, consultant_id):
        """Get consultant assignments"""
        try:
            # Mock data
            assignments_data = {
                '1': [
                    {
                        'opportunity_id': 1,
                        'opportunity_name': 'E-commerce Platform Development',
                        'client_name': 'TechCorp Inc.',
                        'status': 'active'
                    }
                ],
                '2': []
            }
            return assignments_data.get(str(consultant_id), [])
        except Exception as e:
            print(f"Error getting consultant assignments: {e}")
            return []
    
    def get_all_opportunities(self):
        """Get all opportunities"""
        try:
            return [
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
                    'created_at': '2024-01-15'
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
                    'created_at': '2024-01-20'
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
                    'created_at': '2024-01-25'
                }
            ]
        except Exception as e:
            print(f"Error getting opportunities: {e}")
            return []
    
    def get_opportunity_applications(self, opportunity_id):
        """Get applications for a specific opportunity"""
        try:
            # Mock applications data with realistic consultant applications
            applications_data = {
                '1': [  # React Developer opportunity
                    {
                        'id': 'app_1_1',
                        'consultant_id': '1',
                        'consultant_name': 'John Doe',
                        'consultant_email': 'john.doe@company.com',
                        'consultant_skills': ['React', 'JavaScript', 'Node.js', 'HTML', 'CSS'],
                        'experience_years': 5,
                        'status': 'pending',
                        'applied_date': '2024-01-20',
                        'match_score': 85
                    },
                    {
                        'id': 'app_1_2',
                        'consultant_id': '2',
                        'consultant_name': 'Jane Smith',
                        'consultant_email': 'jane.smith@company.com',
                        'consultant_skills': ['Python', 'React', 'JavaScript', 'Data Analysis'],
                        'experience_years': 8,
                        'status': 'accepted',
                        'applied_date': '2024-01-18',
                        'match_score': 75
                    }
                ],
                '2': [  # Data Scientist opportunity
                    {
                        'id': 'app_2_1',
                        'consultant_id': '2',
                        'consultant_name': 'Jane Smith',
                        'consultant_email': 'jane.smith@company.com',
                        'consultant_skills': ['Python', 'Machine Learning', 'TensorFlow', 'SQL', 'Data Science'],
                        'experience_years': 8,
                        'status': 'pending',
                        'applied_date': '2024-01-22',
                        'match_score': 95
                    }
                ],
                '3': [  # DevOps opportunity
                    {
                        'id': 'app_3_1',
                        'consultant_id': '1',
                        'consultant_name': 'John Doe',
                        'consultant_email': 'john.doe@company.com',
                        'consultant_skills': ['React', 'JavaScript', 'Node.js', 'Docker'],
                        'experience_years': 5,
                        'status': 'declined',
                        'applied_date': '2024-01-25',
                        'match_score': 40
                    }
                ]
            }
            return applications_data.get(str(opportunity_id), [])
        except Exception as e:
            print(f"Error getting opportunity applications: {e}")
            return []
    
    def add_application(self, opportunity_id, consultant_id, consultant_email, status='pending'):
        """Add new application"""
        try:
            # Generate new application ID
            import uuid
            application_id = f"app_{opportunity_id}_{uuid.uuid4().hex[:8]}"
            print(f"Adding application {application_id} for consultant {consultant_id} to opportunity {opportunity_id}")
            return application_id
        except Exception as e:
            print(f"Error adding application: {e}")
            raise e
    
    def update_application_status(self, application_id, status):
        """Update application status"""
        try:
            print(f"Updating application {application_id} status to {status}")
            return True
        except Exception as e:
            print(f"Error updating application status: {e}")
            raise e
    
    def add_consultant_assignment(self, consultant_id, opportunity_id):
        """Add consultant assignment to opportunity"""
        try:
            print(f"Assigning consultant {consultant_id} to opportunity {opportunity_id}")
            return True
        except Exception as e:
            print(f"Error adding consultant assignment: {e}")
            raise e
    
    def increment_opportunity_accepted_count(self, opportunity_id):
        """Increment the accepted count for an opportunity"""
        try:
            print(f"Incrementing accepted count for opportunity {opportunity_id}")
            return True
        except Exception as e:
            print(f"Error incrementing opportunity accepted count: {e}")
            raise e
    
    def add_opportunity(self, **kwargs):
        """Add new opportunity"""
        try:
            print(f"Adding opportunity: {kwargs}")
            # Generate new ID based on existing opportunities
            opportunities = self.get_all_opportunities()
            new_id = max([int(opp['id']) for opp in opportunities], default=0) + 1
            return str(new_id)
        except Exception as e:
            print(f"Error adding opportunity: {e}")
            raise e
    
    def get_consultant_training(self, consultant_id):
        """Get consultant training enrollments"""
        try:
            # Mock training data
            training_data = {
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
            return training_data.get(str(consultant_id), [])
        except Exception as e:
            print(f"Error getting consultant training: {e}")
            return []

if __name__ == "__main__":
    test_connection()
    init_database()
