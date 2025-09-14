import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import MealPlansList from './components/MealPlansList';
import MealPlanDetail from './components/MealPlanDetail';
import FoodsManagement from './components/FoodsManagement';
import Navbar from './components/Navbar';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2e7d32',
    },
    secondary: {
      main: '#ff6f00',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            <Route path="/" element={<MealPlansList />} />
            <Route path="/meal-plan/:id" element={<MealPlanDetail />} />
            <Route path="/foods" element={<FoodsManagement />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
