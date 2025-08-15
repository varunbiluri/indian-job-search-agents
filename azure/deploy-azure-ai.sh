#!/bin/bash

# Azure AI Services Deployment Script for Indian Job Search
# This script sets up Azure AI services for the job search application

set -e

echo "🚀 Setting up Azure AI Services for Indian Job Search..."

# Configuration
RESOURCE_GROUP="indian-job-search-rg"
LOCATION="East US"
STORAGE_ACCOUNT="indianjobsearchstorage"
KEY_VAULT="indian-job-search-kv"
APP_INSIGHTS="indian-job-search-insights"
OPENAI_RESOURCE="indian-job-search-openai"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first."
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure..."
    az login
fi

echo "📋 Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "💾 Creating Storage Account..."
az storage account create \
    --resource-group $RESOURCE_GROUP \
    --name $STORAGE_ACCOUNT \
    --location $LOCATION \
    --sku Standard_LRS \
    --encryption-services blob

echo "🔐 Creating Key Vault..."
az keyvault create \
    --resource-group $RESOURCE_GROUP \
    --name $KEY_VAULT \
    --location $LOCATION \
    --enable-rbac-authorization true

echo "📊 Creating Application Insights..."
az monitor app-insights component create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_INSIGHTS \
    --location $LOCATION \
    --kind web

echo "🤖 Creating Azure OpenAI Resource..."
az cognitiveservices account create \
    --resource-group $RESOURCE_GROUP \
    --name $OPENAI_RESOURCE \
    --location $LOCATION \
    --kind OpenAI \
    --sku S0

echo "🔑 Getting OpenAI API Key..."
OPENAI_KEY=$(az cognitiveservices account keys list \
    --resource-group $RESOURCE_GROUP \
    --name $OPENAI_RESOURCE \
    --query key1 -o tsv)

echo "🔐 Storing secrets in Key Vault..."
az keyvault secret set \
    --vault-name $KEY_VAULT \
    --name "openai-api-key" \
    --value "$OPENAI_KEY"

az keyvault secret set \
    --vault-name $KEY_VAULT \
    --name "openai-endpoint" \
    --value "https://$OPENAI_RESOURCE.openai.azure.com"

echo "📋 Creating OpenAI Deployment..."
az cognitiveservices account deployment create \
    --resource-group $RESOURCE_GROUP \
    --name $OPENAI_RESOURCE \
    --deployment-name gpt-4 \
    --name gpt-4 \
    --model-version 0613 \
    --model-format OpenAI \
    --sku-capacity 1 \
    --sku-name Standard

echo "✅ Azure AI Services setup completed!"
echo ""
echo "📋 Summary:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Storage Account: $STORAGE_VAULT"
echo "   Key Vault: $KEY_VAULT"
echo "   Application Insights: $APP_INSIGHTS"
echo "   OpenAI Resource: $OPENAI_RESOURCE"
echo "   OpenAI Endpoint: https://$OPENAI_RESOURCE.openai.azure.com"
echo ""
echo "🔑 Next steps:"
echo "   1. Update config/azure_ai_config.yaml with the above values"
echo "   2. Deploy the application to Azure Kubernetes"
echo "   3. Test the AI services integration"
