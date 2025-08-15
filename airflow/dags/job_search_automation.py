from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.models import Variable
import requests
import json
import logging

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
    'automated_job_search',
    default_args=default_args,
    description='Automated job search using multi-agent system',
    schedule_interval=timedelta(hours=1),  # Run every hour
    catchup=False,
    tags=['job-search', 'ai', 'automation'],
)

def get_active_job_searches():
    """Get all active job searches from database"""
    try:
        # In production, this would query your database
        # For now, return sample searches
        return [
            {
                "user_id": "user1",
                "job_role": "Python Developer",
                "location": "Remote",
                "keywords": ["python", "fastapi", "kubernetes"]
            },
            {
                "user_id": "user2", 
                "job_role": "Data Scientist",
                "location": "San Francisco",
                "keywords": ["python", "machine learning", "sql"]
            }
        ]
    except Exception as e:
        logging.error(f"Failed to get active job searches: {e}")
        return []

def trigger_job_search(search_config):
    """Trigger job search for a specific configuration"""
    try:
        api_url = "http://job-search-api:8000/search"
        
        payload = {
            "job_role": search_config["job_role"],
            "location": search_config["location"],
            "keywords": search_config["keywords"],
            "user_id": search_config["user_id"]
        }
        
        response = requests.post(api_url, json=payload, timeout=300)
        response.raise_for_status()
        
        results = response.json()
        logging.info(f"Job search completed for {search_config['job_role']}: {results['total_jobs_found']} jobs found")
        
        return results
        
    except Exception as e:
        logging.error(f"Job search failed for {search_config['job_role']}: {e}")
        raise

def run_all_job_searches(**context):
    """Run job searches for all active users"""
    active_searches = get_active_job_searches()
    
    if not active_searches:
        logging.info("No active job searches found")
        return
    
    logging.info(f"Starting job searches for {len(active_searches)} active searches")
    
    for search_config in active_searches:
        try:
            results = trigger_job_search(search_config)
            
            # Store results or send notifications
            logging.info(f"Successfully processed search for {search_config['job_role']}")
            
        except Exception as e:
            logging.error(f"Failed to process search for {search_config['job_role']}: {e}")
            continue

def cleanup_old_results(**context):
    """Clean up old job search results"""
    try:
        # In production, this would clean up old results from database
        # For now, just log the cleanup
        logging.info("Cleaning up old job search results")
        
        # Example cleanup logic:
        # - Remove results older than 30 days
        # - Archive successful searches
        # - Clean up failed searches
        
    except Exception as e:
        logging.error(f"Cleanup failed: {e}")

def send_daily_summary(**context):
    """Send daily summary of job searches"""
    try:
        # In production, this would send email/Slack notifications
        logging.info("Sending daily job search summary")
        
        # Example summary:
        # - Total searches run today
        # - New jobs found
        # - Agent performance metrics
        
    except Exception as e:
        logging.error(f"Failed to send daily summary: {e}")

# Define tasks
start_task = PythonOperator(
    task_id='start_job_search_pipeline',
    python_callable=lambda: logging.info("Starting automated job search pipeline"),
    dag=dag,
)

run_searches_task = PythonOperator(
    task_id='run_all_job_searches',
    python_callable=run_all_job_searches,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_results',
    python_callable=cleanup_old_results,
    dag=dag,
)

summary_task = PythonOperator(
    task_id='send_daily_summary',
    python_callable=send_daily_summary,
    dag=dag,
)

# Task dependencies
start_task >> run_searches_task >> cleanup_task >> summary_task
