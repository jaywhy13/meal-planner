#!/bin/bash

echo "Building frontend for production..."

# Build the React frontend
cd frontend
npm install
npm run build

# Copy build files to Django static directory
cd ..
mkdir -p backend/staticfiles
cp -r frontend/build/static/* backend/staticfiles/
cp frontend/build/index.html backend/templates/

echo "Frontend build complete!"
