import asyncio
from typing import List, Dict, Any
from datetime import datetime
import openai
from .base_agent import JobData

class AIContactExtractor(BaseSearchAgent):
    """AI-powered contact information extractor"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("AIContactExtractor", "ai_extractor", config)
        self.openai_client = openai.OpenAI(api_key=config.get("openai_api_key"))
        
    async def search_jobs(self, job_role: str, location: str = None, keywords: List[str] = None) -> List[JobData]:
        """This agent doesn't search for jobs, it enriches existing ones"""
        return []
    
    async def extract_contact_info(self, job_data: JobData) -> JobData:
        """Use AI to extract contact information from job descriptions"""
        
        if not job_data.job_description:
            return job_data
        
        try:
            # Create prompt for AI extraction
            prompt = f"""
            Extract contact information from this job posting:
            
            Job Title: {job_data.job_title}
            Company: {job_data.company_name}
            Description: {job_data.job_description[:1000]}  # Limit to first 1000 chars
            
            Please extract and return ONLY the following information in JSON format:
            {{
                "contact_person": "Name of contact person if mentioned",
                "contact_email": "Email address if mentioned",
                "contact_phone": "Phone number if mentioned",
                "linkedin_url": "LinkedIn profile URL if mentioned",
                "confidence_score": "Confidence level 0-100"
            }}
            
            If information is not found, use "Not found" as the value.
            """
            
            # Call OpenAI API
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            
            # Extract JSON from response (simplified parsing)
            try:
                import json
                contact_info = json.loads(ai_response)
                
                # Update job data with extracted information
                job_data.contact_person = contact_info.get("contact_person", "Not found")
                job_data.contact_email = contact_info.get("contact_email", "Not found")
                job_data.contact_phone = contact_info.get("contact_phone", "Not found")
                job_data.linkedin_url = contact_info.get("linkedin_url", "Not found")
                
                # Update confidence score
                ai_confidence = contact_info.get("confidence_score", 0)
                job_data.confidence_score = min(100, job_data.confidence_score + ai_confidence)
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse AI response as JSON")
                
        except Exception as e:
            self.logger.error(f"AI contact extraction failed: {e}")
        
        return job_data
    
    async def enrich_job_data(self, jobs: List[JobData]) -> List[JobData]:
        """Enrich multiple jobs with AI-extracted contact information"""
        enriched_jobs = []
        
        for job in jobs:
            enriched_job = await self.extract_contact_info(job)
            enriched_jobs.append(enriched_job)
            
            # Rate limiting to avoid API abuse
            await asyncio.sleep(1)
        
        return enriched_jobs
