from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from ..agents.orchestrator import MultiAgentOrchestrator
from ..database.models import User, JobSearch, JobSearchResult
from ..database.database import get_db, engine

# Create database tables
from ..database.models import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multi-Agent Job Search API",
    description="AI-powered job search using multiple agents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = MultiAgentOrchestrator()

# Pydantic models
class JobSearchRequest(BaseModel):
    job_role: str
    location: Optional[str] = None
    keywords: Optional[List[str]] = None
    user_id: Optional[str] = None

class JobSearchResponse(BaseModel):
    status: str
    job_role: str
    total_jobs_found: int
    execution_time: float
    jobs: List[Dict[str, Any]]
    timestamp: datetime

class UserCreate(BaseModel):
    email: str
    name: str

@app.get("/")
async def root():
    return {"message": "Multi-Agent Job Search API"}

@app.get("/health")
async def health_check():
    """Check system health"""
    try:
        agent_health = await orchestrator.health_check()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "agents": agent_health
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest, background_tasks: BackgroundTasks):
    """Search for jobs using multiple agents"""
    try:
        # Run job search
        results = await orchestrator.search_all_sources(
            job_role=request.job_role,
            location=request.location,
            keywords=request.keywords
        )
        
        # Store results in database if user_id provided
        if request.user_id:
            background_tasks.add_task(store_search_results, request.user_id, results)
        
        return JobSearchResponse(**results)
        
    except Exception as e:
        logging.error(f"Job search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/stats")
async def get_agent_statistics():
    """Get statistics for all agents"""
    try:
        stats = orchestrator.get_agent_statistics()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/", response_model=Dict[str, str])
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        db = next(get_db())
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        new_user = User(
            email=user.email,
            name=user.name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"user_id": new_user.id, "message": "User created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/searches")
async def get_user_searches(user_id: str):
    """Get job searches for a specific user"""
    try:
        db = next(get_db())
        searches = db.query(JobSearch).filter(JobSearch.user_id == user_id).all()
        
        return {
            "status": "success",
            "user_id": user_id,
            "searches": [
                {
                    "id": search.id,
                    "job_role": search.job_role,
                    "location": search.location,
                    "created_at": search.created_at,
                    "is_active": search.is_active
                }
                for search in searches
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def store_search_results(user_id: str, results: Dict[str, Any]):
    """Store search results in database (background task)"""
    try:
        db = next(get_db())
        
        # Create job search record
        job_search = JobSearch(
            user_id=user_id,
            job_role=results["job_role"],
            location=results.get("location"),
            keywords=results.get("keywords")
        )
        
        db.add(job_search)
        db.commit()
        db.refresh(job_search)
        
        # Store individual job results
        for job_data in results.get("jobs", []):
            job_result = JobSearchResult(
                job_search_id=job_search.id,
                source=job_data.get("source", "unknown"),
                job_title=job_data.get("job_title", ""),
                company_name=job_data.get("company_name", ""),
                location=job_data.get("location", ""),
                contact_person=job_data.get("contact_person"),
                contact_email=job_data.get("contact_email"),
                contact_phone=job_data.get("contact_phone"),
                linkedin_url=job_data.get("linkedin_url"),
                confidence_score=job_data.get("confidence_score", 0)
            )
            
            db.add(job_result)
        
        db.commit()
        logging.info(f"Stored {len(results.get('jobs', []))} job results for user {user_id}")
        
    except Exception as e:
        logging.error(f"Failed to store search results: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
