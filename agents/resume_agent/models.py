"""
Resume Analysis Models
Data models and schemas for resume analysis
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass
class SkillCategory:
    """Skill category classification"""
    name: str
    skills: List[str]
    confidence: float

@dataclass
class ResumeAnalysisResult:
    """Complete resume analysis result"""
    success: bool
    filename: str
    skills: List[str]
    soft_skills: List[str]
    competencies: List[str]
    roles: List[str]
    skill_categories: Dict[str, List[str]]
    skill_vector: List[float]
    ai_summary: str
    ai_feedback: str
    ai_suggestions: str
    confidence_score: float
    total_skills: int
    analysis_method: str
    extracted_text: str
    error_message: Optional[str] = None

@dataclass
class ConsultantSkill:
    """Consultant skill for database storage"""
    skill_name: str
    category: str
    proficiency_level: str
    confidence_score: int
    source: str
    skill_vector: Optional[List[float]] = None

@dataclass
class SkillSyncResult:
    """Result of skill synchronization to database"""
    success: bool
    consultant_id: int
    skills_added: int
    skills_updated: int
    skills_list: List[ConsultantSkill]
    error_message: Optional[str] = None
