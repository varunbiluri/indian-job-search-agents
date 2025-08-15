from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String(50), default="free")  # free, pro, enterprise
    
    # Relationships
    job_searches = relationship("JobSearch", back_populates="user")
    saved_jobs = relationship("SavedJob", back_populates="user")

class JobSearch(Base):
    __tablename__ = "job_searches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_role = Column(String(255), nullable=False)
    location = Column(String(255))
    keywords = Column(JSON)  # List of keywords
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    search_frequency = Column(String(50), default="hourly")  # hourly, daily, weekly
    
    # Relationships
    user = relationship("User", back_populates="job_searches")
    search_results = relationship("JobSearchResult", back_populates="job_search")

class JobSearchResult(Base):
    __tablename__ = "job_search_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_search_id = Column(String, ForeignKey("job_searches.id"), nullable=False)
    source = Column(String(100), nullable=False)  # indeed, linkedin, glassdoor, etc.
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255))
    location = Column(String(255))
    salary_range = Column(String(255))
    job_description = Column(Text)
    requirements = Column(Text)
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    linkedin_url = Column(String(500))
    application_url = Column(String(500))
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_duplicate = Column(Boolean, default=False)
    confidence_score = Column(Integer)  # AI confidence in data quality
    
    # Relationships
    job_search = relationship("JobSearch", back_populates="search_results")

class SavedJob(Base):
    __tablename__ = "saved_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_result_id = Column(String, ForeignKey("job_search_results.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="saved_jobs")
    job_result = relationship("JobSearchResult")

class SearchAgent(Base):
    __tablename__ = "search_agents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)  # indeed, linkedin, glassdoor
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    success_rate = Column(Integer)  # Percentage of successful searches
    config = Column(JSON)  # Agent-specific configuration
    
class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("search_agents.id"))
    job_search_id = Column(String, ForeignKey("job_searches.id"))
    status = Column(String(50))  # success, failed, partial
    results_count = Column(Integer)
    error_message = Column(Text)
    execution_time = Column(Integer)  # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
