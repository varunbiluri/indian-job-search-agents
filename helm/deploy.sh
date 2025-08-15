#!/bin/bash

# Helm Deployment Script for Indian Job Search Application

set -e

echo "🚀 Deploying Indian Job Search Application with Helm..."

# Configuration
CHART_NAME="indian-job-search"
RELEASE_NAME="indian-job-search"
NAMESPACE="varun-dev"
VALUES_FILE="values.yaml"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found. Please install Helm first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "Chart.yaml" ]; then
    echo "❌ Chart.yaml not found. Please run this script from the helm chart directory."
    exit 1
fi

# Add any required Helm repositories
echo "📦 Adding Helm repositories..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install/Upgrade the chart
echo "🔧 Installing/Upgrading Indian Job Search Application..."
helm upgrade --install $RELEASE_NAME . \
    --namespace $NAMESPACE \
    --create-namespace \
    --values $VALUES_FILE \
    --wait \
    --timeout 10m

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "   Chart: $CHART_NAME"
echo "   Release: $RELEASE_NAME"
echo "   Namespace: $NAMESPACE"
echo ""

# Get service information
echo "🌐 Service Information:"
kubectl get services -n $NAMESPACE | grep $RELEASE_NAME

echo ""
echo "🔍 Check deployment status:"
echo "   kubectl get pods -n $NAMESPACE"
echo "   kubectl get services -n $NAMESPACE"
echo "   helm list -n $NAMESPACE"
