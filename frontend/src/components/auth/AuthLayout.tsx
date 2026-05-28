import React, { ReactNode } from 'react';
import { Box, Typography } from '@mui/material';
import { RestaurantMenu } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { colors, semantic, radius, shadows, fontFamily } from '../../theme/tokens';

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

const AuthLayout = ({ children, title, subtitle }: AuthLayoutProps): React.ReactElement => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: semantic.bgApp,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 3,
        fontFamily,
      }}
    >
      <Box
        onClick={() => navigate('/')}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          mb: 4,
          cursor: 'pointer',
        }}
      >
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: `${radius.r12}px`,
            bgcolor: colors.green500,
            color: colors.white,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            '& svg': { fontSize: 22 },
          }}
        >
          <RestaurantMenu />
        </Box>
        <Typography sx={{ fontSize: 20, fontWeight: 800, color: semantic.textPrimary }}>
          Meal Planner
        </Typography>
      </Box>

      <Box
        sx={{
          width: '100%',
          maxWidth: 440,
          bgcolor: colors.white,
          borderRadius: `${radius.r24}px`,
          boxShadow: shadows.cardLift,
          p: { xs: 3, sm: 4 },
        }}
      >
        <Typography
          sx={{
            fontSize: 26,
            fontWeight: 800,
            color: semantic.textPrimary,
            mb: 0.75,
            lineHeight: 1.2,
          }}
        >
          {title}
        </Typography>
        {subtitle && (
          <Typography
            sx={{
              fontSize: 14,
              color: semantic.textSecondary,
              mb: 3,
              lineHeight: 1.5,
            }}
          >
            {subtitle}
          </Typography>
        )}
        {children}
      </Box>
    </Box>
  );
};

export default AuthLayout;
