import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff, CheckCircleOutline } from '@mui/icons-material';
import { Link, useSearchParams } from 'react-router-dom';
import { AuthService } from '../../services/AuthService';
import AuthLayout from './AuthLayout';
import { colors, radius, shadows, semantic } from '../../theme/tokens';

const authService = new AuthService();

const ResetPasswordPage = () => {
  const [searchParams] = useSearchParams();
  const uid = searchParams.get('uid') || '';
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!uid || !token) {
    return (
      <AuthLayout title="Invalid link">
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <Alert severity="error" sx={{ borderRadius: `${radius.r12}px`, mb: 2 }}>
            This password reset link is missing required parameters.
          </Alert>
          <Typography
            component={Link}
            to="/forgot-password"
            sx={{
              fontSize: 14,
              color: colors.green600,
              fontWeight: 600,
              textDecoration: 'none',
              '&:hover': { textDecoration: 'underline' },
            }}
          >
            Request a new reset link
          </Typography>
        </Box>
      </AuthLayout>
    );
  }

  if (done) {
    return (
      <AuthLayout title="Password updated">
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <CheckCircleOutline sx={{ fontSize: 56, color: colors.green500, mb: 2 }} />
          <Typography sx={{ fontSize: 15, color: semantic.textSecondary, mb: 3 }}>
            Your password has been updated. You can now sign in with your new password.
          </Typography>
          <Typography
            component={Link}
            to="/login"
            sx={{
              fontSize: 14,
              color: colors.green600,
              fontWeight: 600,
              textDecoration: 'none',
              '&:hover': { textDecoration: 'underline' },
            }}
          >
            Go to sign in
          </Typography>
        </Box>
      </AuthLayout>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await authService.resetPassword({ uid, token, password });
      setDone(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Set a new password" subtitle="Choose a strong password for your account.">
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {error && (
            <Alert severity="error" sx={{ borderRadius: `${radius.r12}px` }}>
              {error}
            </Alert>
          )}

          <TextField
            label="New password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            fullWidth
            autoFocus
            autoComplete="new-password"
            sx={inputStyles}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword((v) => !v)} edge="end" size="small">
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
            {submitting ? 'Updating…' : 'Update password'}
          </Button>
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

export default ResetPasswordPage;
