import asyncio
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models.consultant import Consultant
from database.models.bench_status import BenchActivity, BenchUtilization

class BenchTrackingAgent:
    """Agent for tracking consultant bench status and utilization"""
    
    def __init__(self):
        self.activity_types = [
            "available", "on_project", "training", "internal_project", 
            "vacation", "sick_leave", "bench"
        ]
    
    async def update_consultant_status(
        self, 
        consultant_id: int, 
        new_status: str,
        activity_description: Optional[str] = None,
        is_billable: bool = False
    ) -> Dict[str, Any]:
        """Update consultant bench status and log activity"""
        try:
            if new_status not in self.activity_types:
                return {
                    "success": False, 
                    "error": f"Invalid status. Must be one of: {self.activity_types}"
                }
            
            db = SessionLocal()
            try:
                # Get consultant
                consultant = db.query(Consultant).filter(
                    Consultant.id == consultant_id
                ).first()
                
                if not consultant:
                    return {"success": False, "error": "Consultant not found"}
                
                # Update consultant status
                old_status = consultant.bench_status
                consultant.bench_status = new_status
                
                if new_status == "available" and old_status != "available":
                    consultant.bench_start_date = datetime.now()
                elif new_status != "available":
                    consultant.bench_start_date = None
                
                # Log activity
                activity = BenchActivity(
                    consultant_id=consultant_id,
                    activity_type=new_status,
                    activity_description=activity_description or f"Status changed to {new_status}",
                    start_time=datetime.now(),
                    is_billable=is_billable
                )
                
                # End previous activity if exists
                previous_activity = db.query(BenchActivity).filter(
                    BenchActivity.consultant_id == consultant_id,
                    BenchActivity.end_time.is_(None)
                ).first()
                
                if previous_activity:
                    previous_activity.end_time = datetime.now()
                    duration = (previous_activity.end_time - previous_activity.start_time).total_seconds() / 3600
                    previous_activity.duration_hours = int(duration)
                
                db.add(activity)
                db.commit()
                
                return {
                    "success": True,
                    "consultant_id": consultant_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "activity_id": activity.id,
                    "message": f"Status updated from {old_status} to {new_status}"
                }
                
            finally:
                db.close()
                
        except Exception as e:
            return {"success": False, "error": f"Status update failed: {str(e)}"}
    
    async def get_bench_utilization_report(
        self, 
        start_date: str, 
        end_date: str,
        consultant_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Generate bench utilization report for date range"""
        try:
            db = SessionLocal()
            try:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
                
                # Base query
                query = db.query(Consultant)
                if consultant_ids:
                    query = query.filter(Consultant.id.in_(consultant_ids))
                
                consultants = query.all()
                
                report_data = []
                total_consultants = len(consultants)
                total_bench_hours = 0
                total_billable_hours = 0
                
                for consultant in consultants:
                    # Get activities in date range
                    activities = db.query(BenchActivity).filter(
                        BenchActivity.consultant_id == consultant.id,
                        BenchActivity.start_time >= start_dt,
                        BenchActivity.start_time <= end_dt
                    ).all()
                    
                    # Calculate metrics
                    bench_hours = sum(
                        activity.duration_hours or 0 
                        for activity in activities 
                        if activity.activity_type in ["available", "bench"]
                    )
                    
                    billable_hours = sum(
                        activity.duration_hours or 0
                        for activity in activities
                        if activity.is_billable
                    )
                    
                    training_hours = sum(
                        activity.duration_hours or 0
                        for activity in activities
                        if activity.activity_type == "training"
                    )
                    
                    total_hours = sum(activity.duration_hours or 0 for activity in activities)
                    
                    utilization_rate = (billable_hours / total_hours * 100) if total_hours > 0 else 0
                    bench_rate = (bench_hours / total_hours * 100) if total_hours > 0 else 0
                    
                    consultant_data = {
                        "consultant_id": consultant.id,
                        "name": consultant.name,
                        "employee_id": consultant.employee_id,
                        "current_status": consultant.bench_status,
                        "total_hours": total_hours,
                        "billable_hours": billable_hours,
                        "bench_hours": bench_hours,
                        "training_hours": training_hours,
                        "utilization_rate": round(utilization_rate, 2),
                        "bench_rate": round(bench_rate, 2)
                    }
                    
                    report_data.append(consultant_data)
                    total_bench_hours += bench_hours
                    total_billable_hours += billable_hours
                
                # Calculate overall metrics
                overall_utilization = (total_billable_hours / (total_billable_hours + total_bench_hours) * 100) if (total_billable_hours + total_bench_hours) > 0 else 0
                
                return {
                    "success": True,
                    "report_period": f"{start_date} to {end_date}",
                    "total_consultants": total_consultants,
                    "overall_utilization_rate": round(overall_utilization, 2),
                    "total_bench_hours": total_bench_hours,
                    "total_billable_hours": total_billable_hours,
                    "consultant_details": report_data
                }
                
            finally:
                db.close()
                
        except Exception as e:
            return {"success": False, "error": f"Report generation failed: {str(e)}"}
    
    async def get_available_consultants(self, required_skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get list of available consultants, optionally filtered by skills"""
        try:
            db = SessionLocal()
            try:
                # Get available consultants
                consultants = db.query(Consultant).filter(
                    Consultant.bench_status == "available"
                ).all()
                
                available_consultants = []
                
                for consultant in consultants:
                    # Calculate bench duration
                    bench_duration = None
                    if consultant.bench_start_date:
                        bench_duration = (datetime.now() - consultant.bench_start_date).days
                    
                    consultant_data = {
                        "id": consultant.id,
                        "name": consultant.name,
                        "employee_id": consultant.employee_id,
                        "email": consultant.email,
                        "technical_skills": consultant.technical_skills or [],
                        "years_of_experience": consultant.years_of_experience,
                        "bench_duration_days": bench_duration,
                        "certifications": consultant.certifications or []
                    }
                    
                    # Filter by skills if provided
                    if required_skills:
                        consultant_skills = [skill.lower() for skill in (consultant.technical_skills or [])]
                        required_skills_lower = [skill.lower() for skill in required_skills]
                        
                        matching_skills = set(consultant_skills) & set(required_skills_lower)
                        if len(matching_skills) > 0:
                            consultant_data["skill_match_count"] = len(matching_skills)
                            consultant_data["matching_skills"] = list(matching_skills)
                            available_consultants.append(consultant_data)
                    else:
                        available_consultants.append(consultant_data)
                
                # Sort by bench duration (longest first) if no skill filtering
                if not required_skills:
                    available_consultants.sort(
                        key=lambda x: x["bench_duration_days"] or 0, 
                        reverse=True
                    )
                else:
                    # Sort by skill match count
                    available_consultants.sort(
                        key=lambda x: x.get("skill_match_count", 0), 
                        reverse=True
                    )
                
                return {
                    "success": True,
                    "total_available": len(available_consultants),
                    "consultants": available_consultants,
                    "filter_applied": "skills" if required_skills else "none"
                }
                
            finally:
                db.close()
                
        except Exception as e:
            return {"success": False, "error": f"Failed to get available consultants: {str(e)}"}
