import React, { useState } from 'react';
import './App.css';
import MealPlan from './MealPlan';
import RecipeForm from './RecipeForm';
import RecipeList from './RecipeList';
import MealSettings from './MealSettings';

function App() {
  const [currentWeek, setCurrentWeek] = useState(1);
  const [recipes, setRecipes] = useState([]);
  const [mealPlan, setMealPlan] = useState({});
  const [visibleMeals, setVisibleMeals] = useState({
    breakfast: true,
    lunch: true,
    dinner: true,
    snack: true
  });

  // Helper to generate week identifier
  const getWeekKey = (week) => `week${week}`;

  const addRecipe = (recipe) => {
    setRecipes([...recipes, recipe]);
  };

  const assignRecipeToMeal = (recipe, mealType, day) => {
    const weekKey = getWeekKey(currentWeek);
    const dayKey = `day${day}`;
    
    setMealPlan(prevPlan => {
      // Initialize the structure if it doesn't exist
      const newPlan = { ...prevPlan };
      
      if (!newPlan[weekKey]) {
        newPlan[weekKey] = {};
      }
      
      if (!newPlan[weekKey][dayKey]) {
        newPlan[weekKey][dayKey] = {};
      }
      
      // Assign the recipe to the specified meal
      newPlan[weekKey][dayKey][mealType] = recipe;
      
      return newPlan;
    });
  };

  const changeWeek = (weekNumber) => {
    if (weekNumber >= 1 && weekNumber <= 4) {
      setCurrentWeek(weekNumber);
    }
  };

  const weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  return (
    <div className="app">
      <h1>Meal Planner</h1>
      
      <div className="week-navigation">
        <button 
          onClick={() => changeWeek(1)}
          className={currentWeek === 1 ? 'active' : ''}
        >
          Week 1
        </button>
        <button 
          onClick={() => changeWeek(2)}
          className={currentWeek === 2 ? 'active' : ''}
        >
          Week 2
        </button>
        <button 
          onClick={() => changeWeek(3)}
          className={currentWeek === 3 ? 'active' : ''}
        >
          Week 3
        </button>
        <button 
          onClick={() => changeWeek(4)}
          className={currentWeek === 4 ? 'active' : ''}
        >
          Week 4
        </button>
      </div>
      
      <MealSettings visibleMeals={visibleMeals} setVisibleMeals={setVisibleMeals} />
      
      <div className="main-content">
        <div className="left-panel">
          <RecipeForm addRecipe={addRecipe} />
          <RecipeList 
            recipes={recipes} 
            assignRecipeToMeal={assignRecipeToMeal} 
          />
        </div>
        <div className="right-panel">
          <MealPlan 
            weekNumber={currentWeek}
            weekDays={weekDays}
            mealPlan={mealPlan[getWeekKey(currentWeek)] || {}}
            assignRecipeToMeal={assignRecipeToMeal}
            visibleMeals={visibleMeals}
          />
        </div>
      </div>
    </div>
  );
}

export default App;