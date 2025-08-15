#!/bin/bash

# Helm Test Script for Indian Job Search Application

set -e

echo "🧪 Testing Indian Job Search Application with Helm..."

# Configuration
CHART_NAME="indian-job-search"
RELEASE_NAME="indian-job-search"
NAMESPACE="varun-dev"

# Test Helm chart syntax
echo "🔍 Testing Helm chart syntax..."
helm lint .

# Test Helm chart rendering
echo "🔍 Testing Helm chart rendering..."
helm template $RELEASE_NAME . --namespace $NAMESPACE

# Test Helm chart installation (dry-run)
echo "🔍 Testing Helm chart installation (dry-run)..."
helm install $RELEASE_NAME . \
    --namespace $NAMESPACE \
    --dry-run \
    --debug

echo "✅ All Helm tests passed!"
echo ""
echo "🚀 Ready for deployment!"
echo "   Run: ./deploy.sh"
