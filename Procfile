web: cd backend && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn meal_planner.wsgi:application --bind 0.0.0.0:$PORT
