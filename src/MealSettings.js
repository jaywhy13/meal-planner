import React from 'react';

function MealSettings({ visibleMeals, setVisibleMeals }) {
  const toggleMealVisibility = (mealType) => {
    setVisibleMeals(prev => ({
      ...prev,
      [mealType]: !prev[mealType]
    }));
  };

  return (
    <div className="meal-settings">
      <h2>Meal Settings</h2>
      <div className="meal-toggles">
        <div className="meal-toggle">
          <input
            type="checkbox"
            id="breakfast"
            checked={visibleMeals.breakfast}
            onChange={() => toggleMealVisibility('breakfast')}
          />
          <label htmlFor="breakfast">Breakfast</label>
        </div>
        <div className="meal-toggle">
          <input
            type="checkbox"
            id="lunch"
            checked={visibleMeals.lunch}
            onChange={() => toggleMealVisibility('lunch')}
          />
          <label htmlFor="lunch">Lunch</label>
        </div>
        <div className="meal-toggle">
          <input
            type="checkbox"
            id="dinner"
            checked={visibleMeals.dinner}
            onChange={() => toggleMealVisibility('dinner')}
          />
          <label htmlFor="dinner">Dinner</label>
        </div>
        <div className="meal-toggle">
          <input
            type="checkbox"
            id="snack"
            checked={visibleMeals.snack}
            onChange={() => toggleMealVisibility('snack')}
          />
          <label htmlFor="snack">Snack</label>
        </div>
      </div>
    </div>
  );
}

export default MealSettings;