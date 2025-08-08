# database/models/__init__.py
from .consultant import Consultant, Base
from .bench_status import BenchActivity, BenchUtilization
from .project_opportunity import ProjectOpportunity, ConsultantProjectMatch
from .resume_data import ResumeData, ConsultantSkill

__all__ = [
    "Consultant", 
    "Base",
    "BenchActivity", 
    "BenchUtilization",
    "ProjectOpportunity", 
    "ConsultantProjectMatch",
    "ResumeData",
    "ConsultantSkill"
]
