# Frontend-Backend Integration Fix

## The Issue
The frontend is trying to connect to `localhost:8000` but the backend is now running in Docker, which might not be accessible.

## Solutions

### Option 1: Start Backend with Docker (Recommended)

1. **Start the backend:**
   ```bash
   cd /Users/jmwright/code/meal-planner
   docker-compose up --build
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   cd /Users/jmwright/code/meal-planner/frontend
   npm start
   ```

3. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/api/
   ```

### Option 2: Use the Start Script

Run the complete application startup script:
```bash
cd /Users/jmwright/code/meal-planner
./start-app.sh
```

### Option 3: Manual Backend (Fallback)

If Docker isn't working, you can run the backend manually:

1. **Activate virtual environment:**
   ```bash
   cd /Users/jmwright/code/meal-planner/backend
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the server:**
   ```bash
   python manage.py runserver
   ```

## Troubleshooting

### Backend Not Accessible

1. **Check if Docker is running:**
   ```bash
   docker --version
   docker info
   ```

2. **Check Docker containers:**
   ```bash
   docker ps
   docker-compose ps
   ```

3. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

4. **Test backend directly:**
   ```bash
   curl http://localhost:8000/api/
   ```

### Frontend Connection Issues

1. **Check browser console** for API errors
2. **Verify API URL** in `frontend/src/services/api.js`
3. **Check network tab** in browser dev tools

### Port Conflicts

If ports 3000 or 8000 are in use:

1. **Kill processes on port 8000:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **Kill processes on port 3000:**
   ```bash
   lsof -ti:3000 | xargs kill -9
   ```

## Expected Behavior

- **Backend**: http://localhost:8000/api/ should return JSON
- **Frontend**: http://localhost:3000 should load the meal planner
- **Integration**: Frontend should be able to fetch meal plans from backend

## Quick Test

Run this to test the full stack:
```bash
# Terminal 1: Start backend
cd /Users/jmwright/code/meal-planner
docker-compose up --build

# Terminal 2: Start frontend
cd /Users/jmwright/code/meal-planner/frontend
npm start
```

The frontend should now be able to connect to the Dockerized backend!
