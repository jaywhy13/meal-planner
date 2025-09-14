# Meal Planner System

A full-stack meal planning application built with Django REST API backend and React frontend.

## Features

- **Monthly Calendar View**: Visual spreadsheet-style interface for planning meals
- **Food Management**: Add, edit, and search foods with autocomplete functionality
- **Food Creation in Meals**: Create new foods directly from the Add Meal dialog
- **Dedicated Foods Management**: Separate page for managing all foods with full CRUD operations
- **Multiple Meal Plans**: Create, edit, and delete multiple meal plans
- **Meal Suggestions**: AI-powered healthy meal suggestions
- **Meal Plan Generation**: Auto-generate meal plans with healthy suggestions
- **Daily Meal Tracking**: Track breakfast, lunch, dinner, and snacks for each day

## Tech Stack

### Backend
- Django 4.2
- Django REST Framework
- SQLite database
- CORS headers for API access

### Frontend
- React 18
- Material-UI (MUI)
- React Router
- Axios for API calls
- Day.js for date handling

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install django djangorestframework django-cors-headers python-decouple
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Populate initial data:
   ```bash
   python manage.py populate_data
   ```

6. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Meal Plans
- `GET /api/meal-plans/` - List all meal plans
- `POST /api/meal-plans/` - Create a new meal plan
- `GET /api/meal-plans/{id}/` - Get meal plan details
- `PUT /api/meal-plans/{id}/` - Update meal plan
- `DELETE /api/meal-plans/{id}/` - Delete meal plan
- `POST /api/meal-plans/{id}/generate_meal_plan/` - Generate meal plan

### Foods
- `GET /api/foods/` - List all foods
- `POST /api/foods/` - Create a new food
- `GET /api/foods/search/?q={query}` - Search foods

### Daily Meals
- `GET /api/daily-meals/?meal_plan={id}` - List meals for a meal plan
- `POST /api/daily-meals/` - Create a daily meal
- `PUT /api/daily-meals/{id}/` - Update daily meal
- `DELETE /api/daily-meals/{id}/` - Delete daily meal

### Meal Suggestions
- `GET /api/meal-suggestions/` - List all meal suggestions
- `GET /api/meal-suggestions/by_meal_type/?meal_type={type}` - Get suggestions by meal type

## Usage

1. **Create a Meal Plan**: Click "New Meal Plan" and enter a name
2. **View Calendar**: Click on a meal plan to see the monthly calendar view
3. **Add Meals**: Click "Add" on any day/meal type to add foods
4. **Create New Foods**: Use the "Add New Food" section in the meal dialog to create foods on-the-fly
5. **Manage Foods**: Navigate to the "Foods" page to manage all foods with full CRUD operations
6. **Edit Meals**: Click the edit icon to modify existing meals
7. **Generate Plan**: Use the "Generate Plan" button to auto-populate with healthy suggestions
8. **Search Foods**: Use the autocomplete when adding foods to meals

## Database Models

- **MealPlan**: Contains meal plan name and metadata
- **Food**: Individual food items with categories
- **DailyMeal**: Meals for specific dates and meal types
- **MealSuggestion**: Pre-defined healthy meal combinations

## Development

To add new features:

1. Update Django models in `backend/meals/models.py`
2. Create/update serializers in `backend/meals/serializers.py`
3. Add API views in `backend/meals/views.py`
4. Update URL patterns in `backend/meals/urls.py`
5. Run migrations: `python manage.py makemigrations && python manage.py migrate`
6. Update React components in `frontend/src/components/`
7. Update API service calls in `frontend/src/services/api.js`
