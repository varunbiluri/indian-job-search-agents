import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging
from .base_agent import BaseSearchAgent, JobData
from .indeed_agent import IndeedAgent
from .linkedin_agent import LinkedInAgent
from .ai_contact_extractor import AIContactExtractor

class MultiAgentOrchestrator:
    """Orchestrates multiple job search agents"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize agents
        self.agents: List[BaseSearchAgent] = []
        self._initialize_agents()
        
        # Results storage
        self.search_results: Dict[str, Any] = {}
        
    def _initialize_agents(self):
        """Initialize all available search agents"""
        try:
            # Web scraping agents
            self.agents.append(IndeedAgent(self.config.get("indeed", {})))
            self.agents.append(LinkedInAgent(self.config.get("linkedin", {})))
            
            # AI enhancement agent
            self.agents.append(AIContactExtractor(self.config.get("openai", {})))
            
            self.logger.info(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
    
    async def search_all_sources(self, job_role: str, location: str = None, keywords: List[str] = None) -> Dict[str, Any]:
        """Search all sources using multiple agents"""
        
        start_time = datetime.utcnow()
        all_jobs = []
        agent_results = {}
        
        # Run search agents in parallel
        search_tasks = []
        for agent in self.agents:
            if hasattr(agent, 'search_jobs') and agent.source != "ai_extractor":
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
        
        # Use AI agent to enrich job data with contact information
        ai_agent = next((agent for agent in self.agents if agent.source == "ai_extractor"), None)
        if ai_agent and all_jobs:
            try:
                enriched_jobs = await ai_agent.enrich_job_data(all_jobs)
                all_jobs = enriched_jobs
            except Exception as e:
                self.logger.error(f"AI enrichment failed: {e}")
        
        # Remove duplicates based on job title and company
        unique_jobs = self._remove_duplicates(all_jobs)
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Compile final results
        final_results = {
            "status": "completed",
            "job_role": job_role,
            "location": location,
            "keywords": keywords,
            "total_jobs_found": len(unique_jobs),
            "execution_time": execution_time,
            "agents_used": [agent.name for agent in self.agents],
            "agent_results": agent_results,
            "jobs": unique_jobs,
            "timestamp": datetime.utcnow()
        }
        
        self.search_results[job_role] = final_results
        return final_results
    
    def _remove_duplicates(self, jobs: List[JobData]) -> List[JobData]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a unique identifier
            identifier = f"{job.job_title.lower()}_{job.company_name.lower()}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)
            else:
                # Mark as duplicate
                job.is_duplicate = True
        
        return unique_jobs
    
    def get_agent_statistics(self) -> Dict[str, Any]:
        """Get statistics for all agents"""
        stats = {}
        
        for agent in self.agents:
            stats[agent.name] = {
                "source": agent.source,
                "success_count": agent.success_count,
                "failure_count": agent.failure_count,
                "success_rate": agent.get_success_rate(),
                "last_run": agent.last_run
            }
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents"""
        health_status = {}
        
        for agent in self.agents:
            try:
                # Simple health check - try to access agent properties
                health_status[agent.name] = {
                    "status": "healthy",
                    "source": agent.source,
                    "last_run": agent.last_run
                }
            except Exception as e:
                health_status[agent.name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status
