import React, { useState, FormEvent, ChangeEvent } from 'react';
import { AxiosError } from 'axios';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  Grid,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import AuthLayout from './AuthLayout';
import { colors, radius, shadows, semantic } from '../../theme/tokens';
import type { RegisterRequest } from '../../types';

interface ApiErrorBody {
  error?: string;
}

type FormField = keyof RegisterRequest;

const SignUpPage = (): React.ReactElement | null => {
  const navigate = useNavigate();
  const { register, user, loading } = useAuth();

  const [form, setForm] = useState<RegisterRequest>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!loading && user) {
    navigate('/', { replace: true });
    return null;
  }

  const handleChange =
    (field: FormField) =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>): void =>
      setForm((previous) => ({ ...previous, [field]: event.target.value }));

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(form);
      navigate('/');
    } catch (caughtError) {
      const axiosError = caughtError as AxiosError<ApiErrorBody>;
      setError(axiosError.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start planning delicious meals for your family"
    >
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && (
            <Alert severity="error" sx={{ borderRadius: `${radius.r12}px` }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={1.5}>
            <Grid size={6}>
              <TextField
                label="First name"
                value={form.first_name}
                onChange={handleChange('first_name')}
                required
                fullWidth
                autoFocus
                autoComplete="given-name"
                sx={inputStyles}
              />
            </Grid>
            <Grid size={6}>
              <TextField
                label="Last name"
                value={form.last_name}
                onChange={handleChange('last_name')}
                required
                fullWidth
                autoComplete="family-name"
                sx={inputStyles}
              />
            </Grid>
          </Grid>

          <TextField
            label="Email"
            type="email"
            value={form.email}
            onChange={handleChange('email')}
            required
            fullWidth
            autoComplete="email"
            sx={inputStyles}
          />

          <TextField
            label="Password"
            type={showPassword ? 'text' : 'password'}
            value={form.password}
            onChange={handleChange('password')}
            required
            fullWidth
            autoComplete="new-password"
            sx={inputStyles}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword((previous) => !previous)}
                    edge="end"
                    size="small"
                  >
                    {showPassword ? (
                      <VisibilityOff fontSize="small" />
                    ) : (
                      <Visibility fontSize="small" />
                    )}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

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
            {submitting ? 'Creating account…' : 'Create account'}
          </Button>

          <Typography sx={{ textAlign: 'center', fontSize: 14, color: semantic.textSecondary }}>
            Already have an account?{' '}
            <Typography
              component={Link}
              to="/login"
              sx={{
                color: colors.green600,
                fontWeight: 600,
                textDecoration: 'none',
                '&:hover': { textDecoration: 'underline' },
              }}
            >
              Sign in
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

export default SignUpPage;
