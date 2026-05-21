import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Alert } from '@mui/material';
import { CheckCircleOutline } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { authAPI } from '../../services/api';
import AuthLayout from './AuthLayout';
import { colors, radius, shadows, semantic } from '../../theme/tokens';

const ForgotPasswordPage = () => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await authAPI.forgotPassword(email);
      setSent(true);
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (sent) {
    return (
      <AuthLayout title="Check your email">
        <Box sx={{ textAlign: 'center', py: 2 }}>
          <CheckCircleOutline sx={{ fontSize: 56, color: colors.green500, mb: 2 }} />
          <Typography sx={{ fontSize: 15, color: semantic.textSecondary, mb: 3, lineHeight: 1.6 }}>
            If <strong>{email}</strong> is registered, you'll receive a password reset link shortly.
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
            Back to sign in
          </Typography>
        </Box>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Forgot your password?"
      subtitle="Enter your email and we'll send you a reset link."
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
            {submitting ? 'Sending…' : 'Send reset link'}
          </Button>

          <Typography sx={{ textAlign: 'center', fontSize: 14, color: semantic.textSecondary }}>
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
              Back to sign in
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

export default ForgotPasswordPage;
