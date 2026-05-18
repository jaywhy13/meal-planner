import calendar
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from meals.models import DailyMeal, Food, MealPlan, MealSettings, MealSuggestion


class Command(BaseCommand):
    help = 'Populate initial food and meal suggestion data'

    def handle(self, *args, **options):
        # Create initial foods
        foods_data = [
            # Proteins
            {'name': 'Chicken Breast', 'category': 'Protein'},
            {'name': 'Salmon', 'category': 'Protein'},
            {'name': 'Eggs', 'category': 'Protein'},
            {'name': 'Greek Yogurt', 'category': 'Protein'},
            {'name': 'Tofu', 'category': 'Protein'},
            {'name': 'Turkey', 'category': 'Protein'},
            {'name': 'Beans', 'category': 'Protein'},
            {'name': 'Quinoa', 'category': 'Protein'},
            
            # Vegetables
            {'name': 'Broccoli', 'category': 'Vegetable'},
            {'name': 'Spinach', 'category': 'Vegetable'},
            {'name': 'Carrots', 'category': 'Vegetable'},
            {'name': 'Bell Peppers', 'category': 'Vegetable'},
            {'name': 'Sweet Potato', 'category': 'Vegetable'},
            {'name': 'Avocado', 'category': 'Vegetable'},
            {'name': 'Tomatoes', 'category': 'Vegetable'},
            {'name': 'Cucumber', 'category': 'Vegetable'},
            
            # Fruits
            {'name': 'Banana', 'category': 'Fruit'},
            {'name': 'Apple', 'category': 'Fruit'},
            {'name': 'Berries', 'category': 'Fruit'},
            {'name': 'Orange', 'category': 'Fruit'},
            {'name': 'Grapes', 'category': 'Fruit'},
            
            # Grains
            {'name': 'Brown Rice', 'category': 'Grain'},
            {'name': 'Oats', 'category': 'Grain'},
            {'name': 'Whole Wheat Bread', 'category': 'Grain'},
            {'name': 'Pasta', 'category': 'Grain'},

            # Starches
            {'name': 'Potato', 'category': 'Starch'},
            {'name': 'Plantain', 'category': 'Starch'},
            {'name': 'White Rice', 'category': 'Starch'},
            {'name': 'Couscous', 'category': 'Starch'},

            # Dairy
            {'name': 'Milk', 'category': 'Dairy'},
            {'name': 'Cheese', 'category': 'Dairy'},
            {'name': 'Butter', 'category': 'Dairy'},
        ]
        
        for food_data in foods_data:
            food, created = Food.objects.get_or_create(
                name=food_data['name'],
                defaults={'category': food_data['category']}
            )
            if created:
                self.stdout.write(f'Created food: {food.name}')
        
        # Create meal suggestions
        suggestions_data = [
            {
                'name': 'Healthy Breakfast Bowl',
                'description': 'Greek yogurt with berries and oats',
                'meal_type': 'breakfast',
                'foods': ['Greek Yogurt', 'Berries', 'Oats']
            },
            {
                'name': 'Protein Power Breakfast',
                'description': 'Scrambled eggs with spinach and whole wheat toast',
                'meal_type': 'breakfast',
                'foods': ['Eggs', 'Spinach', 'Whole Wheat Bread']
            },
            {
                'name': 'Grilled Chicken Salad',
                'description': 'Mixed greens with grilled chicken and vegetables',
                'meal_type': 'lunch',
                'foods': ['Chicken Breast', 'Spinach', 'Tomatoes', 'Cucumber', 'Avocado']
            },
            {
                'name': 'Salmon Quinoa Bowl',
                'description': 'Baked salmon with quinoa and roasted vegetables',
                'meal_type': 'lunch',
                'foods': ['Salmon', 'Quinoa', 'Broccoli', 'Bell Peppers']
            },
            {
                'name': 'Turkey and Sweet Potato',
                'description': 'Lean turkey with roasted sweet potato and vegetables',
                'meal_type': 'dinner',
                'foods': ['Turkey', 'Sweet Potato', 'Broccoli', 'Carrots']
            },
            {
                'name': 'Vegetarian Buddha Bowl',
                'description': 'Tofu with brown rice and mixed vegetables',
                'meal_type': 'dinner',
                'foods': ['Tofu', 'Brown Rice', 'Bell Peppers', 'Broccoli', 'Avocado']
            },
        ]
        
        for suggestion_data in suggestions_data:
            suggestion, created = MealSuggestion.objects.get_or_create(
                name=suggestion_data['name'],
                defaults={
                    'description': suggestion_data['description'],
                    'meal_type': suggestion_data['meal_type'],
                    'is_healthy': True
                }
            )
            
            if created:
                # Add foods to the suggestion
                food_names = suggestion_data['foods']
                foods = Food.objects.filter(name__in=food_names)
                suggestion.foods.set(foods)
                self.stdout.write(f'Created meal suggestion: {suggestion.name}')
        
        # Create sample MealPlan anchored to the first day of the current month
        start_date = date.today().replace(day=1)
        plan, plan_created = MealPlan.objects.get_or_create(
            name='Sample Meal Plan',
            defaults={'start_date': start_date},
        )
        if plan_created:
            self.stdout.write(f'Created meal plan: {plan.name}')

        # Ensure MealSettings exist for the plan
        meal_settings, _ = MealSettings.objects.get_or_create(meal_plan=plan)

        # Map ISO weekday (1-7) to MealSettings field name
        day_field_map = {
            1: 'monday_enabled', 2: 'tuesday_enabled', 3: 'wednesday_enabled',
            4: 'thursday_enabled', 5: 'friday_enabled', 6: 'saturday_enabled',
            7: 'sunday_enabled',
        }

        enabled_meal_types = [
            meal_type for meal_type, field in [
                ('breakfast', 'breakfast_enabled'), ('lunch', 'lunch_enabled'),
                ('dinner', 'dinner_enabled'), ('snack', 'snack_enabled'),
            ] if getattr(meal_settings, field)
        ]

        _, days_in_month = calendar.monthrange(start_date.year, start_date.month)
        meals_created = 0
        for offset in range(days_in_month):
            current_date = start_date + timedelta(days=offset)
            day_field = day_field_map[current_date.isoweekday()]
            if not getattr(meal_settings, day_field):
                continue

            for meal_type in enabled_meal_types:
                _, created = DailyMeal.objects.get_or_create(
                    meal_plan=plan,
                    date=current_date,
                    meal_type=meal_type,
                )
                if created:
                    meals_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated initial data! '
                f'Sample Meal Plan seeded with {meals_created} new DailyMeal records '
                f'for {start_date.strftime("%B %Y")}.'
            )
        )
