import React, { useState } from 'react';
import './RecipeList.css';

function RecipeList({ recipes, assignRecipeToMeal }) {
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [showDaySelector, setShowDaySelector] = useState(false);
  const [mealType, setMealType] = useState('');

  const handleRecipeClick = (recipe) => {
    setSelectedRecipe(recipe);
  };

  const handleAddToMealPlan = (recipe) => {
    setSelectedRecipe(recipe);
    setMealType(recipe.mealType);
    setShowDaySelector(true);
  };

  const handleDaySelection = (day) => {
    assignRecipeToMeal(selectedRecipe, mealType, day);
    setShowDaySelector(false);
    setSelectedRecipe(null);
  };

  const filterRecipes = (type) => {
    return recipes.filter(recipe => recipe.mealType === type);
  };

  return (
    <div className="recipe-list-container">
      <h2>Your Recipes</h2>

      {/* Show day selector when a recipe is selected */}
      {showDaySelector && (
        <div className="day-selector">
          <h3>Select Day for {selectedRecipe.name}</h3>
          <div className="buttons-container">
            <button onClick={() => handleDaySelection(1)}>Monday</button>
            <button onClick={() => handleDaySelection(2)}>Tuesday</button>
            <button onClick={() => handleDaySelection(3)}>Wednesday</button>
            <button onClick={() => handleDaySelection(4)}>Thursday</button>
            <button onClick={() => handleDaySelection(5)}>Friday</button>
          </div>
          <button className="cancel-btn" onClick={() => setShowDaySelector(false)}>Cancel</button>
        </div>
      )}

      {/* Recipe list by meal type */}
      <div className="recipe-categories">
        <div className="recipe-category">
          <h3>Breakfast</h3>
          {filterRecipes('breakfast').length > 0 ? (
            <ul className="recipe-items">
              {filterRecipes('breakfast').map(recipe => (
                <li key={recipe.id} className="recipe-item">
                  <span onClick={() => handleRecipeClick(recipe)}>{recipe.name}</span>
                  <button onClick={() => handleAddToMealPlan(recipe)}>Add to Plan</button>
                </li>
              ))}
            </ul>
          ) : (
            <p>No breakfast recipes added yet.</p>
          )}
        </div>

        <div className="recipe-category">
          <h3>Lunch</h3>
          {filterRecipes('lunch').length > 0 ? (
            <ul className="recipe-items">
              {filterRecipes('lunch').map(recipe => (
                <li key={recipe.id} className="recipe-item">
                  <span onClick={() => handleRecipeClick(recipe)}>{recipe.name}</span>
                  <button onClick={() => handleAddToMealPlan(recipe)}>Add to Plan</button>
                </li>
              ))}
            </ul>
          ) : (
            <p>No lunch recipes added yet.</p>
          )}
        </div>

        <div className="recipe-category">
          <h3>Dinner</h3>
          {filterRecipes('dinner').length > 0 ? (
            <ul className="recipe-items">
              {filterRecipes('dinner').map(recipe => (
                <li key={recipe.id} className="recipe-item">
                  <span onClick={() => handleRecipeClick(recipe)}>{recipe.name}</span>
                  <button onClick={() => handleAddToMealPlan(recipe)}>Add to Plan</button>
                </li>
              ))}
            </ul>
          ) : (
            <p>No dinner recipes added yet.</p>
          )}
        </div>

        <div className="recipe-category">
          <h3>Snacks</h3>
          {filterRecipes('snack').length > 0 ? (
            <ul className="recipe-items">
              {filterRecipes('snack').map(recipe => (
                <li key={recipe.id} className="recipe-item">
                  <span onClick={() => handleRecipeClick(recipe)}>{recipe.name}</span>
                  <button onClick={() => handleAddToMealPlan(recipe)}>Add to Plan</button>
                </li>
              ))}
            </ul>
          ) : (
            <p>No snack recipes added yet.</p>
          )}
        </div>
      </div>

      {/* Recipe detail view */}
      {selectedRecipe && !showDaySelector && (
        <div className="recipe-detail">
          <h3>{selectedRecipe.name}</h3>
          <p><strong>Meal Type:</strong> {selectedRecipe.mealType.charAt(0).toUpperCase() + selectedRecipe.mealType.slice(1)}</p>

          <h4>Ingredients:</h4>
          <ul>
            {selectedRecipe.ingredients.map((ingredient, index) => (
              <li key={index}>{ingredient}</li>
            ))}
          </ul>

          <h4>Instructions:</h4>
          <p>{selectedRecipe.instructions}</p>

          <div className="recipe-actions">
            <button onClick={() => handleAddToMealPlan(selectedRecipe)}>Add to Meal Plan</button>
            <button onClick={() => setSelectedRecipe(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecipeList;