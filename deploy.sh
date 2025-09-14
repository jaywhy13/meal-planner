#!/bin/bash

echo "🚀 Deploying Meal Planner to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Not logged in to Heroku. Please run 'heroku login' first."
    exit 1
fi

# Get app name from user
read -p "Enter your Heroku app name: " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name is required."
    exit 1
fi

echo "📦 Building frontend..."
./build.sh

echo "🔧 Setting up Heroku app..."
heroku apps:create $APP_NAME 2>/dev/null || echo "App already exists"

echo "⚙️  Setting environment variables..."
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" --app $APP_NAME
heroku config:set DEBUG=False --app $APP_NAME
heroku config:set ALLOWED_HOSTS="$APP_NAME.herokuapp.com" --app $APP_NAME

echo "📤 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"
git push heroku main

echo "🗄️  Running migrations..."
heroku run python backend/manage.py migrate --app $APP_NAME

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "🔧 Admin interface: https://$APP_NAME.herokuapp.com/admin/"
echo "❤️  Health check: https://$APP_NAME.herokuapp.com/health/"
