# Multi-Agent Job Search Application

A sophisticated, AI-powered job search system that uses multiple agents to search the internet for job opportunities and extract contact information.

## 🚀 Features

- **Multi-Agent Architecture**: Indeed, LinkedIn, and AI-powered agents
- **AI Contact Extraction**: Uses OpenAI to extract contact information from job postings
- **Automated Scheduling**: Airflow DAG runs every hour for continuous job discovery
- **Scalable Design**: Built to scale from 1 user to 1M users
- **Azure Kubernetes**: Production-ready deployment on Azure AKS

## 🏗️ Architecture

```
GitHub Push → Jenkins (Build/Test) → ArgoCD (Deploy) → Azure K8s
                                    ↓
                              Job Search API
                                    ↓
                              Multi-Agent System
                                    ↓
                              [Indeed, LinkedIn, AI]
```

## 📊 Data Model

### Core Entities:
- **Users**: System users with subscription tiers
- **Job Searches**: User-defined search criteria
- **Job Results**: Extracted job information with contact details
- **Search Agents**: Individual search and extraction agents
- **Search Logs**: Performance and error tracking

### Contact Information Extracted:
- Job title and company
- Contact person name
- Email address
- Phone number
- LinkedIn URL
- Application URL

## 🛠️ Technology Stack

- **Backend**: FastAPI + Python 3.11
- **AI/ML**: OpenAI GPT, LangChain
- **Database**: PostgreSQL + Redis
- **Orchestration**: Apache Airflow
- **Deployment**: Kubernetes + ArgoCD
- **CI/CD**: Jenkins + ArgoCD
- **Cloud**: Azure Kubernetes Service

## 🚀 Quick Start

### 1. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="postgresql://user:pass@localhost/db"

# Run the API
python -m uvicorn src.api.main:app --reload
```

### 2. Docker
```bash
# Build image
docker build -t job-search-api .

# Run container
docker run -p 8000:8000 job-search-api
```

### 3. Kubernetes Deployment
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n varun-dev
```

## 📋 API Endpoints

- `GET /health` - System health check
- `POST /search` - Search for jobs
- `GET /agents/stats` - Agent performance statistics
- `POST /users/` - Create new user
- `GET /users/{user_id}/searches` - Get user search history

## 🔄 Airflow Automation

The system includes an Airflow DAG that:
- Runs every hour automatically
- Searches for jobs based on user preferences
- Extracts contact information using AI
- Stores results in the database
- Sends notifications for new opportunities

## 📈 Scaling Strategy

### Current (1 User):
- Single API instance
- Basic database setup
- Manual agent management

### Future (1M Users):
- Horizontal pod autoscaling
- Database sharding and read replicas
- Redis clustering for caching
- Multiple agent instances
- Load balancing and CDN
- Microservices architecture

## 🔐 Security

- API key authentication
- Rate limiting
- Input validation
- Secure database connections
- Kubernetes RBAC

## 📊 Monitoring

- Prometheus metrics
- Structured logging
- Health checks
- Performance dashboards
- Error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Contact: varunreddy.billuri@gmail.com
