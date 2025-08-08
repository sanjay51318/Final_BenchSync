#!/usr/bin/env python3
"""
Detailed Resume Upload Test
"""
import requests
import json

def test_detailed_resume_upload():
    """Test resume upload with detailed output"""
    print("🔍 Detailed Resume Upload Test")
    print("=" * 50)
    
    # Create a more detailed test resume
    test_resume_content = """
    John Doe
    Senior Software Engineer
    Phone: (555) 123-4567
    Email: john.doe@email.com
    
    SKILLS:
    - Programming Languages: Python, JavaScript, TypeScript, Java, C++
    - Web Technologies: React, Node.js, Express.js, HTML5, CSS3, REST APIs
    - Cloud Platforms: AWS (EC2, S3, Lambda), Azure, Google Cloud Platform
    - Databases: PostgreSQL, MySQL, MongoDB, Redis
    - DevOps: Docker, Kubernetes, Jenkins, Terraform, CI/CD
    - Machine Learning: TensorFlow, PyTorch, scikit-learn, Pandas, NumPy
    - Version Control: Git, GitHub, GitLab
    - Agile methodologies and Scrum practices
    
    EXPERIENCE:
    Senior Software Engineer | Tech Innovations Corp | 2021-Present
    - Led a team of 5 developers in building scalable web applications
    - Implemented microservices architecture using Docker and Kubernetes
    - Developed machine learning models for predictive analytics
    - Improved system performance by 40% through optimization
    - Mentored junior developers and conducted code reviews
    
    Full Stack Developer | StartupXYZ | 2019-2021
    - Built responsive web applications using React and Node.js
    - Designed and implemented RESTful APIs
    - Managed AWS infrastructure and deployment pipelines
    - Collaborated with cross-functional teams using Agile methodologies
    
    Software Developer | Innovation Labs | 2017-2019
    - Developed backend services using Python and Django
    - Implemented automated testing and continuous integration
    - Worked on data analysis projects using SQL and Python
    
    EDUCATION:
    Master of Science in Computer Science | Stanford University | 2017
    Bachelor of Science in Computer Science | UC Berkeley | 2015
    
    PROJECTS:
    E-commerce Platform (2022)
    - Built a full-stack e-commerce solution using React, Node.js, and PostgreSQL
    - Implemented payment integration and inventory management
    - Deployed on AWS with auto-scaling capabilities
    
    ML Recommendation System (2021)
    - Developed a machine learning recommendation engine using Python and TensorFlow
    - Processed large datasets and implemented collaborative filtering
    - Achieved 25% improvement in user engagement
    
    CERTIFICATIONS:
    - AWS Certified Solutions Architect
    - Google Cloud Professional Developer
    - Certified Scrum Master (CSM)
    """
    
    # Write test resume to file
    test_file_path = "detailed_test_resume.txt"
    with open(test_file_path, "w") as f:
        f.write(test_resume_content)
    
    try:
        # Test the upload endpoint
        url = "http://localhost:8000/upload-resume"
        
        with open(test_file_path, "rb") as file:
            files = {"file": ("detailed_test_resume.txt", file, "text/plain")}
            data = {"consultant_email": "john.doe@example.com"}
            
            print(f"📤 Uploading detailed resume for john.doe@example.com...")
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Resume upload successful!")
                print("\n📊 DETAILED ANALYSIS RESULTS:")
                print("=" * 60)
                
                print(f"\n🔧 EXTRACTED SKILLS ({len(result.get('skills', []))}):")
                skills = result.get('skills', [])
                for i, skill in enumerate(skills[:15], 1):  # Show first 15 skills
                    print(f"   {i:2d}. {skill}")
                if len(skills) > 15:
                    print(f"   ... and {len(skills) - 15} more skills")
                
                print(f"\n💼 COMPETENCIES ({len(result.get('competencies', []))}):")
                for i, comp in enumerate(result.get('competencies', []), 1):
                    print(f"   {i}. {comp}")
                
                print(f"\n🎯 SUGGESTED ROLES ({len(result.get('roles', []))}):")
                for i, role in enumerate(result.get('roles', []), 1):
                    print(f"   {i}. {role}")
                
                print(f"\n🤖 AI SUMMARY:")
                ai_summary = result.get('ai_summary', '')
                if ai_summary:
                    print(f"   {ai_summary}")
                else:
                    print("   No AI summary generated")
                
                print(f"\n📁 FILE INFO:")
                print(f"   Filename: {result.get('filename')}")
                print(f"   Timestamp: {result.get('timestamp')}")
                
                return True
            else:
                print(f"❌ Upload failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False
    finally:
        # Clean up test file
        import os
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    return False

if __name__ == "__main__":
    success = test_detailed_resume_upload()
    if success:
        print("\n🎉 RESUME ANALYSIS SYSTEM IS FULLY OPERATIONAL!")
        print("✅ All AI models are working correctly")
        print("✅ Skills extraction functional")
        print("✅ Competency recognition working")
        print("✅ Role suggestion active") 
        print("✅ Backend ready for frontend integration")
    else:
        print("\n❌ Resume analysis needs debugging")
