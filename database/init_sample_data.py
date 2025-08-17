#!/usr/bin/env python3
"""
Initialize sample data for consultants and admins
Creates multiple consultant profiles with diverse skills and admin accounts
"""
import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.professional_connection import get_db, SessionLocal
from database.models.professional_models import (
    User, ConsultantProfile, ConsultantSkill, ProjectOpportunity,
    ResumeAnalysis, AttendanceRecord
)
from datetime import datetime, timedelta
import json

def create_sample_users_and_consultants():
    """Create sample users and consultant profiles"""
    db = SessionLocal()
    
    try:
        # Clear existing data using ORM (safer approach)
        print("🗑️ Clearing existing data...")
        
        # Delete in proper order to avoid foreign key constraints
        try:
            db.query(ConsultantSkill).delete()
            print("   ✅ Cleared consultant_skills")
        except:
            print("   ⚠️ consultant_skills table not found or empty")
            
        try:
            db.query(AttendanceRecord).delete()
            print("   ✅ Cleared attendance_records")
        except:
            print("   ⚠️ attendance_records table not found or empty")
            
        try:
            db.query(ResumeAnalysis).delete()
            print("   ✅ Cleared resume_analysis")
        except:
            print("   ⚠️ resume_analysis table not found or empty")
            
        try:
            db.query(ConsultantProfile).delete()
            print("   ✅ Cleared consultant_profiles")
        except:
            print("   ⚠️ consultant_profiles table not found or empty")
            
        try:
            db.query(ProjectOpportunity).delete()
            print("   ✅ Cleared project_opportunities")
        except:
            print("   ⚠️ project_opportunities table not found or empty")
            
        try:
            db.query(User).delete()
            print("   ✅ Cleared users")
        except:
            print("   ⚠️ users table not found or empty")
            
        db.commit()
        print("   💾 Cleanup committed")
        
        # Sample consultant data with diverse skills
        sample_data = [
            {
                "user": {
                    "id": "john_doe_001",
                    "name": "John Doe",
                    "email": "john.doe@company.com",
                    "password_hash": "password123",
                    "role": "consultant",
                    "department": "Engineering"
                },
                "profile": {
                    "primary_skill": "Full Stack Development",
                    "experience_years": 5,
                    "bench_start_date": "2024-01-15",
                    "current_status": "available"
                },
                "skills": [
                    {"name": "React", "category": "Frontend", "proficiency": "expert", "years": 4},
                    {"name": "JavaScript", "category": "Programming", "proficiency": "expert", "years": 5},
                    {"name": "Node.js", "category": "Backend", "proficiency": "advanced", "years": 3},
                    {"name": "TypeScript", "category": "Programming", "proficiency": "intermediate", "years": 2},
                    {"name": "Python", "category": "Programming", "proficiency": "advanced", "years": 4},
                    {"name": "PostgreSQL", "category": "Database", "proficiency": "intermediate", "years": 3},
                    {"name": "Docker", "category": "DevOps", "proficiency": "intermediate", "years": 2},
                    {"name": "AWS", "category": "Cloud", "proficiency": "beginner", "years": 1}
                ]
            },
            {
                "user": {
                    "id": "jane_smith_002",
                    "name": "Jane Smith",
                    "email": "jane.smith@company.com",
                    "password_hash": "password123",
                    "role": "consultant",
                    "department": "Data Science"
                },
                "profile": {
                    "primary_skill": "Data Science & ML",
                    "experience_years": 6,
                    "bench_start_date": "2024-02-01",
                    "current_status": "available"
                },
                "skills": [
                    {"name": "Python", "category": "Programming", "proficiency": "expert", "years": 6},
                    {"name": "Machine Learning", "category": "AI/ML", "proficiency": "expert", "years": 5},
                    {"name": "TensorFlow", "category": "AI/ML", "proficiency": "advanced", "years": 4},
                    {"name": "PyTorch", "category": "AI/ML", "proficiency": "advanced", "years": 3},
                    {"name": "SQL", "category": "Database", "proficiency": "expert", "years": 6},
                    {"name": "Pandas", "category": "Data Analysis", "proficiency": "expert", "years": 5},
                    {"name": "Jupyter", "category": "Tools", "proficiency": "expert", "years": 4},
                    {"name": "Docker", "category": "DevOps", "proficiency": "intermediate", "years": 2},
                    {"name": "Kubernetes", "category": "DevOps", "proficiency": "beginner", "years": 1}
                ]
            },
            {
                "user": {
                    "id": "mike_johnson_003",
                    "name": "Mike Johnson",
                    "email": "mike.johnson@company.com",
                    "password_hash": "password123",
                    "role": "consultant",
                    "department": "DevOps"
                },
                "profile": {
                    "primary_skill": "DevOps Engineering",
                    "experience_years": 7,
                    "bench_start_date": "2024-01-20",
                    "current_status": "available"
                },
                "skills": [
                    {"name": "AWS", "category": "Cloud", "proficiency": "expert", "years": 6},
                    {"name": "Docker", "category": "DevOps", "proficiency": "expert", "years": 5},
                    {"name": "Kubernetes", "category": "DevOps", "proficiency": "expert", "years": 4},
                    {"name": "Terraform", "category": "Infrastructure", "proficiency": "advanced", "years": 3},
                    {"name": "Jenkins", "category": "CI/CD", "proficiency": "advanced", "years": 4},
                    {"name": "Python", "category": "Programming", "proficiency": "intermediate", "years": 3},
                    {"name": "Bash", "category": "Scripting", "proficiency": "expert", "years": 7},
                    {"name": "Ansible", "category": "Configuration", "proficiency": "intermediate", "years": 2},
                    {"name": "Monitoring", "category": "Operations", "proficiency": "advanced", "years": 5}
                ]
            },
            {
                "user": {
                    "id": "sarah_wilson_004",
                    "name": "Sarah Wilson",
                    "email": "sarah.wilson@company.com",
                    "password_hash": "password123",
                    "role": "consultant",
                    "department": "Frontend"
                },
                "profile": {
                    "primary_skill": "Frontend Development",
                    "experience_years": 4,
                    "bench_start_date": "2024-02-10",
                    "current_status": "available"
                },
                "skills": [
                    {"name": "React", "category": "Frontend", "proficiency": "expert", "years": 4},
                    {"name": "Angular", "category": "Frontend", "proficiency": "advanced", "years": 3},
                    {"name": "Vue.js", "category": "Frontend", "proficiency": "intermediate", "years": 2},
                    {"name": "TypeScript", "category": "Programming", "proficiency": "advanced", "years": 3},
                    {"name": "JavaScript", "category": "Programming", "proficiency": "expert", "years": 4},
                    {"name": "CSS", "category": "Styling", "proficiency": "expert", "years": 4},
                    {"name": "SCSS", "category": "Styling", "proficiency": "advanced", "years": 3},
                    {"name": "Tailwind", "category": "Styling", "proficiency": "intermediate", "years": 1},
                    {"name": "Figma", "category": "Design", "proficiency": "intermediate", "years": 2}
                ]
            },
            {
                "user": {
                    "id": "david_brown_005",
                    "name": "David Brown",
                    "email": "david.brown@company.com",
                    "password_hash": "password123",
                    "role": "consultant",
                    "department": "Backend"
                },
                "profile": {
                    "primary_skill": "Backend Development",
                    "experience_years": 8,
                    "bench_start_date": "2024-01-05",
                    "current_status": "available"
                },
                "skills": [
                    {"name": "Java", "category": "Programming", "proficiency": "expert", "years": 8},
                    {"name": "Spring Boot", "category": "Framework", "proficiency": "expert", "years": 6},
                    {"name": "Python", "category": "Programming", "proficiency": "advanced", "years": 4},
                    {"name": "Django", "category": "Framework", "proficiency": "advanced", "years": 3},
                    {"name": "PostgreSQL", "category": "Database", "proficiency": "expert", "years": 7},
                    {"name": "MongoDB", "category": "Database", "proficiency": "intermediate", "years": 3},
                    {"name": "Redis", "category": "Cache", "proficiency": "advanced", "years": 4},
                    {"name": "REST API", "category": "Architecture", "proficiency": "expert", "years": 6},
                    {"name": "Microservices", "category": "Architecture", "proficiency": "advanced", "years": 4}
                ]
            }
        ]
        
        # Admin users
        admin_data = [
            {
                "id": "admin_001",
                "name": "Admin User",
                "email": "admin@company.com",
                "password_hash": "admin123",
                "role": "admin",
                "department": "Administration"
            },
            {
                "id": "hr_admin_002",
                "name": "HR Manager",
                "email": "hr.manager@company.com",
                "password_hash": "hr123",
                "role": "admin",
                "department": "Human Resources"
            }
        ]
        
        print("👥 Creating consultant users and profiles...")
        consultant_profiles = []
        
        for data in sample_data:
            # Create user
            user = User(**data["user"])
            db.add(user)
            db.flush()  # Get the user ID
            
            # Create consultant profile
            profile = ConsultantProfile(
                user_id=user.id,
                **data["profile"]
            )
            db.add(profile)
            db.flush()  # Get the profile ID
            consultant_profiles.append(profile)
            
            # Create skills
            for skill_data in data["skills"]:
                skill = ConsultantSkill(
                    consultant_id=profile.id,
                    skill_name=skill_data["name"],
                    skill_category=skill_data["category"],
                    proficiency_level=skill_data["proficiency"],
                    years_experience=skill_data["years"],
                    source="manual",
                    confidence_score=0.9
                )
                db.add(skill)
            
            print(f"✅ Created consultant: {user.name} with {len(data['skills'])} skills")
        
        print("👑 Creating admin users...")
        for admin in admin_data:
            user = User(**admin)
            db.add(user)
            print(f"✅ Created admin: {user.name}")
        
        # Create sample opportunities with specific skill requirements
        print("🚀 Creating sample opportunities...")
        opportunities = [
            {
                "title": "React Frontend Developer",
                "description": "Build modern web applications using React and TypeScript",
                "client_name": "TechCorp Solutions",
                "required_skills": ["React", "TypeScript", "JavaScript", "CSS"],
                "experience_level": "mid",
                "project_duration": "6 months",
                "budget_range": "$80k - $100k",
                "start_date": "2024-09-01",
                "end_date": "2025-03-01",
                "status": "open"
            },
            {
                "title": "Data Science Consultant",
                "description": "Build ML models and data pipelines for analytics platform",
                "client_name": "DataTech Inc",
                "required_skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Pandas"],
                "experience_level": "senior",
                "project_duration": "8 months",
                "budget_range": "$120k - $150k",
                "start_date": "2024-10-15",
                "end_date": "2025-06-15",
                "status": "open"
            },
            {
                "title": "DevOps Engineer",
                "description": "Implement CI/CD pipelines and cloud infrastructure",
                "client_name": "CloudFirst Ltd",
                "required_skills": ["AWS", "Docker", "Kubernetes", "Jenkins", "Terraform"],
                "experience_level": "senior",
                "project_duration": "12 months",
                "budget_range": "$130k - $160k",
                "start_date": "2024-09-15",
                "end_date": "2025-09-15",
                "status": "open"
            },
            {
                "title": "Full Stack Developer",
                "description": "Develop end-to-end web application with modern stack",
                "client_name": "StartupTech",
                "required_skills": ["React", "Node.js", "JavaScript", "PostgreSQL", "Docker"],
                "experience_level": "mid",
                "project_duration": "4 months",
                "budget_range": "$70k - $90k",
                "start_date": "2024-08-20",
                "end_date": "2024-12-20",
                "status": "open"
            },
            {
                "title": "Backend API Developer",
                "description": "Build scalable REST APIs and microservices",
                "client_name": "Enterprise Corp",
                "required_skills": ["Java", "Spring Boot", "PostgreSQL", "REST API", "Microservices"],
                "experience_level": "senior",
                "project_duration": "10 months",
                "budget_range": "$110k - $140k",
                "start_date": "2024-10-01",
                "end_date": "2025-08-01",
                "status": "open"
            }
        ]
        
        for opp_data in opportunities:
            # Convert required_skills to JSON string
            opp_data["required_skills"] = json.dumps(opp_data["required_skills"])
            opportunity = ProjectOpportunity(**opp_data)
            db.add(opportunity)
            print(f"✅ Created opportunity: {opportunity.title}")
        
        # Create some attendance records
        print("📅 Creating sample attendance records...")
        today = datetime.now()
        for i, profile in enumerate(consultant_profiles):
            # Create attendance for last 30 days
            for day_offset in range(30):
                date = today - timedelta(days=day_offset)
                if date.weekday() < 5:  # Weekdays only
                    status = "present" if day_offset % 7 != 0 else "absent"  # Mostly present
                    attendance = AttendanceRecord(
                        user_id=profile.user_id,
                        date=date.strftime("%Y-%m-%d"),
                        status=status,
                        check_in_time="09:00" if status == "present" else None,
                        check_out_time="18:00" if status == "present" else None,
                        hours_worked=8.0 if status == "present" else 0.0,
                        location="office"
                    )
                    db.add(attendance)
        
        # Commit all changes
        db.commit()
        print("💾 All data committed successfully!")
        
        # Print summary
        total_users = db.query(User).count()
        total_consultants = db.query(ConsultantProfile).count()
        total_skills = db.query(ConsultantSkill).count()
        total_opportunities = db.query(ProjectOpportunity).count()
        total_attendance = db.query(AttendanceRecord).count()
        
        print(f"""
🎉 SAMPLE DATA CREATION COMPLETE!

📊 Summary:
   👥 Users: {total_users} (5 consultants + 2 admins)
   💼 Consultant Profiles: {total_consultants}
   🛠️ Skills: {total_skills}
   🚀 Opportunities: {total_opportunities}
   📅 Attendance Records: {total_attendance}

🔐 LOGIN CREDENTIALS:

📋 CONSULTANTS:
   • john.doe@company.com / password123 (Full Stack - React, Node.js, Python)
   • jane.smith@company.com / password123 (Data Science - ML, Python, TensorFlow)
   • mike.johnson@company.com / password123 (DevOps - AWS, Docker, Kubernetes)
   • sarah.wilson@company.com / password123 (Frontend - React, Angular, TypeScript)
   • david.brown@company.com / password123 (Backend - Java, Spring Boot, PostgreSQL)

👑 ADMINS:
   • admin@company.com / admin123
   • hr.manager@company.com / hr123

🎯 Each consultant has 8-9 diverse skills with proper proficiency levels!
🚀 5 opportunities created that match different consultant skill sets!
        """)
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_users_and_consultants()
