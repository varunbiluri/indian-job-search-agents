from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.models import Variable
import requests
import json
import logging
from typing import List, Dict, Any

default_args = {
    'owner': 'varun',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'indian_job_search_automation',
    default_args=default_args,
    description='Automated job search across Indian startups and companies using multi-AI models',
    schedule_interval=timedelta(hours=1),  # Run every hour
    catchup=False,
    tags=['job-search', 'india', 'ai', 'automation', 'startups'],
)

# Indian job market configuration
INDIAN_JOB_ROLES = [
    "Python Developer",
    "Data Scientist", 
    "Machine Learning Engineer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Product Manager",
    "UI/UX Designer",
    "Data Analyst",
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Mobile Developer",
    "QA Engineer",
    "System Administrator",
    "Cloud Engineer"
]

INDIAN_LOCATIONS = [
    "Bangalore",
    "Mumbai", 
    "Delhi",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Gurgaon",
    "Noida",
    "Remote India",
    "Hybrid India"
]

COMPANY_TYPES = [
    "fintech",
    "edtech", 
    "healthtech",
    "ecommerce",
    "saas",
    "logistics",
    "realestate",
    "travel",
    "media",
    "gaming"
]

def get_indian_job_searches() -> List[Dict[str, Any]]:
    """Get comprehensive job searches for Indian market"""
    searches = []
    
    # Generate searches for all combinations
    for job_role in INDIAN_JOB_ROLES:
        for location in INDIAN_LOCATIONS:
            searches.append({
                "job_role": job_role,
                "location": location,
                "keywords": ["India", "Indian", "Startup", "Tech"],
                "priority": "high"
            })
    
    # Add company type specific searches
    for company_type in COMPANY_TYPES:
        searches.append({
            "job_role": "Software Engineer",
            "location": "India",
            "keywords": [company_type, "startup", "India"],
            "priority": "medium"
        })
    
    return searches

def trigger_indian_job_search(search_config: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger job search for Indian market"""
    try:
        api_url = "http://job-search-api:8000/search/indian-market"
        
        payload = {
            "job_role": search_config["job_role"],
            "location": search_config["location"],
            "keywords": search_config["keywords"],
            "market": "indian",
            "company_types": COMPANY_TYPES,
            "priority": search_config.get("priority", "medium")
        }
        
        response = requests.post(api_url, json=payload, timeout=600)  # 10 minute timeout
        response.raise_for_status()
        
        results = response.json()
        logging.info(f"Indian job search completed for {search_config['job_role']} in {search_config['location']}: {results['quality_jobs']} quality jobs found")
        
        return results
        
    except Exception as e:
        logging.error(f"Indian job search failed for {search_config['job_role']} in {search_config['location']}: {e}")
        raise

def run_indian_market_searches(**context) -> None:
    """Run comprehensive job searches across Indian market"""
    active_searches = get_indian_job_searches()
    
    if not active_searches:
        logging.info("No Indian job searches configured")
        return
    
    logging.info(f"Starting Indian market job searches: {len(active_searches)} searches")
    
    successful_searches = 0
    total_jobs_found = 0
    
    for search_config in active_searches:
        try:
            results = trigger_indian_job_search(search_config)
            
            if results.get("status") == "completed":
                successful_searches += 1
                total_jobs_found += results.get("quality_jobs", 0)
            
            # Rate limiting between searches
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"Failed to process Indian search for {search_config['job_role']} in {search_config['location']}: {e}")
            continue
    
    logging.info(f"Indian market search completed: {successful_searches}/{len(active_searches)} successful, {total_jobs_found} total quality jobs found")
    
    # Store summary in XCom for downstream tasks
    context['task_instance'].xcom_push(
        key='indian_search_summary',
        value={
            'total_searches': len(active_searches),
            'successful_searches': successful_searches,
            'total_jobs_found': total_jobs_found,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

def analyze_indian_market_trends(**context) -> None:
    """Analyze trends in Indian job market"""
    try:
        # Get search summary from previous task
        summary = context['task_instance'].xcom_pull(key='indian_search_summary')
        
        if not summary:
            logging.warning("No search summary available for trend analysis")
            return
        
        # Analyze trends
        trends = {
            "hot_job_roles": [],
            "top_locations": [],
            "growing_company_types": [],
            "salary_trends": [],
            "skill_demand": []
        }
        
        # This would integrate with your analytics system
        logging.info(f"Trend analysis completed for Indian market: {summary['total_jobs_found']} jobs analyzed")
        
        # Store trends in XCom
        context['task_instance'].xcom_push(
            key='indian_market_trends',
            value=trends
        )
        
    except Exception as e:
        logging.error(f"Indian market trend analysis failed: {e}")

def send_indian_market_alerts(**context) -> None:
    """Send alerts for Indian market opportunities"""
    try:
        # Get search results and trends
        summary = context['task_instance'].xcom_pull(key='indian_search_summary')
        trends = context['task_instance'].xcom_pull(key='indian_market_trends')
        
        if not summary:
            logging.warning("No search summary available for alerts")
            return
        
        # Generate alerts
        alerts = []
        
        if summary['total_jobs_found'] > 100:
            alerts.append(f"🚀 High job volume: {summary['total_jobs_found']} quality jobs found in Indian market")
        
        if summary['successful_searches'] / summary['total_searches'] < 0.8:
            alerts.append(f"⚠️ Some searches failed: {summary['successful_searches']}/{summary['total_searches']} successful")
        
        # Send alerts (email, Slack, etc.)
        for alert in alerts:
            logging.info(f"ALERT: {alert}")
            # send_alert(alert)  # Implement your alert system
        
        logging.info(f"Indian market alerts sent: {len(alerts)} alerts generated")
        
    except Exception as e:
        logging.error(f"Failed to send Indian market alerts: {e}")

def cleanup_indian_search_data(**context) -> None:
    """Clean up old Indian search data"""
    try:
        logging.info("Cleaning up old Indian job search data")
        
        # Cleanup logic:
        # - Remove results older than 7 days
        # - Archive successful searches
        # - Clean up failed searches
        # - Optimize database
        
        logging.info("Indian search data cleanup completed")
        
    except Exception as e:
        logging.error(f"Indian search data cleanup failed: {e}")

def generate_indian_market_report(**context) -> None:
    """Generate comprehensive Indian market report"""
    try:
        summary = context['task_instance'].xcom_pull(key='indian_search_summary')
        trends = context['task_instance'].xcom_pull(key='indian_market_trends')
        
        report = {
            "report_type": "indian_market_hourly",
            "timestamp": datetime.utcnow().isoformat(),
            "search_summary": summary,
            "market_trends": trends,
            "company_coverage": len(COMPANY_TYPES),
            "location_coverage": len(INDIAN_LOCATIONS),
            "job_role_coverage": len(INDIAN_JOB_ROLES)
        }
        
        # Store report
        context['task_instance'].xcom_push(key='indian_market_report', value=report)
        
        logging.info(f"Indian market report generated: {report['job_role_coverage']} roles, {report['location_coverage']} locations, {report['company_coverage']} company types")
        
    except Exception as e:
        logging.error(f"Failed to generate Indian market report: {e}")

# Define tasks
start_task = PythonOperator(
    task_id='start_indian_job_search_pipeline',
    python_callable=lambda: logging.info("Starting Indian market job search pipeline"),
    dag=dag,
)

run_searches_task = PythonOperator(
    task_id='run_indian_market_searches',
    python_callable=run_indian_market_searches,
    dag=dag,
)

analyze_trends_task = PythonOperator(
    task_id='analyze_indian_market_trends',
    python_callable=analyze_indian_market_trends,
    dag=dag,
)

send_alerts_task = PythonOperator(
    task_id='send_indian_market_alerts',
    python_callable=send_indian_market_alerts,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_indian_search_data',
    python_callable=cleanup_indian_search_data,
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_indian_market_report',
    python_callable=generate_indian_market_report,
    dag=dag,
)

# Task dependencies
start_task >> run_searches_task >> analyze_trends_task >> send_alerts_task
run_searches_task >> cleanup_task
analyze_trends_task >> generate_report_task
