import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert, InputAdornment, IconButton } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import AuthLayout from './AuthLayout';
import { colors, radius, shadows, semantic } from '../../theme/tokens';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, user, loading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) {
    navigate('/', { replace: true });
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your meal planner account"
    >
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && <Alert severity="error" sx={{ borderRadius: `${radius.r12}px` }}>{error}</Alert>}

          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            fullWidth
            autoFocus
            autoComplete="email"
            sx={inputStyles}
          />

          <TextField
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            fullWidth
            autoComplete="current-password"
            sx={inputStyles}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword((v) => !v)} edge="end" size="small">
                    {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Box sx={{ textAlign: 'right', mt: -1 }}>
            <Typography
              component={Link}
              to="/forgot-password"
              sx={{
                fontSize: 13,
                color: colors.green600,
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
              }}
            >
              Forgot password?
            </Typography>
          </Box>

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={submitting}
            sx={{
              bgcolor: colors.green500,
              color: colors.white,
              fontWeight: 700,
              fontSize: 15,
              py: 1.5,
              borderRadius: `${radius.r12}px`,
              boxShadow: shadows.buttonGlow,
              textTransform: 'none',
              '&:hover': { bgcolor: colors.green600 },
              '&:disabled': { opacity: 0.7 },
            }}
          >
            {submitting ? 'Signing in…' : 'Sign in'}
          </Button>

          <Typography sx={{ textAlign: 'center', fontSize: 14, color: semantic.textSecondary }}>
            Don't have an account?{' '}
            <Typography
              component={Link}
              to="/signup"
              sx={{
                color: colors.green600,
                fontWeight: 600,
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
              }}
            >
              Sign up
            </Typography>
          </Typography>
        </Box>
      </form>
    </AuthLayout>
  );
};

const inputStyles = {
  '& .MuiOutlinedInput-root': {
    borderRadius: `${radius.r12}px`,
    '&.Mui-focused fieldset': { borderColor: colors.green500 },
  },
  '& label.Mui-focused': { color: colors.green600 },
};

export default LoginPage;
