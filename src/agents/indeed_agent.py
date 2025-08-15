import asyncio
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from .base_agent import BaseSearchAgent, JobData

class IndeedAgent(BaseSearchAgent):
    """Indeed.com job search agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("IndeedAgent", "indeed", config)
        self.base_url = "https://www.indeed.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def search_jobs(self, job_role: str, location: str = None, keywords: List[str] = None) -> List[JobData]:
        """Search Indeed for jobs"""
        jobs = []
        
        # Build search query
        query = job_role
        if keywords:
            query += " " + " ".join(keywords)
        
        search_url = f"{self.base_url}/jobs"
        params = {
            "q": query,
            "l": location or "Remote",
            "sort": "date"
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract job listings (this is a simplified example)
            job_cards = soup.find_all("div", class_="job_seen_beacon")
            
            for card in job_cards[:20]:  # Limit to first 20 results
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Failed to parse job card: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Indeed search failed: {e}")
            raise
        
        return jobs
    
    def _parse_job_card(self, card) -> JobData:
        """Parse individual job card from Indeed"""
        try:
            # Extract basic job information
            title_elem = card.find("h2", class_="jobTitle")
            company_elem = card.find("span", class_="companyName")
            location_elem = card.find("div", class_="companyLocation")
            
            job_title = title_elem.get_text(strip=True) if title_elem else "N/A"
            company_name = company_elem.get_text(strip=True) if company_elem else "N/A"
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            # Create job data object
            job = JobData(
                job_title=job_title,
                company_name=company_name,
                location=location,
                source="indeed",
                confidence_score=70  # Base confidence for Indeed
            )
            
            return job
            
        except Exception as e:
            self.logger.error(f"Failed to parse job card: {e}")
            return None
    
    async def extract_contact_info(self, job_data: JobData) -> JobData:
        """Extract contact information from Indeed job posting"""
        # Indeed typically doesn't show contact info in listings
        # This would require clicking into individual job postings
        # For now, we'll return the job data as-is
        
        # In a full implementation, you would:
        # 1. Navigate to the job posting URL
        # 2. Extract contact information from the full posting
        # 3. Use AI to identify contact details
        
        return job_data
