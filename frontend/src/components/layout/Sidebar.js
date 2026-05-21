import React from 'react';
import { Box, Typography, Avatar, IconButton, Tooltip } from '@mui/material';
import { RestaurantMenu, LogoutOutlined } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { colors, semantic, radius } from '../../theme/tokens';

const SIDEBAR_WIDTH = 240;

const NAV_ITEMS = [
  { label: 'Meal Plans', path: '/', emoji: '📅' },
  { label: 'Foods', path: '/foods', emoji: '🥦' },
  { label: 'Meal Settings', path: '/meal-settings', emoji: '⚙️' },
];

const IconBox = ({ active, children }) => (
  <Box
    sx={{
      width: 28,
      height: 28,
      borderRadius: `${radius.r8}px`,
      bgcolor: active ? colors.green500 : colors.gray100,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
      fontSize: 14,
      filter: active ? 'none' : 'grayscale(0.2)',
    }}
  >
    {children}
  </Box>
);

const NavItem = ({ item, active, onClick }) => {
  return (
    <Box
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') onClick();
      }}
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1.5,
        px: 1.5,
        py: 1.25,
        mx: 1,
        borderRadius: `${radius.r12}px`,
        bgcolor: active ? colors.green100 : 'transparent',
        cursor: 'pointer',
        transition: 'background-color 120ms ease',
        '&:hover': {
          bgcolor: active ? colors.green100 : colors.gray50,
        },
      }}
    >
      <IconBox active={active}>{item.emoji}</IconBox>
      <Typography
        sx={{
          fontSize: 14,
          fontWeight: active ? 600 : 500,
          color: active ? colors.green600 : semantic.textSecondary,
        }}
      >
        {item.label}
      </Typography>
    </Box>
  );
};

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <Box
      component="aside"
      sx={{
        width: SIDEBAR_WIDTH,
        flexShrink: 0,
        bgcolor: semantic.bgSidebar,
        borderRight: `1px solid ${semantic.borderDefault}`,
        height: '100vh',
        position: 'sticky',
        top: 0,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box
        onClick={() => navigate('/')}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          px: 2,
          py: 2.5,
          cursor: 'pointer',
        }}
      >
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: `${radius.r12}px`,
            bgcolor: colors.green500,
            color: colors.white,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            '& svg': { fontSize: 20 },
          }}
        >
          <RestaurantMenu />
        </Box>
        <Typography sx={{ fontSize: 18, fontWeight: 800, color: semantic.textPrimary }}>
          Meal Planner
        </Typography>
      </Box>

      <Typography
        variant="overline"
        sx={{ color: semantic.textMuted, px: 2.5, mt: 1, mb: 1, display: 'block' }}
      >
        Main Menu
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {NAV_ITEMS.map((item) => (
          <NavItem
            key={item.path}
            item={item}
            active={isActive(item.path)}
            onClick={() => navigate(item.path)}
          />
        ))}
      </Box>

      <Box sx={{ flexGrow: 1 }} />

      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          px: 2,
          py: 2,
          borderTop: `1px solid ${semantic.borderDefault}`,
        }}
      >
        <Avatar
          sx={{
            width: 36,
            height: 36,
            bgcolor: colors.green500,
            color: colors.white,
            fontSize: 14,
            fontWeight: 700,
            flexShrink: 0,
          }}
        >
          {user?.first_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || '?'}
        </Avatar>
        <Box sx={{ minWidth: 0, flexGrow: 1 }}>
          <Typography
            sx={{
              fontSize: 14,
              fontWeight: 600,
              color: semantic.textPrimary,
              lineHeight: 1.2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {user?.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user?.email}
          </Typography>
          <Typography
            sx={{
              fontSize: 12,
              color: semantic.textMuted,
              lineHeight: 1.2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {user?.email}
          </Typography>
        </Box>
        <Tooltip title="Sign out">
          <IconButton
            size="small"
            onClick={logout}
            sx={{ color: semantic.textMuted, '&:hover': { color: semantic.textSecondary } }}
          >
            <LogoutOutlined fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Sidebar;
export { SIDEBAR_WIDTH };
