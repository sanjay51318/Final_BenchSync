import pytest
import asyncio
from agents.consultant_profiling_agent.agent import ConsultantProfilingAgent

@pytest.fixture
def profiling_agent():
    return ConsultantProfilingAgent()

@pytest.fixture
def sample_consultant_profile():
    return """
    Jane Doe - Senior Cloud Consultant
    Email: jane.doe@consulting.com
    
    Experience: 6 years in cloud architecture and DevOps
    
    Technical Skills:
    - AWS, Azure, Google Cloud
    - Docker, Kubernetes, Terraform
    - Python, Java, Node.js
    - CI/CD, Jenkins, GitLab
    
    Certifications:
    - AWS Solutions Architect Professional
    - Azure DevOps Engineer Expert
    
    Led cloud migration projects for 15+ enterprise clients.
    Strong leadership and client communication skills.
    """

@pytest.mark.asyncio
async def test_consultant_profile_analysis(profiling_agent, sample_consultant_profile):
    """Test consultant profile analysis"""
    result = await profiling_agent.analyze_consultant_profile(
        sample_consultant_profile, 
        "Jane Doe"
    )
    
    assert result["success"] == True
    assert result["consultant_name"] == "Jane Doe"
    assert len(result["technical_skills"]) > 0
    assert result["experience_years"] == 6.0
    assert "cloud" in " ".join(result["suitability_areas"]).lower()

@pytest.mark.asyncio 
async def test_skill_extraction(profiling_agent):
    """Test technical skill extraction"""
    text = "experienced in python, aws, docker, and kubernetes with react frontend development"
    preprocessed = profiling_agent.preprocess_text(text)
    info = profiling_agent.extract_consultant_information(preprocessed)
    
    skills_lower = [skill.lower() for skill in info["technical_skills"]]
    assert "python" in skills_lower
    assert "aws" in skills_lower or "Aws" in info["technical_skills"]

if __name__ == "__main__":
    pytest.main([__file__])
