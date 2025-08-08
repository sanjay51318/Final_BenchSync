from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from .consultant import Base
from datetime import datetime

class BenchActivity(Base):
    __tablename__ = "bench_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    consultant_id = Column(Integer, ForeignKey("consultants.id"))
    
    # Activity Details
    activity_type = Column(String)  # training, internal_project, available, on_project
    activity_description = Column(Text)
    
    # Time Tracking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_hours = Column(Integer, nullable=True)
    
    # Status
    is_billable = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    consultant = relationship("Consultant", back_populates="bench_activities")

class BenchUtilization(Base):
    __tablename__ = "bench_utilization"
    
    id = Column(Integer, primary_key=True, index=True) 
    consultant_id = Column(Integer, ForeignKey("consultants.id"))
    
    # Utilization Metrics
    month = Column(String)  # "2025-01"
    total_available_hours = Column(Integer)
    billable_hours = Column(Integer)  
    training_hours = Column(Integer)
    bench_hours = Column(Integer)
    
    # Calculated Metrics - Float imported correctly
    utilization_rate = Column(Float)  # billable / total_available
    bench_rate = Column(Float)        # bench / total_available
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    consultant = relationship("Consultant")
