#!/bin/bash

echo "Building frontend for production..."

# Build the React frontend
cd frontend
yarn install
yarn run build

# Copy build files to Django static directory
cd ..
mkdir -p backend/staticfiles
cp -r frontend/build/static/* backend/staticfiles/
cp frontend/build/index.html backend/templates/

# Also copy to root for Heroku
mkdir -p staticfiles templates
cp -r frontend/build/static/* staticfiles/
cp frontend/build/index.html templates/

echo "Frontend build complete!"
