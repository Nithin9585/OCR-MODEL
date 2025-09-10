@echo off
echo 🚀 Deploying OCR Service to Railway...

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Login to Railway
echo 🔐 Logging in to Railway...
railway login

REM Create a new project or link to existing one
echo 📦 Setting up Railway project...
railway init

REM Deploy the service
echo 🚢 Deploying to Railway...
railway up

echo ✅ Deployment complete!
echo 🌐 Your OCR service will be available at the Railway-provided URL
echo 📋 Check Railway dashboard for logs and monitoring

pause
