import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './components/auth/LoginPage';
import SignUpPage from './components/auth/SignUpPage';
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
        <AuthProvider>
          <Routes>
            {/* Public auth routes — no sidebar */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />

            {/* Protected app routes — with sidebar */}
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<MealPlansList />} />
                      <Route path="/meal-plan/:id" element={<MealPlanDetail />} />
                      <Route path="/foods" element={<FoodsManagement />} />
                      <Route path="/meal-settings" element={<MealSettingsPlaceholder />} />
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App;
