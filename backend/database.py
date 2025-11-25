"""
Database models and utilities
SQLAlchemy with SQLite (Postgres-ready)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bluepath.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models

class Route(Base):
    """Route storage"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, unique=True, index=True)
    path = Column(Text)  # JSON string
    distance = Column(Float)
    eta = Column(String)
    fuel_estimate = Column(Float)
    scores = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class Telemetry(Base):
    """Telemetry data storage"""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, index=True)
    timestamp = Column(String)
    wave_height = Column(Float)
    wind_speed = Column(Float)
    current_speed = Column(Float)
    visibility = Column(Float)
    temperature = Column(Float)

class AuditLog(Base):
    """Blockchain-style audit log"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    data = Column(Text)  # JSON string
    timestamp = Column(String)
    hash = Column(String, unique=True)
    signature = Column(String)
    prev_hash = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
