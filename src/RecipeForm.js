import React, { useState } from 'react';
import './RecipeForm.css';

function RecipeForm({ addRecipe }) {
  const [name, setName] = useState('');
  const [ingredients, setIngredients] = useState('');
  const [instructions, setInstructions] = useState('');
  const [mealType, setMealType] = useState('dinner');

  const handleSubmit = (e) => {
    e.preventDefault();

    // Basic validation
    if (!name.trim()) {
      alert('Please enter a recipe name');
      return;
    }

    const newRecipe = {
      id: Date.now(), // Simple unique ID
      name,
      ingredients: ingredients.split(',').map(item => item.trim()),
      instructions,
      mealType
    };

    addRecipe(newRecipe);

    // Reset form
    setName('');
    setIngredients('');
    setInstructions('');
    setMealType('dinner');
  };

  return (
    <div className="recipe-form-container">
      <h2>Add New Recipe</h2>
      <form className="recipe-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="recipeName">Recipe Name</label>
          <input
            id="recipeName"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter recipe name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="mealType">Meal Type</label>
          <select
            id="mealType"
            value={mealType}
            onChange={(e) => setMealType(e.target.value)}
          >
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="ingredients">Ingredients</label>
          <textarea
            id="ingredients"
            value={ingredients}
            onChange={(e) => setIngredients(e.target.value)}
            placeholder="Enter ingredients (comma-separated)"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="instructions">Instructions</label>
          <textarea
            id="instructions"
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Enter cooking instructions"
            rows="4"
          />
        </div>

        <button type="submit" className="submit-btn">Add Recipe</button>
      </form>
    </div>
  );
}

export default RecipeForm;