# Meal Planner Backend - Docker Setup

This backend is now dockerized and can run without requiring Python to be installed on your machine.

## Quick Start with Docker Compose

### Option 1: Simple Setup (SQLite)
```bash
docker-compose up --build
```

### Option 2: Production Setup (PostgreSQL)
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## Setup Steps

1. **Start the services:**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **Create a superuser (optional):**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Access the API:**
   - Backend API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

## Individual Docker Commands

If you prefer to run Docker commands individually:

1. **Build the image:**
   ```bash
   cd backend
   docker build -t meal-planner-backend .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 meal-planner-backend
   ```

## Environment Variables

The application uses the following environment variables:

- `SECRET_KEY`: Django secret key (defaults to development key)
- `DEBUG`: Enable debug mode (defaults to True)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection string (empty for SQLite)

## Database Options

- **Development**: Uses SQLite by default (docker-compose.yml)
- **Production**: Uses PostgreSQL (docker-compose.prod.yml)

## Services

- **Backend**: Django REST API on port 8000
- **Database**: PostgreSQL on port 5432 (when using docker-compose.prod.yml)

## Development

For development with hot reloading, use:
```bash
docker-compose up --build
```

The backend code is mounted as a volume, so changes will be reflected immediately.

## Troubleshooting

If you encounter issues:

1. **Check Docker is running:**
   ```bash
   docker --version
   docker info
   ```

2. **Rebuild the image:**
   ```bash
   docker-compose build --no-cache
   ```

3. **Check logs:**
   ```bash
   docker-compose logs backend
   ```

4. **Reset everything:**
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```
