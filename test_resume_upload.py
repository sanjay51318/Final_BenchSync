#!/usr/bin/env python3
"""
Test resume upload functionality
"""
import requests
import os

def test_resume_upload():
    """Test the resume upload endpoint"""
    print("🔍 Testing Resume Upload Functionality")
    print("=" * 50)
    
    # Create a test text file to simulate a resume
    test_resume_content = """
    John Doe
    Software Engineer
    
    Skills: Python, JavaScript, React, Node.js, SQL, AWS, Docker, Machine Learning
    
    Experience:
    - Senior Software Engineer at Tech Corp (2020-2023)
    - Full Stack Developer at StartupXYZ (2018-2020)
    
    Education:
    - Bachelor of Science in Computer Science
    
    Projects:
    - Built scalable web applications using React and Node.js
    - Implemented machine learning models for data analysis
    - Deployed applications on AWS cloud infrastructure
    """
    
    # Write test resume to file
    test_file_path = "test_resume_upload.txt"
    with open(test_file_path, "w") as f:
        f.write(test_resume_content)
    
    try:
        # Test the upload endpoint
        url = "http://localhost:8000/upload-resume"
        
        with open(test_file_path, "rb") as file:
            files = {"file": ("test_resume.txt", file, "text/plain")}
            data = {"consultant_email": "john.doe@example.com"}
            
            print(f"📤 Uploading resume for john.doe@example.com...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Resume upload successful!")
                print(f"📊 Analysis Summary:")
                print(f"   Skills: {result.get('skills', [])[:5]}...")
                print(f"   Competencies: {result.get('competencies', [])}")
                print(f"   Suggested Roles: {result.get('roles', [])}")
                print(f"   AI Summary: {result.get('ai_summary', '')[:100]}...")
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
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
    
    return False

if __name__ == "__main__":
    success = test_resume_upload()
    if success:
        print("\n🎉 Resume upload with AI analysis is working perfectly!")
        print("✅ Backend is ready for frontend integration")
    else:
        print("\n❌ Resume upload needs debugging")
