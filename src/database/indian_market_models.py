from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class IndianCompany(Base):
    __tablename__ = "indian_companies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    website = Column(String(500))
    company_type = Column(String(100))  # fintech, edtech, healthtech, etc.
    founded_year = Column(Integer)
    employee_count = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    funding_stage = Column(String(100))  # seed, series A, series B, etc.
    headquarters = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job_postings = relationship("IndianJobPosting", back_populates="company")

class IndianJobPosting(Base):
    __tablename__ = "indian_job_postings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("indian_companies.id"), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_description = Column(Text)
    requirements = Column(Text)
    location = Column(String(255))
    salary_range = Column(String(255))
    experience_level = Column(String(100))  # entry, mid, senior, lead
    job_type = Column(String(100))  # full-time, part-time, contract, internship
    remote_policy = Column(String(100))  # remote, hybrid, on-site
    posted_date = Column(DateTime)
    application_deadline = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Analysis Results
    ai_confidence_score = Column(Float)
    ai_contact_extraction = Column(JSON)
    ai_decision = Column(JSON)
    
    # Relationships
    company = relationship("IndianCompany", back_populates="job_postings")
    contact_information = relationship("JobContactInformation", back_populates="job_posting")

class JobContactInformation(Base):
    __tablename__ = "job_contact_information"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_posting_id = Column(String, ForeignKey("indian_job_postings.id"), nullable=False)
    contact_person = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    linkedin_url = Column(String(500))
    application_url = Column(String(500))
    hr_email = Column(String(255))
    hr_phone = Column(String(50))
    office_address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job_posting = relationship("IndianJobPosting", back_populates="contact_information")

class IndianMarketSearch(Base):
    __tablename__ = "indian_market_searches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    job_role = Column(String(255), nullable=False)
    location = Column(String(255))
    company_types = Column(JSON)  # List of company types to search
    keywords = Column(JSON)
    search_frequency = Column(String(50), default="hourly")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime)
    
    # Search Results
    total_jobs_found = Column(Integer, default=0)
    quality_jobs_found = Column(Integer, default=0)
    last_success_rate = Column(Float)

class AIModelPerformance(Base):
    __tablename__ = "ai_model_performance"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(100), nullable=False)  # llama2, falcon, mistral
    task_type = Column(String(100))  # contact_extraction, decision_making
    accuracy_score = Column(Float)
    response_time = Column(Float)  # in seconds
    tokens_used = Column(Integer)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def get_success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0.0

class IndianMarketTrend(Base):
    __tablename__ = "indian_market_trends"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trend_date = Column(DateTime, default=datetime.utcnow)
    trend_type = Column(String(100))  # job_demand, salary_trend, skill_demand
    trend_data = Column(JSON)
    confidence_score = Column(Float)
    source = Column(String(100))  # ai_analysis, market_data, user_feedback

class CompanyTypeSearch(Base):
    __tablename__ = "company_type_searches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_type = Column(String(100), nullable=False)
    search_date = Column(DateTime, default=datetime.utcnow)
    companies_found = Column(Integer)
    jobs_found = Column(Integer)
    average_salary = Column(Float)
    top_skills = Column(JSON)
    growth_rate = Column(Float)  # Month-over-month growth

class IndianLocationSearch(Base):
    __tablename__ = "indian_location_searches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    location = Column(String(255), nullable=False)
    search_date = Column(DateTime, default=datetime.utcnow)
    total_companies = Column(Integer)
    active_jobs = Column(Integer)
    average_salary = Column(Float)
    top_industries = Column(JSON)
    remote_jobs_percentage = Column(Float)

class SearchQualityMetrics(Base):
    __tablename__ = "search_quality_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    search_id = Column(String, ForeignKey("indian_market_searches.id"))
    total_jobs_scraped = Column(Integer)
    duplicate_jobs_removed = Column(Integer)
    quality_jobs_identified = Column(Integer)
    contact_info_extracted = Column(Integer)
    ai_decision_accuracy = Column(Float)
    search_execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
