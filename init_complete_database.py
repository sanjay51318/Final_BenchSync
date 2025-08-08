#!/usr/bin/env python3
"""
Complete Database Initialization Script for PostgreSQL
Creates all necessary tables and populates with comprehensive sample data
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, date
import json
from pathlib import Path
import random

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database setup - PostgreSQL configuration
DATABASE_URL = "postgresql://postgres:2005@localhost:5432/consultant_bench_db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models
try:
    from database.models.professional_models import *
except ImportError:
    # Try alternative import
    sys.path.insert(0, str(current_dir / "database"))
    from models.professional_models import *

def init_database():
    """Initialize database tables"""
    try:
        # Drop all tables and recreate them
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Professional database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def create_comprehensive_sample_data():
    """Create comprehensive sample data for all tables"""
    db = SessionLocal()
    
    try:
        print("🗄️ Creating comprehensive database tables and sample data...")
        
        # Create all tables
        init_database()
        
        # No need to clear tables as they were just recreated
        print("✅ Tables recreated with new schema")
        
        # Create Users
        users_data = [
            {"id": "user_1", "name": "John Doe", "email": "john.doe@example.com", "password_hash": "password123", "role": "consultant", "department": "Technology"},
            {"id": "user_2", "name": "Sarah Wilson", "email": "sarah.wilson@example.com", "password_hash": "password123", "role": "consultant", "department": "Technology"},
            {"id": "user_3", "name": "Mike Johnson", "email": "mike.johnson@example.com", "password_hash": "password123", "role": "consultant", "department": "Technology"},
            {"id": "user_4", "name": "Emily Davis", "email": "emily.davis@example.com", "password_hash": "password123", "role": "consultant", "department": "Technology"},
            {"id": "user_5", "name": "Alex Chen", "email": "alex.chen@example.com", "password_hash": "password123", "role": "consultant", "department": "Technology"},
            {"id": "user_6", "name": "Kisshore Kumar", "email": "kisshore@company.com", "password_hash": "password123", "role": "consultant", "department": "Technology"},
            {"id": "admin_1", "name": "Admin User", "email": "admin@company.com", "password_hash": "password123", "role": "admin", "department": "Management"},
        ]
        
        created_users = []
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
            db.flush()
            created_users.append(user)
        
        print(f"✅ Created {len(created_users)} users")
        
        # Create Consultant Profiles
        consultant_profiles_data = [
            {
                "user_id": created_users[0].id,
                "primary_skill": "React",
                "experience_years": 5,
                "current_status": "assigned",
                "attendance_rate": 88.0,
                "training_status": "in-progress",
                "resume_status": "not updated",
                "opportunities_count": 0,
                "bench_start_date": None
            },
            {
                "user_id": created_users[1].id,
                "primary_skill": "Python",
                "experience_years": 7,
                "current_status": "assigned",
                "attendance_rate": 91.0,
                "training_status": "completed",
                "resume_status": "not updated",
                "opportunities_count": 0,
                "bench_start_date": None
            },
            {
                "user_id": created_users[2].id,
                "primary_skill": "DevOps",
                "experience_years": 6,
                "current_status": "assigned",
                "attendance_rate": 94.0,
                "training_status": "in-progress",
                "resume_status": "not updated",
                "opportunities_count": 0,
                "bench_start_date": None
            },
            {
                "user_id": created_users[3].id,
                "primary_skill": "Full Stack",
                "experience_years": 4,
                "current_status": "available",
                "attendance_rate": 97.0,
                "training_status": "completed",
                "resume_status": "not updated",
                "opportunities_count": 0,
                "bench_start_date": None
            },
            {
                "user_id": created_users[4].id,
                "primary_skill": "Mobile",
                "experience_years": 5,
                "current_status": "available",
                "attendance_rate": 100.0,
                "training_status": "in-progress",
                "resume_status": "not updated",
                "opportunities_count": 0,
                "bench_start_date": None
            },
            {
                "user_id": created_users[5].id,
                "primary_skill": "C#",
                "experience_years": 8,
                "current_status": "available",
                "attendance_rate": 0.0,
                "training_status": "not-started",
                "resume_status": "updated",
                "opportunities_count": 0,
                "bench_start_date": None
            }
        ]
        
        created_consultants = []
        for profile_data in consultant_profiles_data:
            consultant = ConsultantProfile(**profile_data)
            db.add(consultant)
            db.flush()
            created_consultants.append(consultant)
        
        print(f"✅ Created {len(created_consultants)} consultant profiles")
        
        # Create Project Opportunities
        opportunities_data = [
            {
                "title": "Senior React Developer - FinTech Platform",
                "description": "Lead frontend development for modern fintech application using React, TypeScript, and advanced state management",
                "client_name": "FinanceCorp Solutions",
                "required_skills": ["React", "TypeScript", "Redux", "JavaScript", "CSS3", "HTML5"],
                "experience_level": "senior",
                "project_duration": "8 months",
                "budget_range": "$80,000 - $120,000",
                "start_date": datetime(2025, 8, 15),
                "end_date": datetime(2026, 4, 15),
                "status": "assigned"
            },
            {
                "title": "Python Backend Engineer - E-commerce API",
                "description": "Design and implement scalable backend services using Python, Django, and microservices architecture",
                "client_name": "ShopTech Inc",
                "required_skills": ["Python", "Django", "PostgreSQL", "Redis", "Docker", "AWS"],
                "experience_level": "senior",
                "project_duration": "6 months",
                "budget_range": "$75,000 - $110,000",
                "start_date": datetime(2025, 9, 1),
                "end_date": datetime(2026, 3, 1),
                "status": "assigned"
            },
            {
                "title": "DevOps Engineer - Cloud Infrastructure",
                "description": "Modernize infrastructure using Kubernetes, Terraform, and implement CI/CD pipelines",
                "client_name": "CloudFirst Technologies",
                "required_skills": ["Kubernetes", "Docker", "Terraform", "AWS", "Jenkins", "Python"],
                "experience_level": "mid",
                "project_duration": "10 months",
                "budget_range": "$85,000 - $125,000",
                "start_date": datetime(2025, 8, 20),
                "end_date": datetime(2026, 6, 20),
                "status": "assigned"
            },
            {
                "title": "Full Stack Developer - Healthcare Platform",
                "description": "Develop comprehensive healthcare management system using React, Node.js, and MongoDB",
                "client_name": "HealthTech Solutions",
                "required_skills": ["React", "Node.js", "MongoDB", "JavaScript", "TypeScript", "Express.js"],
                "experience_level": "mid",
                "project_duration": "5 months",
                "budget_range": "$70,000 - $100,000",
                "start_date": datetime(2025, 9, 10),
                "end_date": datetime(2026, 2, 10),
                "status": "open"
            },
            {
                "title": "Mobile App Developer - Cross-Platform Solution",
                "description": "Build cross-platform mobile application using Flutter for iOS and Android deployment",
                "client_name": "MobileFirst Corp",
                "required_skills": ["Flutter", "Dart", "React Native", "Mobile Development", "Firebase"],
                "experience_level": "mid",
                "project_duration": "6 months",
                "budget_range": "$75,000 - $105,000",
                "start_date": datetime(2025, 9, 5),
                "end_date": datetime(2026, 3, 5),
                "status": "open"
            }
        ]
        
        created_opportunities = []
        for opp_data in opportunities_data:
            opportunity = ProjectOpportunity(**opp_data)
            db.add(opportunity)
            db.flush()
            created_opportunities.append(opportunity)
        
        print(f"✅ Created {len(created_opportunities)} project opportunities")
        
        # Create Consultant Project Matches (Assignments)
        assignments_data = [
            {
                "consultant_id": created_consultants[0].id,  # John Doe -> React project
                "opportunity_id": created_opportunities[0].id,
                "match_score": 95.0,
                "ai_reasoning": "Perfect skill match with React and TypeScript expertise",
                "application_date": datetime.now() - timedelta(days=10),
                "status": "selected"
            },
            {
                "consultant_id": created_consultants[1].id,  # Sarah Wilson -> Python project
                "opportunity_id": created_opportunities[1].id,
                "match_score": 88.0,
                "ai_reasoning": "Strong Python and Django background with cloud experience",
                "application_date": datetime.now() - timedelta(days=8),
                "status": "selected"
            },
            {
                "consultant_id": created_consultants[2].id,  # Mike Johnson -> DevOps project
                "opportunity_id": created_opportunities[2].id,
                "match_score": 92.0,
                "ai_reasoning": "Excellent DevOps skills with Kubernetes and AWS expertise",
                "application_date": datetime.now() - timedelta(days=5),
                "status": "selected"
            }
        ]
        
        for assignment_data in assignments_data:
            assignment = OpportunityApplication(**assignment_data)
            db.add(assignment)
        
        print(f"✅ Created {len(assignments_data)} consultant assignments")
        
        # Add Skills for consultants
        skills_data = [
            # John Doe skills
            {"consultant_id": created_consultants[0].id, "skill_name": "React", "proficiency_level": "expert", "years_experience": 5.0, "is_primary": True},
            {"consultant_id": created_consultants[0].id, "skill_name": "TypeScript", "proficiency_level": "advanced", "years_experience": 3.0, "is_primary": False},
            {"consultant_id": created_consultants[0].id, "skill_name": "JavaScript", "proficiency_level": "expert", "years_experience": 5.0, "is_primary": False},
            
            # Sarah Wilson skills
            {"consultant_id": created_consultants[1].id, "skill_name": "Python", "proficiency_level": "expert", "years_experience": 7.0, "is_primary": True},
            {"consultant_id": created_consultants[1].id, "skill_name": "Django", "proficiency_level": "advanced", "years_experience": 5.0, "is_primary": False},
            {"consultant_id": created_consultants[1].id, "skill_name": "PostgreSQL", "proficiency_level": "advanced", "years_experience": 4.0, "is_primary": False},
            
            # Mike Johnson skills
            {"consultant_id": created_consultants[2].id, "skill_name": "Kubernetes", "proficiency_level": "expert", "years_experience": 4.0, "is_primary": True},
            {"consultant_id": created_consultants[2].id, "skill_name": "Docker", "proficiency_level": "expert", "years_experience": 5.0, "is_primary": False},
            {"consultant_id": created_consultants[2].id, "skill_name": "AWS", "proficiency_level": "advanced", "years_experience": 6.0, "is_primary": False},
            
            # Emily Davis skills
            {"consultant_id": created_consultants[3].id, "skill_name": "React", "proficiency_level": "advanced", "years_experience": 3.0, "is_primary": True},
            {"consultant_id": created_consultants[3].id, "skill_name": "Node.js", "proficiency_level": "advanced", "years_experience": 4.0, "is_primary": False},
            {"consultant_id": created_consultants[3].id, "skill_name": "MongoDB", "proficiency_level": "intermediate", "years_experience": 2.0, "is_primary": False},
            
            # Alex Chen skills
            {"consultant_id": created_consultants[4].id, "skill_name": "Flutter", "proficiency_level": "expert", "years_experience": 3.0, "is_primary": True},
            {"consultant_id": created_consultants[4].id, "skill_name": "React Native", "proficiency_level": "advanced", "years_experience": 4.0, "is_primary": False},
            {"consultant_id": created_consultants[4].id, "skill_name": "Dart", "proficiency_level": "expert", "years_experience": 3.0, "is_primary": False},
            
            # Kisshore Kumar skills
            {"consultant_id": created_consultants[5].id, "skill_name": "C#", "proficiency_level": "expert", "years_experience": 8.0, "is_primary": True},
            {"consultant_id": created_consultants[5].id, "skill_name": "Go", "proficiency_level": "intermediate", "years_experience": 2.0, "is_primary": False},
            {"consultant_id": created_consultants[5].id, "skill_name": "AWS", "proficiency_level": "advanced", "years_experience": 4.0, "is_primary": False},
            {"consultant_id": created_consultants[5].id, "skill_name": "Git", "proficiency_level": "advanced", "years_experience": 6.0, "is_primary": False},
        ]
        
        for skill_data in skills_data:
            skill = ConsultantSkill(**skill_data)
            db.add(skill)
        
        print(f"✅ Created {len(skills_data)} consultant skills")
        
        # Create Attendance Records for the last 30 days
        attendance_data = []
        base_date = date.today() - timedelta(days=30)
        
        for user in created_users:
            if user.role == "consultant":  # Only create attendance for consultants
                for day_offset in range(30):
                    current_date = base_date + timedelta(days=day_offset)
                    
                    # Skip weekends for regular attendance
                    if current_date.weekday() < 5:  # Monday=0, Friday=4
                        # Generate realistic attendance patterns
                        attendance_probability = random.choice([0.95, 0.90, 0.85, 0.92, 0.88])  # Different consultants have different patterns
                        
                        if random.random() < attendance_probability:
                            status = "present"
                            check_in = f"0{random.randint(8,9)}:{random.randint(0,5)}{random.randint(0,9)}"
                            check_out = f"{random.randint(17,18)}:{random.randint(0,5)}{random.randint(0,9)}"
                            hours = round(random.uniform(7.5, 9.0), 1)
                            location = random.choice(["office", "remote", "office", "office"])  # Mostly office
                        else:
                            status = random.choice(["absent", "leave", "half_day"])
                            check_in = None
                            check_out = None
                            hours = 4.0 if status == "half_day" else 0.0
                            location = "office"
                        
                        attendance_record = {
                            "user_id": user.id,
                            "date": current_date.strftime("%Y-%m-%d"),
                            "status": status,
                            "check_in_time": check_in,
                            "check_out_time": check_out,
                            "hours_worked": hours,
                            "location": location,
                            "notes": f"Auto-generated attendance for {user.name}"
                        }
                        attendance_data.append(attendance_record)
        
        for attendance_record in attendance_data:
            attendance = AttendanceRecord(**attendance_record)
            db.add(attendance)
        
        print(f"✅ Created {len(attendance_data)} attendance records for last 30 days")
        
        # Commit all changes
        db.commit()
        print("✅ All sample data created successfully!")
        
        # Verify data
        consultant_count = db.query(ConsultantProfile).count()
        opportunity_count = db.query(ProjectOpportunity).count()
        assignment_count = db.query(OpportunityApplication).count()
        skill_count = db.query(ConsultantSkill).count()
        attendance_count = db.query(AttendanceRecord).count()
        
        print(f"""
📊 Database Summary:
   - Consultants: {consultant_count}
   - Opportunities: {opportunity_count}
   - Active Assignments: {assignment_count}
   - Skills: {skill_count}
   - Attendance Records: {attendance_count}
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting comprehensive database initialization...")
    success = create_comprehensive_sample_data()
    if success:
        print("✅ Database initialization completed successfully!")
        print("🎉 Your system now has comprehensive sample data for testing.")
    else:
        print("❌ Database initialization failed!")
        sys.exit(1)
