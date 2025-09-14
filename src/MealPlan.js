import React from 'react';
import './MealPlan.css';

function MealPlan({ weekNumber, weekDays, mealPlan, assignRecipeToMeal, visibleMeals }) {
  const renderMealSlot = (day, mealType) => {
    const dayKey = `day${day}`;
    const recipe = mealPlan[dayKey] && mealPlan[dayKey][mealType];
    
    return (
      <div 
        className="meal-slot"
        onClick={() => {
          // This could open a modal or trigger some selection interface
          console.log(`Clicked on ${mealType} for day ${day}`);
        }}
      >
        {recipe ? recipe.name : 'Add a recipe'}
      </div>
    );
  };

  return (
    <div className="meal-plan">
      <h2>Week {weekNumber} Meal Plan</h2>
      <table className="meal-table">
        <thead>
          <tr>
            <th>Day</th>
            {visibleMeals.breakfast && <th>Breakfast</th>}
            {visibleMeals.lunch && <th>Lunch</th>}
            {visibleMeals.dinner && <th>Dinner</th>}
            {visibleMeals.snack && <th>Snack</th>}
          </tr>
        </thead>
        <tbody>
          {weekDays.map((dayName, index) => {
            const dayNumber = index + 1;
            return (
              <tr key={dayNumber}>
                <td className="day-name">{dayName}</td>
                {visibleMeals.breakfast && <td>{renderMealSlot(dayNumber, 'breakfast')}</td>}
                {visibleMeals.lunch && <td>{renderMealSlot(dayNumber, 'lunch')}</td>}
                {visibleMeals.dinner && <td>{renderMealSlot(dayNumber, 'dinner')}</td>}
                {visibleMeals.snack && <td>{renderMealSlot(dayNumber, 'snack')}</td>}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default MealPlan;