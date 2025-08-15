#!/bin/bash

# Simple Cloud Integration Test for Indian Job Search
# Tests the system in the cloud environment

echo "🚀 Starting Cloud Integration Tests..."
echo "=================================================="
echo "⏰ Test started at: $(date)"
echo "🌐 Testing in Azure Kubernetes cluster"
echo "=================================================="

# Test 1: Check if we're in the right directory
echo ""
echo "🔍 Test 1: Project Structure"
if [ -f "src/agents/indian_companies_agent.py" ]; then
    echo "✅ Indian companies agent found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Indian companies agent not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

if [ -f "src/agents/azure_ai_models.py" ]; then
    echo "✅ Azure AI models agent found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Azure AI models agent not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

if [ -f "config/azure_ai_config.yaml" ]; then
    echo "✅ Azure AI configuration found"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Azure AI configuration not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 2: Check Kubernetes deployment
echo ""
echo "🔍 Test 2: Kubernetes Deployment"
if kubectl get pods -n varun-dev | grep -q "job-search-api-test.*Running"; then
    echo "✅ Test API is running"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Test API is not running"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

if kubectl get services -n varun-dev | grep -q "job-search-api-test"; then
    echo "✅ Test API service exists"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Test API service not found"
    FAILED_TESTS=$((PASSED_TESTS + 1))
fi

# Test 3: Check Azure AI Models
echo ""
echo "🔍 Test 3: Azure AI Models"
if kubectl get deployments -n varun-dev | grep -q "llama2-service-lite"; then
    echo "✅ Llama2 service deployment exists"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Llama2 service deployment not found"
    FAILED_TESTS=$((PASSED_TESTS + 1))
fi

if kubectl get deployments -n varun-dev | grep -q "falcon-service-lite"; then
    echo "✅ Falcon service deployment exists"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Falcon service deployment not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

if kubectl get deployments -n varun-dev | grep -q "mistral-service-lite"; then
    echo "✅ Mistral service deployment exists"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Mistral service deployment not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 4: Check Configuration
echo ""
echo "🔍 Test 4: Configuration Files"
if grep -q "azure_openai" config/azure_ai_config.yaml; then
    echo "✅ Azure OpenAI configuration present"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Azure OpenAI configuration missing"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

if grep -q "indian_market" config/indian_market_config.yaml; then
    echo "✅ Indian market configuration present"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Indian market configuration missing"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Initialize counters
PASSED_TESTS=0
FAILED_TESTS=0

# Test 5: Check Git Branch
echo ""
echo "🔍 Test 5: Git Branch"
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "feature/azure-ai-models-testing" ]; then
    echo "✅ Correct branch: $CURRENT_BRANCH"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Wrong branch: $CURRENT_BRANCH (expected: feature/azure-ai-models-testing)"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 6: Check Remote
echo ""
echo "🔍 Test 6: Git Remote"
if git remote -v | grep -q "indian-job-search-agents"; then
    echo "✅ Correct remote repository"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "❌ Wrong remote repository"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Print Results
echo ""
echo "=================================================="
echo "🧪 CLOUD INTEGRATION TEST RESULTS"
echo "=================================================="

TOTAL_TESTS=$((PASSED_TESTS + FAILED_TESTS))

echo "📊 Total Tests: $TOTAL_TESTS"
echo "✅ Passed: $PASSED_TESTS"
echo "❌ Failed: $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo "🎉 All cloud integration tests passed!"
    echo "   The feature branch is ready for production deployment!"
    echo "   You can now merge this to main branch!"
else
    echo ""
    echo "⚠️  $FAILED_TESTS test(s) failed."
    echo "   Please fix issues before merging to main."
fi

echo "=================================================="
