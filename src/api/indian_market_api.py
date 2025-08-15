from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from ..agents.indian_market_orchestrator import IndianMarketOrchestrator
from ..database.database import get_db
from ..database.indian_market_models import IndianCompany, IndianJobPosting, IndianMarketSearch

router = APIRouter(prefix="/indian-market", tags=["Indian Market"])

# Initialize orchestrator
orchestrator = IndianMarketOrchestrator()

# Pydantic models
class IndianMarketSearchRequest(BaseModel):
    job_role: str
    location: Optional[str] = "India"
    company_types: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    user_id: Optional[str] = None
    priority: Optional[str] = "medium"

class CompanyTypeSearchRequest(BaseModel):
    company_type: str
    job_role: str
    location: Optional[str] = "India"

class LocationSearchRequest(BaseModel):
    location: str
    job_role: str
    company_types: Optional[List[str]] = None

class IndianMarketStats(BaseModel):
    total_companies: int
    companies_by_type: Dict[str, int]
    total_jobs_found: int
    ai_model_accuracy: Dict[str, float]
    market_coverage: str

@router.post("/search", response_model=Dict[str, Any])
async def search_indian_market(request: IndianMarketSearchRequest, background_tasks: BackgroundTasks):
    """Search for jobs across the entire Indian market"""
    try:
        # Run comprehensive Indian market search
        results = await orchestrator.search_indian_market(
            job_role=request.job_role,
            location=request.location,
            keywords=request.keywords,
            user_preferences={"locations": [request.location], "company_types": request.company_types}
        )
        
        # Store search results in database if user_id provided
        if request.user_id:
            background_tasks.add_task(store_indian_search_results, request.user_id, results)
        
        return results
        
    except Exception as e:
        logging.error(f"Indian market search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/company-type", response_model=Dict[str, Any])
async def search_by_company_type(request: CompanyTypeSearchRequest):
    """Search jobs in specific company types (e.g., fintech, edtech)"""
    try:
        results = await orchestrator.search_by_company_type(
            job_role=request.job_role,
            company_type=request.company_type,
            location=request.location
        )
        
        return results
        
    except Exception as e:
        logging.error(f"Company type search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/location", response_model=Dict[str, Any])
async def search_by_location(request: LocationSearchRequest):
    """Search jobs in specific Indian cities/regions"""
    try:
        results = await orchestrator.search_by_location(
            job_role=request.job_role,
            specific_location=request.location
        )
        
        return results
        
    except Exception as e:
        logging.error(f"Location search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=IndianMarketStats)
async def get_indian_market_stats():
    """Get comprehensive statistics for Indian market"""
    try:
        stats = await orchestrator.get_indian_market_stats()
        return IndianMarketStats(**stats)
        
    except Exception as e:
        logging.error(f"Failed to get Indian market stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies", response_model=List[Dict[str, Any]])
async def get_indian_companies(company_type: Optional[str] = None, limit: int = 100):
    """Get list of Indian companies"""
    try:
        db = next(get_db())
        
        query = db.query(IndianCompany).filter(IndianCompany.is_active == True)
        
        if company_type:
            query = query.filter(IndianCompany.company_type == company_type)
        
        companies = query.limit(limit).all()
        
        return [
            {
                "id": company.id,
                "name": company.name,
                "website": company.website,
                "company_type": company.company_type,
                "founded_year": company.founded_year,
                "employee_count": company.employee_count,
                "funding_stage": company.funding_stage,
                "headquarters": company.headquarters
            }
            for company in companies
        ]
        
    except Exception as e:
        logging.error(f"Failed to get Indian companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends", response_model=List[Dict[str, Any]])
async def get_market_trends(trend_type: Optional[str] = None, days: int = 7):
    """Get market trends and insights"""
    try:
        db = next(get_db())
        
        # This would query your trends table
        # For now, return mock data
        trends = [
            {
                "trend_type": "job_demand",
                "trend_data": {
                    "python_developer": {"growth": 15.2, "demand": "high"},
                    "data_scientist": {"growth": 22.1, "demand": "very_high"},
                    "devops_engineer": {"growth": 18.7, "demand": "high"}
                },
                "confidence_score": 0.85,
                "trend_date": datetime.utcnow().isoformat()
            },
            {
                "trend_type": "salary_trends",
                "trend_data": {
                    "bangalore": {"avg_salary": 1800000, "growth": 8.5},
                    "mumbai": {"avg_salary": 1650000, "growth": 7.2},
                    "delhi": {"avg_salary": 1550000, "growth": 6.8}
                },
                "confidence_score": 0.78,
                "trend_date": datetime.utcnow().isoformat()
            }
        ]
        
        return trends
        
    except Exception as e:
        logging.error(f"Failed to get market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-models/performance", response_model=List[Dict[str, Any]])
async def get_ai_model_performance():
    """Get performance metrics for AI models"""
    try:
        # This would query your AI performance table
        # For now, return mock data
        performance = [
            {
                "model_name": "llama2",
                "task_type": "contact_extraction",
                "accuracy_score": 0.87,
                "response_time": 2.3,
                "success_rate": 94.2
            },
            {
                "model_name": "falcon",
                "task_type": "contact_extraction",
                "accuracy_score": 0.82,
                "response_time": 1.8,
                "success_rate": 91.5
            },
            {
                "model_name": "mistral",
                "task_type": "contact_extraction",
                "accuracy_score": 0.89,
                "response_time": 2.1,
                "success_rate": 96.1
            }
        ]
        
        return performance
        
    except Exception as e:
        logging.error(f"Failed to get AI model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/companies/add", response_model=Dict[str, str])
async def add_indian_company(company_data: Dict[str, Any]):
    """Add a new Indian company to the database"""
    try:
        db = next(get_db())
        
        new_company = IndianCompany(
            name=company_data["name"],
            website=company_data.get("website"),
            company_type=company_data.get("company_type"),
            founded_year=company_data.get("founded_year"),
            employee_count=company_data.get("employee_count"),
            funding_stage=company_data.get("funding_stage"),
            headquarters=company_data.get("headquarters")
        )
        
        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        
        return {"company_id": new_company.id, "message": "Company added successfully"}
        
    except Exception as e:
        logging.error(f"Failed to add company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def store_indian_search_results(user_id: str, results: Dict[str, Any]):
    """Store Indian market search results in database (background task)"""
    try:
        db = next(get_db())
        
        # Create search record
        search_record = IndianMarketSearch(
            user_id=user_id,
            job_role=results["job_role"],
            location=results.get("location"),
            company_types=results.get("company_types", []),
            keywords=results.get("keywords"),
            total_jobs_found=results.get("total_jobs_found", 0),
            quality_jobs_found=results.get("quality_jobs", 0),
            last_run=datetime.utcnow()
        )
        
        db.add(search_record)
        db.commit()
        db.refresh(search_record)
        
        logging.info(f"Stored Indian market search results for user {user_id}: {results.get('quality_jobs', 0)} quality jobs")
        
    except Exception as e:
        logging.error(f"Failed to store Indian market search results: {e}")
