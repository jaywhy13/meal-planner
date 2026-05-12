import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import MealPlansList from './components/MealPlansList';
import MealPlanDetail from './components/MealPlanDetail';
import FoodsManagement from './components/FoodsManagement';
import MealSettingsPlaceholder from './components/MealSettingsPlaceholder';
import Layout from './components/layout/Layout';
import theme from './theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<MealPlansList />} />
            <Route path="/meal-plan/:id" element={<MealPlanDetail />} />
            <Route path="/foods" element={<FoodsManagement />} />
            <Route path="/meal-settings" element={<MealSettingsPlaceholder />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
