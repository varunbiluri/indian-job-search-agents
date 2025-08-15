from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import asyncio
import logging
from dataclasses import dataclass

@dataclass
class JobData:
    job_title: str
    company_name: str
    location: str
    salary_range: str = None
    job_description: str = None
    requirements: str = None
    contact_person: str = None
    contact_email: str = None
    contact_phone: str = None
    linkedin_url: str = None
    application_url: str = None
    posted_date: datetime = None
    source: str = None
    confidence_score: int = 0

class BaseSearchAgent(ABC):
    """Base class for all job search agents"""
    
    def __init__(self, name: str, source: str, config: Dict[str, Any] = None):
        self.name = name
        self.source = source
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.last_run = None
        self.success_count = 0
        self.failure_count = 0
        
    @abstractmethod
    async def search_jobs(self, job_role: str, location: str = None, keywords: List[str] = None) -> List[JobData]:
        """Search for jobs using the agent's specific method"""
        pass
    
    @abstractmethod
    async def extract_contact_info(self, job_data: JobData) -> JobData:
        """Extract contact information from job posting"""
        pass
    
    async def run_search(self, job_role: str, location: str = None, keywords: List[str] = None) -> Dict[str, Any]:
        """Run a complete job search and return results with metadata"""
        start_time = datetime.utcnow()
        
        try:
            # Search for jobs
            jobs = await self.search_jobs(job_role, location, keywords)
            
            # Extract contact information for each job
            enriched_jobs = []
            for job in jobs:
                enriched_job = await self.extract_contact_info(job)
                enriched_jobs.append(enriched_job)
            
            # Update statistics
            self.success_count += 1
            self.last_run = datetime.utcnow()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                "status": "success",
                "agent": self.name,
                "source": self.source,
                "jobs_found": len(enriched_jobs),
                "execution_time": execution_time,
                "jobs": enriched_jobs,
                "timestamp": self.last_run
            }
            
        except Exception as e:
            self.failure_count += 1
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            
            return {
                "status": "failed",
                "agent": self.name,
                "source": self.source,
                "error": str(e),
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "timestamp": datetime.utcnow()
            }
    
    def get_success_rate(self) -> float:
        """Calculate success rate of the agent"""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0.0
