"""
Training and Certification Agent
AI-powered training recommendations and progress tracking
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingAgent:
    """AI-powered training and certification agent"""
    
    def __init__(self):
        self.name = "TrainingAgent"
        self.version = "1.0.0"
        self.capabilities = [
            "skill_gap_analysis",
            "training_recommendations", 
            "certification_planning",
            "progress_tracking",
            "learning_path_optimization"
        ]
        
        # Training database (in production, this would come from a real training API)
        self.training_catalog = self._initialize_training_catalog()
        
    def _initialize_training_catalog(self) -> Dict[str, List[Dict]]:
        """Initialize comprehensive training catalog"""
        return {
            "cloud_computing": [
                {
                    "id": "aws_solutions_architect",
                    "title": "AWS Solutions Architect Associate",
                    "provider": "Amazon Web Services",
                    "duration_hours": 60,
                    "difficulty": "Intermediate",
                    "cost": 150.0,
                    "certification": True,
                    "cert_name": "AWS Certified Solutions Architect - Associate",
                    "skills": ["AWS", "Cloud Architecture", "EC2", "S3", "VPC", "IAM"],
                    "prerequisites": ["Basic Cloud Knowledge", "Networking Fundamentals"],
                    "market_demand": 95,
                    "career_impact": "High",
                    "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                    "rating": 4.8
                },
                {
                    "id": "azure_fundamentals",
                    "title": "Microsoft Azure Fundamentals",
                    "provider": "Microsoft",
                    "duration_hours": 40,
                    "difficulty": "Beginner",
                    "cost": 99.0,
                    "certification": True,
                    "cert_name": "Microsoft Certified: Azure Fundamentals",
                    "skills": ["Azure", "Cloud Concepts", "Azure Services", "Security"],
                    "prerequisites": [],
                    "market_demand": 90,
                    "career_impact": "High",
                    "url": "https://docs.microsoft.com/en-us/learn/certifications/azure-fundamentals/",
                    "rating": 4.7
                },
                {
                    "id": "kubernetes_fundamentals",
                    "title": "Kubernetes Fundamentals",
                    "provider": "Linux Foundation",
                    "duration_hours": 50,
                    "difficulty": "Intermediate",
                    "cost": 199.0,
                    "certification": True,
                    "cert_name": "Certified Kubernetes Administrator (CKA)",
                    "skills": ["Kubernetes", "Container Orchestration", "Docker", "DevOps"],
                    "prerequisites": ["Docker Basics", "Linux Commands"],
                    "market_demand": 88,
                    "career_impact": "High",
                    "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/",
                    "rating": 4.6
                }
            ],
            "programming": [
                {
                    "id": "nodejs_complete",
                    "title": "Complete Node.js Developer Course",
                    "provider": "Udemy",
                    "duration_hours": 35,
                    "difficulty": "Intermediate", 
                    "cost": 89.99,
                    "certification": False,
                    "skills": ["Node.js", "Express.js", "MongoDB", "RESTful APIs"],
                    "prerequisites": ["JavaScript Basics"],
                    "market_demand": 85,
                    "career_impact": "High",
                    "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
                    "rating": 4.7
                },
                {
                    "id": "react_complete",
                    "title": "Complete React Developer Course",
                    "provider": "Udemy", 
                    "duration_hours": 40,
                    "difficulty": "Intermediate",
                    "cost": 94.99,
                    "certification": False,
                    "skills": ["React", "Redux", "React Hooks", "Context API"],
                    "prerequisites": ["JavaScript ES6", "HTML/CSS"],
                    "market_demand": 92,
                    "career_impact": "High",
                    "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
                    "rating": 4.8
                },
                {
                    "id": "python_data_science",
                    "title": "Python for Data Science and Machine Learning",
                    "provider": "Coursera",
                    "duration_hours": 60,
                    "difficulty": "Intermediate",
                    "cost": 49.0,
                    "certification": True,
                    "cert_name": "Python for Data Science Specialization",
                    "skills": ["Python", "Pandas", "NumPy", "Matplotlib", "Scikit-learn"],
                    "prerequisites": ["Python Basics"],
                    "market_demand": 89,
                    "career_impact": "High",
                    "url": "https://www.coursera.org/specializations/python-data-science",
                    "rating": 4.6
                }
            ],
            "database": [
                {
                    "id": "postgresql_mastery",
                    "title": "PostgreSQL Database Administration",
                    "provider": "PostgreSQL Global Development Group",
                    "duration_hours": 45,
                    "difficulty": "Intermediate",
                    "cost": 0.0,
                    "certification": False,
                    "skills": ["PostgreSQL", "Database Design", "SQL Optimization", "Backup & Recovery"],
                    "prerequisites": ["SQL Basics"],
                    "market_demand": 78,
                    "career_impact": "Medium",
                    "url": "https://www.postgresql.org/docs/current/tutorial.html",
                    "rating": 4.5
                },
                {
                    "id": "mongodb_developer",
                    "title": "MongoDB Developer Certification",
                    "provider": "MongoDB University",
                    "duration_hours": 30,
                    "difficulty": "Intermediate", 
                    "cost": 150.0,
                    "certification": True,
                    "cert_name": "MongoDB Certified Developer Associate",
                    "skills": ["MongoDB", "NoSQL", "Aggregation Pipeline", "Indexing"],
                    "prerequisites": ["Database Fundamentals"],
                    "market_demand": 82,
                    "career_impact": "Medium",
                    "url": "https://university.mongodb.com/certification",
                    "rating": 4.4
                }
            ],
            "ai_ml": [
                {
                    "id": "machine_learning_basics",
                    "title": "Machine Learning Fundamentals",
                    "provider": "Stanford Online",
                    "duration_hours": 55,
                    "difficulty": "Intermediate",
                    "cost": 0.0,
                    "certification": True,
                    "cert_name": "Machine Learning Certificate",
                    "skills": ["Machine Learning", "Python", "TensorFlow", "Data Analysis"],
                    "prerequisites": ["Python", "Statistics", "Linear Algebra"],
                    "market_demand": 94,
                    "career_impact": "High",
                    "url": "https://www.coursera.org/learn/machine-learning",
                    "rating": 4.9
                },
                {
                    "id": "ai_for_everyone",
                    "title": "AI for Everyone",
                    "provider": "deeplearning.ai",
                    "duration_hours": 25,
                    "difficulty": "Beginner",
                    "cost": 49.0,
                    "certification": True,
                    "cert_name": "AI for Everyone Certificate",
                    "skills": ["AI Concepts", "Machine Learning Basics", "AI Strategy"],
                    "prerequisites": [],
                    "market_demand": 91,
                    "career_impact": "Medium",
                    "url": "https://www.coursera.org/learn/ai-for-everyone",
                    "rating": 4.7
                }
            ]
        }
    
    async def analyze_skill_gaps(self, consultant_skills: List[str], target_skills: List[str]) -> Dict[str, Any]:
        """Analyze gaps between current and target skills"""
        try:
            current_skills_lower = [skill.lower().strip() for skill in consultant_skills]
            target_skills_lower = [skill.lower().strip() for skill in target_skills]
            
            # Find missing skills
            missing_skills = []
            for target_skill in target_skills:
                if target_skill.lower().strip() not in current_skills_lower:
                    missing_skills.append(target_skill)
            
            # Calculate skill coverage
            matching_skills = []
            for target_skill in target_skills:
                if target_skill.lower().strip() in current_skills_lower:
                    matching_skills.append(target_skill)
            
            coverage_percentage = (len(matching_skills) / len(target_skills)) * 100 if target_skills else 100
            
            return {
                "success": True,
                "analysis": {
                    "total_target_skills": len(target_skills),
                    "matching_skills": matching_skills,
                    "missing_skills": missing_skills,
                    "coverage_percentage": round(coverage_percentage, 1),
                    "priority_gaps": missing_skills[:3],  # Top 3 priority gaps
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Skill gap analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_training_recommendations(self, consultant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized training recommendations"""
        try:
            current_skills = consultant_data.get("skills", [])
            missing_skills = consultant_data.get("missing_skills", [])
            experience_level = consultant_data.get("experience_level", "intermediate")
            career_goals = consultant_data.get("career_goals", [])
            
            recommendations = []
            
            # Analyze each missing skill and find relevant training
            for missing_skill in missing_skills:
                skill_recommendations = self._find_training_for_skill(missing_skill.lower())
                
                for training in skill_recommendations:
                    # Calculate recommendation score
                    score = self._calculate_recommendation_score(
                        training, current_skills, experience_level
                    )
                    
                    recommendation = {
                        "training_id": training["id"],
                        "title": training["title"],
                        "provider": training["provider"],
                        "duration_hours": training["duration_hours"],
                        "difficulty": training["difficulty"],
                        "cost": training["cost"],
                        "certification_available": training.get("certification", False),
                        "certification_name": training.get("cert_name", ""),
                        "skills_covered": training["skills"],
                        "prerequisites": training.get("prerequisites", []),
                        "url": training["url"],
                        "rating": training["rating"],
                        "recommendation_score": score,
                        "priority": self._get_priority_level(score),
                        "market_demand": training["market_demand"],
                        "career_impact": training["career_impact"],
                        "reason": self._generate_recommendation_reason(training, missing_skill),
                        "estimated_roi": self._calculate_training_roi(training)
                    }
                    recommendations.append(recommendation)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
            
            # Create learning paths
            learning_paths = self._create_learning_paths(recommendations, missing_skills)
            
            return {
                "success": True,
                "consultant_id": consultant_data.get("consultant_id"),
                "recommendations": recommendations[:10],  # Top 10 recommendations
                "learning_paths": learning_paths,
                "summary": {
                    "total_recommendations": len(recommendations),
                    "high_priority": len([r for r in recommendations if r["priority"] == "High"]),
                    "with_certification": len([r for r in recommendations if r["certification_available"]]),
                    "estimated_total_hours": sum(r["duration_hours"] for r in recommendations[:5]),
                    "estimated_total_cost": sum(r["cost"] for r in recommendations[:5])
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Training recommendation generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _find_training_for_skill(self, skill: str) -> List[Dict]:
        """Find training programs that cover a specific skill"""
        relevant_training = []
        
        for category, programs in self.training_catalog.items():
            for program in programs:
                program_skills = [s.lower() for s in program["skills"]]
                if any(skill in ps or ps in skill for ps in program_skills):
                    relevant_training.append(program)
        
        return relevant_training
    
    def _calculate_recommendation_score(self, training: Dict, current_skills: List[str], experience_level: str) -> float:
        """Calculate recommendation score based on multiple factors"""
        score = 0.0
        
        # Market demand factor (0-30 points)
        score += (training["market_demand"] / 100) * 30
        
        # Rating factor (0-20 points)
        score += (training["rating"] / 5) * 20
        
        # Experience level match (0-20 points)
        difficulty_map = {"beginner": 1, "intermediate": 2, "advanced": 3}
        exp_level_map = {"junior": 1, "intermediate": 2, "senior": 3}
        
        training_level = difficulty_map.get(training["difficulty"].lower(), 2)
        consultant_level = exp_level_map.get(experience_level.lower(), 2)
        
        level_diff = abs(training_level - consultant_level)
        if level_diff == 0:
            score += 20
        elif level_diff == 1:
            score += 15
        else:
            score += 5
        
        # Career impact factor (0-15 points)
        impact_map = {"high": 15, "medium": 10, "low": 5}
        score += impact_map.get(training["career_impact"].lower(), 10)
        
        # Cost efficiency factor (0-15 points)
        if training["cost"] == 0:
            score += 15
        elif training["cost"] <= 100:
            score += 12
        elif training["cost"] <= 200:
            score += 8
        else:
            score += 3
        
        return round(score, 1)
    
    def _get_priority_level(self, score: float) -> str:
        """Convert numerical score to priority level"""
        if score >= 80:
            return "High"
        elif score >= 60:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendation_reason(self, training: Dict, missing_skill: str) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        if training["market_demand"] > 85:
            reasons.append("high market demand")
        
        if training["certification"]:
            reasons.append("industry-recognized certification")
        
        if training["cost"] == 0:
            reasons.append("free course")
        
        if training["rating"] >= 4.5:
            reasons.append("highly rated")
        
        if missing_skill.lower() in [s.lower() for s in training["skills"]]:
            reasons.append(f"directly addresses {missing_skill} skill gap")
        
        if len(reasons) == 0:
            reasons.append("relevant to your career goals")
        
        return f"Recommended due to {', '.join(reasons[:3])}"
    
    def _calculate_training_roi(self, training: Dict) -> str:
        """Calculate estimated ROI for training"""
        if training["career_impact"] == "High" and training["market_demand"] > 85:
            return "Very High"
        elif training["career_impact"] == "High" or training["market_demand"] > 75:
            return "High"
        elif training["career_impact"] == "Medium" or training["market_demand"] > 60:
            return "Medium"
        else:
            return "Low"
    
    def _create_learning_paths(self, recommendations: List[Dict], missing_skills: List[str]) -> List[Dict]:
        """Create structured learning paths"""
        paths = []
        
        # Group recommendations by skill area
        skill_groups = {}
        for rec in recommendations:
            for skill in rec["skills_covered"]:
                if skill.lower() in [ms.lower() for ms in missing_skills]:
                    if skill not in skill_groups:
                        skill_groups[skill] = []
                    skill_groups[skill].append(rec)
        
        # Create learning path for each skill group
        for skill, trainings in skill_groups.items():
            if len(trainings) > 1:
                # Sort by difficulty and create progression
                trainings.sort(key=lambda x: {"beginner": 1, "intermediate": 2, "advanced": 3}.get(x["difficulty"].lower(), 2))
                
                path = {
                    "skill_focus": skill,
                    "total_duration_hours": sum(t["duration_hours"] for t in trainings),
                    "total_cost": sum(t["cost"] for t in trainings),
                    "progression": [
                        {
                            "step": i + 1,
                            "training_id": t["training_id"],
                            "title": t["title"],
                            "duration_hours": t["duration_hours"],
                            "difficulty": t["difficulty"],
                            "certification": t["certification_available"]
                        }
                        for i, t in enumerate(trainings)
                    ]
                }
                paths.append(path)
        
        return paths[:3]  # Return top 3 learning paths
    
    async def track_training_progress(self, enrollment_id: int, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and update training progress"""
        try:
            # In a real implementation, this would update the database
            progress = {
                "enrollment_id": enrollment_id,
                "current_progress": progress_data.get("progress_percentage", 0),
                "milestone": progress_data.get("milestone", ""),
                "time_spent_hours": progress_data.get("time_spent_hours", 0),
                "status": self._calculate_status(progress_data.get("progress_percentage", 0)),
                "updated_at": datetime.now().isoformat(),
                "next_milestone": self._get_next_milestone(progress_data.get("progress_percentage", 0)),
                "estimated_completion": self._estimate_completion_date(
                    progress_data.get("progress_percentage", 0),
                    progress_data.get("total_duration_hours", 40)
                )
            }
            
            return {"success": True, "progress": progress}
            
        except Exception as e:
            logger.error(f"Progress tracking failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _calculate_status(self, progress_percentage: float) -> str:
        """Calculate training status based on progress"""
        if progress_percentage == 0:
            return "not_started"
        elif progress_percentage < 25:
            return "getting_started"
        elif progress_percentage < 50:
            return "progressing_well"
        elif progress_percentage < 75:
            return "more_than_halfway"
        elif progress_percentage < 100:
            return "nearly_complete"
        else:
            return "completed"
    
    def _get_next_milestone(self, progress_percentage: float) -> str:
        """Get next milestone based on current progress"""
        if progress_percentage < 25:
            return "Complete first quarter of course"
        elif progress_percentage < 50:
            return "Reach halfway point"
        elif progress_percentage < 75:
            return "Complete three quarters"
        elif progress_percentage < 100:
            return "Complete final assessments"
        else:
            return "Course completed!"
    
    def _estimate_completion_date(self, progress_percentage: float, total_hours: int) -> str:
        """Estimate completion date based on current progress"""
        if progress_percentage >= 100:
            return "Completed"
        
        remaining_percentage = 100 - progress_percentage
        remaining_hours = (remaining_percentage / 100) * total_hours
        
        # Assume 5 hours per week study time
        weeks_remaining = remaining_hours / 5
        completion_date = datetime.now() + timedelta(weeks=weeks_remaining)
        
        return completion_date.strftime("%Y-%m-%d")
    
    async def generate_skill_development_plan(self, consultant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive skill development plan"""
        try:
            current_skills = consultant_data.get("skills", [])
            target_skills = consultant_data.get("target_skills", [])
            experience_years = consultant_data.get("experience_years", 3)
            
            # Analyze skill gaps
            gap_analysis = await self.analyze_skill_gaps(current_skills, target_skills)
            
            if not gap_analysis["success"]:
                return gap_analysis
            
            # Generate training recommendations
            recommendations = await self.generate_training_recommendations({
                **consultant_data,
                "missing_skills": gap_analysis["analysis"]["missing_skills"]
            })
            
            if not recommendations["success"]:
                return recommendations
            
            # Create development plan
            plan = {
                "consultant_id": consultant_data.get("consultant_id"),
                "plan_title": f"Skill Development Plan for {consultant_data.get('name', 'Consultant')}",
                "current_level": self._assess_current_level(experience_years, len(current_skills)),
                "target_level": "Advanced",
                "skill_gap_analysis": gap_analysis["analysis"],
                "recommended_trainings": recommendations["recommendations"][:5],
                "learning_paths": recommendations["learning_paths"],
                "timeline": self._create_development_timeline(recommendations["recommendations"][:5]),
                "milestones": self._create_milestones(gap_analysis["analysis"]["missing_skills"]),
                "success_metrics": self._define_success_metrics(target_skills),
                "estimated_duration_months": self._estimate_plan_duration(recommendations["recommendations"][:5]),
                "total_investment": recommendations["summary"]["estimated_total_cost"],
                "created_at": datetime.now().isoformat()
            }
            
            return {"success": True, "development_plan": plan}
            
        except Exception as e:
            logger.error(f"Skill development plan generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _assess_current_level(self, experience_years: int, skill_count: int) -> str:
        """Assess consultant's current level"""
        if experience_years < 2 or skill_count < 5:
            return "Beginner"
        elif experience_years < 5 or skill_count < 12:
            return "Intermediate"
        else:
            return "Advanced"
    
    def _create_development_timeline(self, trainings: List[Dict]) -> List[Dict]:
        """Create timeline for skill development"""
        timeline = []
        current_date = datetime.now()
        
        for i, training in enumerate(trainings):
            start_date = current_date + timedelta(weeks=i*2)  # Start each training 2 weeks apart
            end_date = start_date + timedelta(hours=training["duration_hours"]/10)  # Assume 10 hours per week
            
            timeline.append({
                "phase": i + 1,
                "training_title": training["title"],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration_weeks": round((end_date - start_date).days / 7),
                "skills_gained": training["skills_covered"]
            })
        
        return timeline
    
    def _create_milestones(self, missing_skills: List[str]) -> List[Dict]:
        """Create milestones for tracking progress"""
        milestones = []
        
        for i, skill in enumerate(missing_skills[:5]):
            milestones.append({
                "milestone_id": i + 1,
                "title": f"Master {skill}",
                "description": f"Complete training and demonstrate proficiency in {skill}",
                "target_date": (datetime.now() + timedelta(weeks=(i+1)*8)).strftime("%Y-%m-%d"),
                "success_criteria": [
                    f"Complete relevant {skill} training course",
                    f"Pass {skill} assessment with 80%+ score",
                    f"Apply {skill} in a real project"
                ]
            })
        
        return milestones
    
    def _define_success_metrics(self, target_skills: List[str]) -> Dict[str, Any]:
        """Define measurable success metrics"""
        return {
            "skill_acquisition": {
                "target": len(target_skills),
                "metric": "Number of new skills mastered",
                "measurement": "Completed training + practical application"
            },
            "certification_goals": {
                "target": "2-3 industry certifications",
                "metric": "Professional certifications earned",
                "measurement": "Valid certificates obtained"
            },
            "project_application": {
                "target": "Apply skills in real projects",
                "metric": "Practical skill demonstration",
                "measurement": "Project portfolio updates"
            },
            "market_readiness": {
                "target": "80%+ skill match for target roles",
                "metric": "Job market competitiveness",
                "measurement": "Opportunity matching score"
            }
        }
    
    def _estimate_plan_duration(self, trainings: List[Dict]) -> int:
        """Estimate total duration for development plan in months"""
        total_hours = sum(t["duration_hours"] for t in trainings)
        # Assume 10 hours per week study time
        weeks_needed = total_hours / 10
        months_needed = weeks_needed / 4
        return max(3, round(months_needed))  # Minimum 3 months
    
    async def get_training_catalog(self, category: str = "all") -> Dict[str, Any]:
        """Get training catalog by category or all categories"""
        try:
            if category == "all":
                catalog = self.training_catalog
            else:
                catalog = {category: self.training_catalog.get(category, [])}
            
            # Format for API response
            formatted_catalog = {}
            for cat, programs in catalog.items():
                formatted_catalog[cat] = {
                    "category_name": cat.replace("_", " ").title(),
                    "programs": programs,
                    "program_count": len(programs)
                }
            
            return {
                "success": True,
                "catalog": formatted_catalog,
                "total_programs": sum(len(programs) for programs in catalog.values()),
                "categories": list(formatted_catalog.keys())
            }
            
        except Exception as e:
            logger.error(f"Training catalog retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve training catalog: {str(e)}"
            }
