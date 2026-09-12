from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True) # e.g. INC-00021
    title = Column(String, index=True)
    severity = Column(String) # CRITICAL, HIGH, MEDIUM, LOW
    confidence = Column(Float)
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="OPEN") # OPEN, RESOLVED
    mitre_techniques = Column(JSON, default=list) # List of dicts or strings
    explanation = Column(String)
    
    # Aggregated fields for display
    source_ip = Column(String, nullable=True)
    target_ip = Column(String, nullable=True)
    
    alerts = relationship("Alert", back_populates="incident")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    source_ip = Column(String, index=True, nullable=True)
    destination_ip = Column(String, index=True, nullable=True)
    username = Column(String, index=True, nullable=True)
    event_type = Column(String, index=True)
    severity = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    description = Column(String, nullable=True)
    attack_stage = Column(String, nullable=True)
    
    # Raw data can be stored if needed
    raw_data = Column(JSON, nullable=True)
    
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    incident = relationship("Incident", back_populates="alerts")
