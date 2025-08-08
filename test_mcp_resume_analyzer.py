#!/usr/bin/env python3
"""
Test the Resume Analyzer MCP Server
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.getcwd())

from utils.resume_analyzer_interface import resume_analyzer_client

async def test_resume_analysis():
    """Test resume analysis functionality"""
    
    # Sample resume text
    resume_text = """
    John Doe
    Senior Software Engineer
    
    SKILLS:
    - Python programming with 5+ years experience
    - React and JavaScript frontend development
    - PostgreSQL database design and optimization
    - AWS cloud services and Docker containerization
    - Machine Learning with TensorFlow and PyTorch
    - DevOps with Kubernetes and Jenkins
    
    EXPERIENCE:
    Lead Software Engineer at TechCorp (2020-2025)
    - Built microservices using Python and Django
    - Developed React applications with TypeScript
    - Implemented CI/CD pipelines with Jenkins
    - Managed AWS infrastructure with Terraform
    """
    
    print("🔍 Testing Resume Analysis with MCP Server...")
    print("=" * 50)
    
    try:
        result = await resume_analyzer_client.analyze_resume(resume_text, "test_resume.txt")
        
        print(f"✅ Analysis successful!")
        print(f"📊 Analysis Method: {result.get('analysis_method', 'Unknown')}")
        print(f"🎯 Skills Found: {result.get('total_skills', 0)}")
        print(f"📈 Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"🤖 AI Summary: {result.get('ai_summary', 'N/A')}")
        print("\n🛠️ Extracted Skills:")
        
        skills_by_category = result.get('skill_categories', {})
        for category, skills in skills_by_category.items():
            print(f"  📁 {category}: {', '.join(skills)}")
        
        print(f"\n💼 Suggested Roles: {', '.join(result.get('roles', []))}")
        print(f"💡 AI Suggestions: {result.get('ai_suggestions', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_resume_analysis())
