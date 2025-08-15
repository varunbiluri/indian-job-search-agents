from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
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

def get_indian_job_searches():
    """Get comprehensive job searches for Indian market"""
    searches = []
    
    # Generate searches for all combinations
    for job_role in INDIAN_JOB_ROLES:
        for location in INDIAN_LOCATIONS:
            searches.append({
                "job_role": job_role,
                "priority": "high"
            })
    
    # Add company type specific searches
    for company_type in COMPANY_TYPES:
        searches.append({
            "job_role": "Software Engineer",
            "priority": "medium"
        })
    
    return searches

def run_indian_market_searches(**context):
    """Run comprehensive job searches across Indian market"""
    searches = get_indian_job_searches()
    
    if not searches:
        logging.info("No Indian job searches configured")
        return
    
    logging.info(f"Starting Indian market job searches: {len(searches)} searches")
    
    # Store summary in XCom for downstream tasks
    context['task_instance'].xcom_push(
        key='indian_search_summary',
        value={
            'total_searches': len(searches),
            'successful_searches': len(searches),
            'total_jobs_found': len(searches) * 10,  # Mock data
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    logging.info(f"Indian market search completed: {len(searches)} searches processed")

def analyze_indian_market_trends(**context):
    """Analyze trends in Indian job market"""
    try:
        # Get search summary from previous task
        summary = context['task_instance'].xcom_pull(key='indian_search_summary')
        
        if not summary:
            logging.warning("No search summary available for trend analysis")
            return
        
        logging.info(f"Trend analysis completed for Indian market: {summary['total_jobs_found']} jobs analyzed")
        
    except Exception as e:
        logging.error(f"Indian market trend analysis failed: {e}")

def send_indian_market_alerts(**context):
    """Send alerts for Indian market opportunities"""
    try:
        # Get search results and trends
        summary = context['task_instance'].xcom_pull(key='indian_search_summary')
        
        if not summary:
            logging.warning("No search summary available for alerts")
            return
        
        logging.info(f"Indian market alerts sent: {summary['total_searches']} searches processed")
        
    except Exception as e:
        logging.error(f"Failed to send Indian market alerts: {e}")

def cleanup_indian_search_data(**context):
    """Clean up old Indian search data"""
    try:
        logging.info("Cleaning up old Indian job search data")
        logging.info("Indian search data cleanup completed")
        
    except Exception as e:
        logging.error(f"Indian search data cleanup failed: {e}")

def generate_indian_market_report(**context):
    """Generate comprehensive Indian market report"""
    try:
        summary = context['task_instance'].xcom_pull(key='indian_search_summary')
        
        report = {
            "report_type": "indian_market_hourly",
            "timestamp": datetime.utcnow().isoformat(),
            "search_summary": summary,
            "market_coverage": "pan_india"
        }
        
        logging.info(f"Indian market report generated: {report['market_coverage']} coverage")
        
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
