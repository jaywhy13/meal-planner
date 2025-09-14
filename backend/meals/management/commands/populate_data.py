from django.core.management.base import BaseCommand
from meals.models import Food, MealSuggestion


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
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated initial data!')
        )
