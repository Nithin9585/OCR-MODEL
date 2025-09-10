#!/bin/bash

echo "🚀 Deploying OCR Service to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Logging in to Railway..."
railway login

# Create a new project or link to existing one
echo "📦 Setting up Railway project..."
railway init

# Deploy the service
echo "🚢 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your OCR service will be available at the Railway-provided URL"
echo "📋 Check Railway dashboard for logs and monitoring"
