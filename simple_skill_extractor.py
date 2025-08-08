#!/usr/bin/env python3
"""
Simple Resume Skill Extractor
No external AI dependencies - just pattern matching
"""
import re
from typing import List, Dict, Any

def extract_skills_from_text(resume_text: str, filename: str = "resume.txt") -> Dict[str, Any]:
    """
    Extract skills from resume text using simple pattern matching
    
    Args:
        resume_text: The text content of the resume
        filename: Name of the uploaded file
    
    Returns:
        Dictionary containing extracted skills and analysis
    """
    
    # Comprehensive list of technical skills to detect
    TECHNICAL_SKILLS = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin',
        
        # Web Frameworks
        'React', 'Angular', 'Vue.js', 'Vue', 'Node.js', 'Express.js', 'Django', 'Flask', 'Spring Boot', 'Spring',
        'FastAPI', 'ASP.NET', 'Laravel', 'Rails', 'Next.js', 'Nuxt.js',
        
        # Databases
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server', 'SQLite',
        'Cassandra', 'DynamoDB', 'Neo4j',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'DevOps', 'Terraform',
        'Ansible', 'Git', 'GitHub', 'GitLab', 'Bitbucket',
        
        # Frontend Technologies
        'HTML', 'CSS', 'SCSS', 'Sass', 'Bootstrap', 'Tailwind CSS', 'Material-UI', 'jQuery',
        
        # Data & AI
        'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn',
        'Tableau', 'Power BI', 'Analytics', 'Big Data', 'Spark', 'Hadoop',
        
        # Mobile Development
        'React Native', 'Flutter', 'iOS', 'Android', 'Xamarin',
        
        # Other Technologies
        'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'JIRA', 'Confluence'
    ]
    
    # Soft skills to detect
    SOFT_SKILLS = [
        'Leadership', 'Communication', 'Problem Solving', 'Team Work', 'Teamwork',
        'Project Management', 'Critical Thinking', 'Adaptability', 'Time Management',
        'Collaboration', 'Creativity', 'Innovation', 'Mentoring'
    ]
    
    # Convert text to lowercase for case-insensitive matching
    resume_lower = resume_text.lower()
    
    # Extract technical skills
    extracted_technical_skills = []
    for skill in TECHNICAL_SKILLS:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, resume_lower):
            extracted_technical_skills.append(skill)
    
    # Extract soft skills
    extracted_soft_skills = []
    for skill in SOFT_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, resume_lower):
            extracted_soft_skills.append(skill)
    
    # Combine all skills
    all_skills = extracted_technical_skills + extracted_soft_skills
    
    # Categorize skills
    skill_categories = {}
    
    # Categorize technical skills
    for skill in extracted_technical_skills:
        category = categorize_technical_skill(skill)
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill)
    
    # Add soft skills if any
    if extracted_soft_skills:
        skill_categories['Soft Skills'] = extracted_soft_skills
    
    # Infer possible roles based on skills
    possible_roles = infer_roles_from_skills(extracted_technical_skills)
    
    # Generate a simple summary
    tech_count = len(extracted_technical_skills)
    soft_count = len(extracted_soft_skills)
    total_count = len(all_skills)
    
    summary = f"Resume analysis complete. Found {total_count} skills ({tech_count} technical, {soft_count} soft skills) across {len(skill_categories)} categories."
    
    return {
        "extracted_text": resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text,
        "skills": all_skills,
        "technical_skills": extracted_technical_skills,
        "soft_skills": extracted_soft_skills,
        "skill_categories": skill_categories,
        "competencies": list(skill_categories.keys()),
        "roles": possible_roles,
        "skill_vector": [1.0] * len(all_skills),  # Simplified vector
        "ai_summary": summary,
        "ai_feedback": "Skills successfully extracted using pattern matching analysis.",
        "ai_suggestions": "Consider adding specific project examples and quantifiable achievements to strengthen your profile.",
        "confidence_score": min(0.95, len(all_skills) / 25.0),  # Higher confidence for more skills
        "total_skills": total_count,
        "filename": filename,
        "processing_method": "pattern_matching"
    }

def categorize_technical_skill(skill: str) -> str:
    """Categorize a technical skill into a broader category"""
    skill_lower = skill.lower()
    
    # Programming languages
    if skill_lower in ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin']:
        return 'Programming Languages'
    
    # Web frameworks
    elif skill_lower in ['react', 'angular', 'vue.js', 'vue', 'node.js', 'express.js', 'django', 'flask', 'spring boot', 'spring', 'fastapi', 'asp.net', 'laravel', 'rails', 'next.js', 'nuxt.js']:
        return 'Web Frameworks'
    
    # Databases
    elif skill_lower in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server', 'sqlite', 'cassandra', 'dynamodb', 'neo4j']:
        return 'Databases'
    
    # Cloud & DevOps
    elif skill_lower in ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'devops', 'terraform', 'ansible', 'git', 'github', 'gitlab', 'bitbucket']:
        return 'Cloud & DevOps'
    
    # Frontend
    elif skill_lower in ['html', 'css', 'scss', 'sass', 'bootstrap', 'tailwind css', 'material-ui', 'jquery']:
        return 'Frontend Technologies'
    
    # Data & AI
    elif skill_lower in ['machine learning', 'ai', 'data science', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'tableau', 'power bi', 'analytics', 'big data', 'spark', 'hadoop']:
        return 'Data & AI'
    
    # Mobile
    elif skill_lower in ['react native', 'flutter', 'ios', 'android', 'xamarin']:
        return 'Mobile Development'
    
    # Other
    else:
        return 'Other Technologies'

def infer_roles_from_skills(technical_skills: List[str]) -> List[str]:
    """Infer possible job roles based on technical skills"""
    skills_lower = [skill.lower() for skill in technical_skills]
    roles = []
    
    # Frontend Developer
    frontend_skills = ['react', 'angular', 'vue.js', 'vue', 'html', 'css', 'javascript', 'typescript']
    if any(skill in skills_lower for skill in frontend_skills):
        roles.append('Frontend Developer')
    
    # Backend Developer
    backend_skills = ['python', 'java', 'node.js', 'django', 'flask', 'spring', 'sql', 'postgresql', 'mysql']
    if any(skill in skills_lower for skill in backend_skills):
        roles.append('Backend Developer')
    
    # Full Stack Developer
    if any(skill in skills_lower for skill in frontend_skills) and any(skill in skills_lower for skill in backend_skills):
        roles.append('Full Stack Developer')
    
    # DevOps Engineer
    devops_skills = ['aws', 'azure', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible']
    if any(skill in skills_lower for skill in devops_skills):
        roles.append('DevOps Engineer')
    
    # Data Scientist
    data_skills = ['python', 'machine learning', 'data science', 'tensorflow', 'pytorch', 'pandas', 'numpy']
    if any(skill in skills_lower for skill in data_skills):
        roles.append('Data Scientist')
    
    # Mobile Developer
    mobile_skills = ['react native', 'flutter', 'ios', 'android', 'swift', 'kotlin']
    if any(skill in skills_lower for skill in mobile_skills):
        roles.append('Mobile Developer')
    
    # Default to Software Developer if no specific role identified
    if not roles and technical_skills:
        roles.append('Software Developer')
    
    return roles
