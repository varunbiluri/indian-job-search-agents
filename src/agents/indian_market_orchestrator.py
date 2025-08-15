import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging
from .base_agent import BaseSearchAgent, JobData
from .indian_companies_agent import IndianCompaniesAgent
from .indeed_agent import IndeedAgent
from .linkedin_agent import LinkedInAgent
from .multi_ai_models import MultiAIModelsAgent

class IndianMarketOrchestrator:
    """Orchestrates job search across Indian market using multiple agents and AI models"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize specialized agents for Indian market
        self.agents: List[BaseSearchAgent] = []
        self.ai_models: MultiAIModelsAgent = None
        self._initialize_agents()
        
        # Results storage
        self.search_results: Dict[str, Any] = {}
        self.decision_logs: List[Dict[str, Any]] = []
        
    def _initialize_agents(self):
        """Initialize all available search agents for Indian market"""
        try:
            # Indian market specific agents
            self.agents.append(IndianCompaniesAgent(self.config.get("indian_companies", {})))
            
            # Global job platforms (filtered for India)
            self.agents.append(IndeedAgent(self.config.get("indeed", {})))
            self.agents.append(LinkedInAgent(self.config.get("linkedin", {})))
            
            # AI models for decision making
            self.ai_models = MultiAIModelsAgent(self.config.get("ai_models", {}))
            
            self.logger.info(f"Initialized {len(self.agents)} agents for Indian market")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
    
    async def search_indian_market(self, job_role: str, location: str = "India", keywords: List[str] = None, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for jobs across the entire Indian market"""
        
        start_time = datetime.utcnow()
        all_jobs = []
        agent_results = {}
        
        # Add India-specific keywords if not provided
        if not keywords:
            keywords = []
        
        # Add Indian market keywords
        india_keywords = ["India", "Indian", "Remote India", "Hybrid India"]
        keywords.extend(india_keywords)
        
        # Run search agents in parallel
        search_tasks = []
        for agent in self.agents:
            if hasattr(agent, 'search_jobs'):
                task = agent.run_search(job_role, location, keywords)
                search_tasks.append(task)
        
        # Wait for all searches to complete
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Agent {self.agents[i].name} failed: {result}")
                    agent_results[self.agents[i].name] = {
                        "status": "failed",
                        "error": str(result)
                    }
                else:
                    agent_results[self.agents[i].name] = result
                    if result.get("status") == "success":
                        all_jobs.extend(result.get("jobs", []))
        
        # Use AI models to enrich job data and make decisions
        if self.ai_models and all_jobs:
            try:
                enriched_jobs = await self._enrich_with_ai(all_jobs, user_preferences)
                all_jobs = enriched_jobs
            except Exception as e:
                self.logger.error(f"AI enrichment failed: {e}")
        
        # Remove duplicates and filter for quality
        unique_jobs = self._remove_duplicates(all_jobs)
        quality_jobs = self._filter_quality_jobs(unique_jobs)
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Compile final results
        final_results = {
            "status": "completed",
            "job_role": job_role,
            "location": location,
            "keywords": keywords,
            "total_jobs_found": len(all_jobs),
            "unique_jobs": len(unique_jobs),
            "quality_jobs": len(quality_jobs),
            "execution_time": execution_time,
            "agents_used": [agent.name for agent in self.agents],
            "agent_results": agent_results,
            "ai_models_used": ["llama2", "falcon", "mistral"] if self.ai_models else [],
            "jobs": quality_jobs,
            "timestamp": datetime.utcnow(),
            "market": "Indian"
        }
        
        self.search_results[job_role] = final_results
        return final_results
    
    async def _enrich_with_ai(self, jobs: List[JobData], user_preferences: Dict[str, Any] = None) -> List[JobData]:
        """Enrich jobs using AI models and make decisions"""
        enriched_jobs = []
        
        for job in jobs:
            try:
                # Extract contact information using AI
                enriched_job = await self.ai_models.extract_contact_info(job)
                
                # Make decision about adding to database
                if user_preferences:
                    decision = await self.ai_models.make_decision(enriched_job, user_preferences)
                    
                    # Log decision
                    self.decision_logs.append({
                        "job_id": getattr(job, 'id', 'unknown'),
                        "decision": decision,
                        "timestamp": datetime.utcnow()
                    })
                    
                    # Only add jobs that AI recommends
                    if decision.get("decision") == "add":
                        enriched_jobs.append(enriched_job)
                else:
                    # If no user preferences, add all jobs
                    enriched_jobs.append(enriched_job)
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"AI enrichment failed for job {job.job_title}: {e}")
                # Add job without AI enrichment
                enriched_jobs.append(job)
        
        return enriched_jobs
    
    def _remove_duplicates(self, jobs: List[JobData]) -> List[JobData]:
        """Remove duplicate jobs based on multiple criteria"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create multiple identifiers for better duplicate detection
            identifiers = [
                f"{job.job_title.lower()}_{job.company_name.lower()}",
                f"{job.job_title.lower()}_{job.location.lower()}",
                f"{job.company_name.lower()}_{job.location.lower()}"
            ]
            
            is_duplicate = False
            for identifier in identifiers:
                if identifier in seen:
                    job.is_duplicate = True
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                for identifier in identifiers:
                    seen.add(identifier)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _filter_quality_jobs(self, jobs: List[JobData]) -> List[JobData]:
        """Filter jobs based on quality criteria"""
        quality_jobs = []
        
        for job in jobs:
            quality_score = self._calculate_quality_score(job)
            
            # Only include jobs with quality score above threshold
            if quality_score >= self.config.get("quality_threshold", 60):
                job.quality_score = quality_score
                quality_jobs.append(job)
        
        # Sort by quality score
        quality_jobs.sort(key=lambda x: getattr(x, 'quality_score', 0), reverse=True)
        
        return quality_jobs
    
    def _calculate_quality_score(self, job: JobData) -> int:
        """Calculate quality score for a job posting"""
        score = 0
        
        # Job title quality
        if job.job_title and len(job.job_title) > 5:
            score += 20
        
        # Company information
        if job.company_name and len(job.company_name) > 2:
            score += 15
        
        # Location information
        if job.location and len(job.location) > 2:
            score += 15
        
        # Contact information (bonus points)
        if job.contact_email and job.contact_email != "Not found":
            score += 20
        
        if job.contact_person and job.contact_person != "Not found":
            score += 15
        
        if job.linkedin_url and job.linkedin_url != "Not found":
            score += 15
        
        # Description quality
        if job.job_description and len(job.job_description) > 100:
            score += 10
        
        return min(100, score)
    
    async def get_indian_market_stats(self) -> Dict[str, Any]:
        """Get statistics specific to Indian market"""
        stats = {
            "total_companies": len(self.agents[0].indian_companies) if self.agents else 0,
            "companies_by_type": {},
            "agent_performance": {},
            "ai_model_accuracy": {},
            "market_coverage": "pan_india"
        }
        
        # Company type distribution
        if self.agents and hasattr(self.agents[0], 'indian_companies'):
            for company in self.agents[0].indian_companies:
                company_type = company.get("type", "unknown")
                stats["companies_by_type"][company_type] = stats["companies_by_type"].get(company_type, 0) + 1
        
        # Agent performance
        for agent in self.agents:
            stats["agent_performance"][agent.name] = {
                "success_rate": agent.get_success_rate(),
                "last_run": agent.last_run
            }
        
        return stats
    
    async def search_by_company_type(self, job_role: str, company_type: str, location: str = "India") -> Dict[str, Any]:
        """Search jobs in specific company types (e.g., fintech, edtech)"""
        if not self.agents or not hasattr(self.agents[0], 'indian_companies'):
            return {"error": "Indian companies agent not available"}
        
        # Filter companies by type
        filtered_companies = [
            company for company in self.agents[0].indian_companies
            if company.get("type") == company_type
        ]
        
        if not filtered_companies:
            return {"error": f"No companies found for type: {company_type}"}
        
        # Create temporary agent with filtered companies
        temp_agent = IndianCompaniesAgent()
        temp_agent.indian_companies = filtered_companies
        
        # Run search
        result = await temp_agent.run_search(job_role, location)
        
        return {
            "company_type": company_type,
            "companies_searched": len(filtered_companies),
            "search_results": result
        }
    
    async def search_by_location(self, job_role: str, specific_location: str) -> Dict[str, Any]:
        """Search jobs in specific Indian cities/regions"""
        # Add location-specific keywords
        location_keywords = [specific_location, f"{specific_location} India"]
        
        return await self.search_indian_market(
            job_role=job_role,
            location=specific_location,
            keywords=location_keywords
        )
