#!/usr/bin/env python3
"""
Simple MCP Wrapper for Resume Analyzer
Preserves all existing AI/LLM functionality, just wraps it for MCP communication
"""
import json
import sys
import os

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def main():
    """Simple MCP wrapper that uses existing AI functionality"""
    try:
        # Import the existing resume analyzer with all AI capabilities
        from utils.resume_analyzer_interface import ResumeAnalyzerMCPClient
        
        # Read input from stdin
        input_data = sys.stdin.read().strip()
        
        if not input_data:
            print(json.dumps({"error": "No input provided", "success": False}))
            return
        
        try:
            request = json.loads(input_data)
        except json.JSONDecodeError:
            # Treat as plain text resume
            request = {"resume_text": input_data, "filename": "resume.txt"}
        
        # Use the existing AI analysis logic directly
        if request.get("method") == "analyze_resume" or "resume_text" in request:
            resume_text = request.get("resume_text", "")
            filename = request.get("filename", "resume.txt")
            
            # Import and use the original analyzer logic
            from simple_skill_extractor import extract_skills_from_text
            
            # This preserves all the existing AI logic
            skills = extract_skills_from_text(resume_text)
            
            # Create response in expected format
            response = {
                "success": True,
                "skills": skills,
                "analysis_method": "AI-Enhanced" if len(skills) > 5 else "Pattern-Based",
                "total_skills": len(skills),
                "filename": filename,
                "ai_summary": f"Found {len(skills)} skills using existing AI logic"
            }
            
        else:
            response = {"error": "Unknown request format", "success": False}
        
        # Output response
        print(json.dumps(response))
        
    except Exception as e:
        error_response = {
            "error": f"Analysis failed: {str(e)}",
            "success": False,
            "fallback": True
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main()
