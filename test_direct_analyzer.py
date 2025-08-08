#!/usr/bin/env python3
"""
Direct test of MCP Resume Analyzer Server
"""
import sys
import os
import subprocess
import json

def test_resume_analyzer_direct():
    """Test the resume analyzer server directly"""
    
    # Paths
    server_path = os.path.join(os.getcwd(), "mcp_servers", "professional_resume_analyzer_server.py")
    python_path = "C:/Users/Sanjay N/anaconda3/python.exe"
    
    print(f"Server path: {server_path}")
    print(f"Server exists: {os.path.exists(server_path)}")
    
    # Test direct import
    try:
        sys.path.append("mcp_servers")
        from professional_resume_analyzer_server import ResumeAnalyzerMCP
        
        analyzer = ResumeAnalyzerMCP()
        print(f"✅ Resume Analyzer instantiated successfully")
        print(f"AI capabilities: {analyzer.has_ai}")
        
        # Test direct analysis
        test_resume = """
        John Doe
        Software Engineer
        
        SKILLS:
        - Python programming
        - React development
        - PostgreSQL database
        """
        
        if analyzer.has_ai:
            result = analyzer.extract_skills_advanced(test_resume)
            method = "AI-Enhanced"
        else:
            result = analyzer.extract_skills_basic(test_resume)
            method = "Pattern-Based"
            
        print(f"✅ Direct analysis successful using {method}")
        print(f"Skills found: {result.get('skills', [])}")
        print(f"Categories: {list(result.get('skill_categories', {}).keys())}")
        print(f"Total skills: {len(result.get('skills', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_resume_analyzer_direct()
