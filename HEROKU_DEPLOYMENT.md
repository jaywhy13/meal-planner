# Heroku Deployment Guide

## Prerequisites
1. Install Heroku CLI
2. Create a Heroku account
3. Login to Heroku: `heroku login`

## Deployment Steps

### 1. Create Heroku App
```bash
heroku create your-meal-planner-app-name
```

### 2. Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
```

### 3. Build Frontend
```bash
./build.sh
```

### 4. Deploy to Heroku
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 5. Run Migrations
```bash
heroku run python backend/manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
heroku run python backend/manage.py createsuperuser
```

## Environment Variables

Set these in your Heroku app settings:

- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Your Heroku app domain
- `CORS_ALLOWED_ORIGINS`: Your frontend URL

## Features

✅ **SQLite Database**: Uses SQLite for simplicity
✅ **Static Files**: Serves React build files from Django
✅ **CORS**: Configured for frontend-backend communication
✅ **Health Check**: `/health/` endpoint for monitoring
✅ **Admin Interface**: Available at `/admin/`

## URLs

- **App**: `https://your-app-name.herokuapp.com/`
- **API**: `https://your-app-name.herokuapp.com/api/`
- **Admin**: `https://your-app-name.herokuapp.com/admin/`
- **Health**: `https://your-app-name.herokuapp.com/health/`

## Troubleshooting

1. **Build Fails**: Check that all dependencies are in requirements.txt
2. **Static Files**: Ensure build.sh runs successfully
3. **Database**: Run migrations after deployment
4. **CORS Issues**: Update CORS_ALLOWED_ORIGINS

## Notes

- The app uses SQLite for simplicity (data will be lost on dyno restart)
- For production with persistent data, consider using PostgreSQL addon
- Frontend is built and served from Django static files
- All API endpoints are prefixed with `/api/`
