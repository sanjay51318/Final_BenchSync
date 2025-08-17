#!/usr/bin/env python3
"""
Attendance Chatbot for Professional Bench Tracking System
AI-powered chatbot to query attendance data from PostgreSQL
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import re
from typing import Dict, List, Any

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class AttendanceChatbot:
    """AI Chatbot for attendance queries"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    def process_question(self, question: str, user_email: str = None) -> Dict[str, Any]:
        """Process natural language questions about attendance"""
        question_lower = question.lower().strip()
        
        # Check for specific person's attendance first
        person_attendance = self._extract_person_attendance_query(question_lower)
        if person_attendance:
            return person_attendance
        
        # Define response patterns
        if any(word in question_lower for word in ['my attendance', 'my rate', 'how am i', 'my record']):
            return self._get_personal_attendance(user_email)
            
        elif any(word in question_lower for word in ['today', 'present today', 'who is here']):
            return self._get_today_attendance()
            
        elif any(word in question_lower for word in ['this week', 'weekly', 'week attendance']):
            return self._get_weekly_attendance(user_email)
            
        elif any(word in question_lower for word in ['this month', 'monthly', 'month attendance']):
            return self._get_monthly_attendance(user_email)
            
        elif any(word in question_lower for word in ['best attendance', 'highest', 'top performer']):
            return self._get_best_attendance()
            
        elif any(word in question_lower for word in ['worst attendance', 'lowest', 'poor attendance']):
            return self._get_worst_attendance()
            
        elif any(word in question_lower for word in ['team average', 'overall', 'company average']):
            return self._get_team_average()
            
        elif any(word in question_lower for word in ['absent today', 'who is absent', 'missing today']):
            return self._get_absent_today()
            
        elif any(word in question_lower for word in ['late arrivals', 'who came late', 'late today']):
            return self._get_late_arrivals()
            
        elif 'days present' in question_lower or 'how many days' in question_lower:
            return self._get_days_present(user_email)
            
        else:
            return self._get_help_message()
    
    def _extract_person_attendance_query(self, question_lower: str):
        """Extract person's name from attendance query and return their attendance"""
        try:
            from database.models.professional_models import User
            
            # Patterns to match person-specific queries
            patterns = [
                r"what is (\w+(?:\s+\w+)*)'s attendance",
                r"(\w+(?:\s+\w+)*)'s attendance",
                r"attendance of (\w+(?:\s+\w+)*)",
                r"show (\w+(?:\s+\w+)*) attendance", 
                r"what is (\w+(?:\s+\w+)*) attendance percentage",
                r"(\w+(?:\s+\w+)*) attendance percentage",
                r"how is (\w+(?:\s+\w+)*)'s attendance",
                r"get (\w+(?:\s+\w+)*) attendance",
                r"what is (\w+(?:\s+\w+)*) attendance like",
                r"(\w+(?:\s+\w+)*) attendance like"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, question_lower)
                if match:
                    person_name = match.group(1).strip()
                    
                    # Skip if it's a generic word
                    if person_name in ['my', 'team', 'overall', 'company', 'today', 'this']:
                        continue
                    
                    # Find user by name (case insensitive)
                    session = self.db.get_session()
                    try:
                        user = session.query(User).filter(
                            User.name.ilike(f"%{person_name}%")
                        ).first()
                        
                        if user:
                            # Get their attendance using the existing method
                            result = self._get_personal_attendance(user.email)
                            # Customize the message for the specific person
                            if result.get('type') == 'personal_stats':
                                result['message'] = f"Attendance summary for {user.name}:"
                            return result
                        else:
                            return {
                                "type": "error",
                                "message": f"Could not find consultant '{person_name}'. Please check the name and try again.",
                                "data": {"person_searched": person_name}
                            }
                    finally:
                        session.close()
            
            return None  # No person-specific query found
            
        except Exception as e:
            return {
                "type": "error", 
                "message": f"Error processing person-specific query: {str(e)}"
            }
    
    def _get_personal_attendance(self, user_email: str) -> Dict[str, Any]:
        """Get personal attendance statistics"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                # Get user
                user = session.query(User).filter(User.email == user_email).first()
                if not user:
                    return {"error": "User not found"}
                
                # Use same 30-day calculation as dashboard for consistency
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                # Get attendance records in last 30 days (same as dashboard)
                records = session.query(AttendanceRecord).filter(
                    AttendanceRecord.user_id == user.id,
                    AttendanceRecord.date >= start_date.strftime('%Y-%m-%d'),
                    AttendanceRecord.date <= end_date.strftime('%Y-%m-%d')
                ).all()
                
                # Calculate statistics
                total_days = len(records)
                present_days = len([r for r in records if r.status in ['present', 'half_day']])
                absent_days = len([r for r in records if r.status == 'absent'])
                leave_days = len([r for r in records if r.status == 'leave'])
                
                attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
                
                # Get recent check-ins
                recent_records = session.query(AttendanceRecord).filter(
                    AttendanceRecord.user_id == user.id
                ).order_by(AttendanceRecord.date.desc()).limit(5).all()
                
                return {
                    "type": "personal_stats",
                    "message": f"Hi {user.name}! Here's your attendance summary for the last 30 days:",
                    "data": {
                        "user_name": user.name,
                        "attendance_rate": round(attendance_rate, 1),
                        "total_days": total_days,
                        "present_days": present_days,
                        "absent_days": absent_days,
                        "leave_days": leave_days,
                        "recent_records": [
                            {
                                "date": r.date,
                                "status": r.status,
                                "check_in": r.check_in_time,
                                "check_out": r.check_out_time
                            } for r in recent_records
                        ]
                    }
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving attendance data: {str(e)}"}
    
    def _get_today_attendance(self) -> Dict[str, Any]:
        """Get today's attendance summary"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Get today's records
                today_records = session.query(AttendanceRecord, User).join(
                    User, AttendanceRecord.user_id == User.id
                ).filter(AttendanceRecord.date == today).all()
                
                present_users = []
                absent_users = []
                late_users = []
                
                for record, user in today_records:
                    user_data = {
                        "name": user.name,
                        "email": user.email,
                        "check_in": record.check_in_time,
                        "status": record.status
                    }
                    
                    if record.status == 'present':
                        present_users.append(user_data)
                        # Check if late (after 9:30 AM)
                        if record.check_in_time and record.check_in_time > "09:30":
                            late_users.append(user_data)
                    elif record.status == 'absent':
                        absent_users.append(user_data)
                
                total_consultants = session.query(User).filter(User.role == 'consultant').count()
                present_count = len(present_users)
                attendance_rate = (present_count / total_consultants * 100) if total_consultants > 0 else 0
                
                return {
                    "type": "today_summary",
                    "message": f"Today's Attendance Summary ({today}):",
                    "data": {
                        "date": today,
                        "total_consultants": total_consultants,
                        "present_count": present_count,
                        "absent_count": len(absent_users),
                        "attendance_rate": round(attendance_rate, 1),
                        "present_users": present_users,
                        "absent_users": absent_users,
                        "late_users": late_users
                    }
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving today's attendance: {str(e)}"}
    
    def _get_team_average(self) -> Dict[str, Any]:
        """Get team average attendance"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                # Get current month data
                current_month = datetime.now().strftime('%Y-%m')
                
                # Get all consultant users
                consultants = session.query(User).filter(User.role == 'consultant').all()
                
                team_stats = []
                total_rate = 0
                
                for consultant in consultants:
                    records = session.query(AttendanceRecord).filter(
                        AttendanceRecord.user_id == consultant.id,
                        AttendanceRecord.date.like(f"{current_month}%")
                    ).all()
                    
                    total_days = len(records)
                    present_days = len([r for r in records if r.status in ['present', 'half_day']])
                    
                    rate = (present_days / total_days * 100) if total_days > 0 else 0
                    total_rate += rate
                    
                    team_stats.append({
                        "name": consultant.name,
                        "email": consultant.email,
                        "attendance_rate": round(rate, 1),
                        "present_days": present_days,
                        "total_days": total_days
                    })
                
                avg_rate = total_rate / len(consultants) if consultants else 0
                
                # Sort by attendance rate
                team_stats.sort(key=lambda x: x['attendance_rate'], reverse=True)
                
                return {
                    "type": "team_average",
                    "message": f"Team Attendance Summary for {datetime.now().strftime('%B %Y')}:",
                    "data": {
                        "average_rate": round(avg_rate, 1),
                        "total_consultants": len(consultants),
                        "team_stats": team_stats
                    }
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving team average: {str(e)}"}
    
    def _get_best_attendance(self) -> Dict[str, Any]:
        """Get consultant with best attendance"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                current_month = datetime.now().strftime('%Y-%m')
                consultants = session.query(User).filter(User.role == 'consultant').all()
                
                best_rate = 0
                best_consultant = None
                
                for consultant in consultants:
                    records = session.query(AttendanceRecord).filter(
                        AttendanceRecord.user_id == consultant.id,
                        AttendanceRecord.date.like(f"{current_month}%")
                    ).all()
                    
                    total_days = len(records)
                    present_days = len([r for r in records if r.status in ['present', 'half_day']])
                    
                    rate = (present_days / total_days * 100) if total_days > 0 else 0
                    
                    if rate > best_rate:
                        best_rate = rate
                        best_consultant = {
                            "name": consultant.name,
                            "email": consultant.email,
                            "rate": round(rate, 1),
                            "present_days": present_days,
                            "total_days": total_days
                        }
                
                return {
                    "type": "best_performer",
                    "message": "🏆 Best Attendance Performer:",
                    "data": best_consultant if best_consultant else {"message": "No data available"}
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving best attendance: {str(e)}"}
    
    def _get_help_message(self) -> Dict[str, Any]:
        """Get help message with available commands"""
        return {
            "type": "help",
            "message": "I can help you with attendance queries! Try asking:",
            "data": {
                "suggestions": [
                    "What's my attendance rate?",
                    "What is John Doe's attendance?",
                    "Show Kisshore's attendance percentage",
                    "Who is present today?",
                    "Show me this week's attendance",
                    "What's the team average?",
                    "Who has the best attendance?",
                    "Show me absent employees today",
                    "How many days have I been present?",
                    "Who came late today?"
                ]
            }
        }
    
    def _get_weekly_attendance(self, user_email: str) -> Dict[str, Any]:
        """Get weekly attendance for user"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                user = session.query(User).filter(User.email == user_email).first()
                if not user:
                    return {"error": "User not found"}
                
                # Get this week's dates
                today = datetime.now()
                start_of_week = today - timedelta(days=today.weekday())
                
                weekly_records = []
                for i in range(7):
                    date = (start_of_week + timedelta(days=i)).strftime('%Y-%m-%d')
                    record = session.query(AttendanceRecord).filter(
                        AttendanceRecord.user_id == user.id,
                        AttendanceRecord.date == date
                    ).first()
                    
                    weekly_records.append({
                        "date": date,
                        "day": (start_of_week + timedelta(days=i)).strftime('%A'),
                        "status": record.status if record else 'No record',
                        "check_in": record.check_in_time if record else None,
                        "check_out": record.check_out_time if record else None
                    })
                
                present_days = len([r for r in weekly_records if r['status'] in ['present', 'half_day']])
                
                return {
                    "type": "weekly_attendance",
                    "message": f"Weekly Attendance for {user.name}:",
                    "data": {
                        "user_name": user.name,
                        "week_records": weekly_records,
                        "present_days": present_days,
                        "total_days": 7
                    }
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving weekly attendance: {str(e)}"}
    
    def _get_monthly_attendance(self, user_email: str) -> Dict[str, Any]:
        """Get monthly attendance for user"""
        return self._get_personal_attendance(user_email)
    
    def _get_absent_today(self) -> Dict[str, Any]:
        """Get list of absent employees today"""
        today_data = self._get_today_attendance()
        if "data" in today_data:
            return {
                "type": "absent_today",
                "message": f"Employees absent today ({today_data['data']['date']}):",
                "data": {
                    "absent_users": today_data['data']['absent_users'],
                    "absent_count": today_data['data']['absent_count']
                }
            }
        return {"error": "Could not retrieve absence data"}
    
    def _get_late_arrivals(self) -> Dict[str, Any]:
        """Get list of late arrivals today"""
        today_data = self._get_today_attendance()
        if "data" in today_data:
            return {
                "type": "late_arrivals",
                "message": f"Late arrivals today ({today_data['data']['date']}):",
                "data": {
                    "late_users": today_data['data']['late_users'],
                    "late_count": len(today_data['data']['late_users'])
                }
            }
        return {"error": "Could not retrieve late arrival data"}
    
    def _get_days_present(self, user_email: str) -> Dict[str, Any]:
        """Get number of days present for user"""
        personal_data = self._get_personal_attendance(user_email)
        if "data" in personal_data:
            return {
                "type": "days_present",
                "message": f"Days present for {personal_data['data']['user_name']}:",
                "data": {
                    "present_days": personal_data['data']['present_days'],
                    "total_days": personal_data['data']['total_days'],
                    "attendance_rate": personal_data['data']['attendance_rate']
                }
            }
        return {"error": "Could not retrieve attendance days"}
    
    def _get_worst_attendance(self) -> Dict[str, Any]:
        """Get consultant with worst attendance"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                current_month = datetime.now().strftime('%Y-%m')
                consultants = session.query(User).filter(User.role == 'consultant').all()
                
                worst_rate = 100
                worst_consultant = None
                
                for consultant in consultants:
                    records = session.query(AttendanceRecord).filter(
                        AttendanceRecord.user_id == consultant.id,
                        AttendanceRecord.date.like(f"{current_month}%")
                    ).all()
                    
                    total_days = len(records)
                    present_days = len([r for r in records if r.status in ['present', 'half_day']])
                    
                    rate = (present_days / total_days * 100) if total_days > 0 else 0
                    
                    if rate < worst_rate and total_days > 0:
                        worst_rate = rate
                        worst_consultant = {
                            "name": consultant.name,
                            "email": consultant.email,
                            "rate": round(rate, 1),
                            "present_days": present_days,
                            "total_days": total_days
                        }
                
                return {
                    "type": "worst_performer",
                    "message": "⚠️ Needs Attention - Lowest Attendance:",
                    "data": worst_consultant if worst_consultant else {"message": "No data available"}
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving worst attendance: {str(e)}"}
    
    def get_user_attendance_stats(self, user_email: str, days: int = 30) -> Dict[str, Any]:
        """Get user attendance statistics for specified number of days"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                # Get user
                user = session.query(User).filter(User.email == user_email).first()
                if not user:
                    return {"error": "User not found"}
                
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Get attendance records in date range
                records = session.query(AttendanceRecord).filter(
                    AttendanceRecord.user_id == user.id,
                    AttendanceRecord.date >= start_date.strftime('%Y-%m-%d'),
                    AttendanceRecord.date <= end_date.strftime('%Y-%m-%d')
                ).all()
                
                # Calculate statistics
                total_days = len(records)
                present_days = len([r for r in records if r.status in ['present', 'half_day']])
                absent_days = len([r for r in records if r.status == 'absent'])
                leave_days = len([r for r in records if r.status == 'leave'])
                
                attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
                
                return {
                    "user_name": user.name,
                    "user_email": user.email,
                    "attendance_rate": round(attendance_rate, 2),
                    "total_days": total_days,
                    "present_days": present_days,
                    "absent_days": absent_days,
                    "leave_days": leave_days,
                    "period_days": days
                }
                
            finally:
                session.close()
                
        except Exception as e:
            return {"error": f"Error retrieving user attendance stats: {str(e)}"}
    
    def get_all_consultants_attendance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get attendance statistics for all consultants"""
        try:
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Get all consultants
                consultants = session.query(User).filter(User.role == 'consultant').all()
                
                consultant_stats = []
                
                for consultant in consultants:
                    # Get attendance records for this consultant
                    records = session.query(AttendanceRecord).filter(
                        AttendanceRecord.user_id == consultant.id,
                        AttendanceRecord.date >= start_date.strftime('%Y-%m-%d'),
                        AttendanceRecord.date <= end_date.strftime('%Y-%m-%d')
                    ).all()
                    
                    # Calculate statistics
                    total_days = len(records)
                    present_days = len([r for r in records if r.status in ['present', 'half_day']])
                    absent_days = len([r for r in records if r.status == 'absent'])
                    leave_days = len([r for r in records if r.status == 'leave'])
                    
                    attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
                    
                    consultant_stats.append({
                        "user_name": consultant.name,
                        "user_email": consultant.email,
                        "attendance_rate": round(attendance_rate, 2),
                        "total_days": total_days,
                        "present_days": present_days,
                        "absent_days": absent_days,
                        "leave_days": leave_days
                    })
                
                return consultant_stats
                
            finally:
                session.close()
                
        except Exception as e:
            return [{"error": f"Error retrieving team attendance stats: {str(e)}"}]
    
    def add_sample_attendance_data(self, user_email: str, days: int = 30) -> bool:
        """Add sample attendance data for testing"""
        try:
            import random
            from database.models.professional_models import User, AttendanceRecord
            
            session = self.db.get_session()
            try:
                # Get user
                user = session.query(User).filter(User.email == user_email).first()
                if not user:
                    return False
                
                # Generate sample data for the specified number of days
                for i in range(days):
                    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    
                    # Check if record already exists
                    existing = session.query(AttendanceRecord).filter(
                        AttendanceRecord.user_id == user.id,
                        AttendanceRecord.date == date
                    ).first()
                    
                    if not existing:
                        # Generate random attendance data
                        status_choices = ['present', 'present', 'present', 'present', 'absent', 'leave']
                        status = random.choice(status_choices)
                        
                        if status == 'present':
                            check_in_choices = ['08:30', '09:00', '09:15', '09:30', '09:45', '10:00']
                            check_in_time = random.choice(check_in_choices)
                            check_out_time = '18:00'
                            hours_worked = 8.5
                        else:
                            check_in_time = None
                            check_out_time = None
                            hours_worked = 0
                        
                        record = AttendanceRecord(
                            user_id=user.id,
                            date=date,
                            status=status,
                            check_in_time=check_in_time,
                            check_out_time=check_out_time,
                            hours_worked=hours_worked
                        )
                        
                        session.add(record)
                
                session.commit()
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            print(f"Error adding sample attendance data: {str(e)}")
            return False
