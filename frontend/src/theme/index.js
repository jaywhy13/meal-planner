import { createTheme } from '@mui/material/styles';
import {
  colors,
  semantic,
  radius,
  shadows,
  fontFamily,
  typography as t,
} from './tokens';

const theme = createTheme({
  palette: {
    primary: {
      light: colors.green100,
      main: colors.green500,
      dark: colors.green600,
      contrastText: colors.white,
    },
    secondary: {
      light: colors.yellow100,
      main: colors.yellow400,
      dark: colors.orange400,
      contrastText: colors.gray900,
    },
    background: {
      default: semantic.bgApp,
      paper: semantic.bgCard,
    },
    text: {
      primary: semantic.textPrimary,
      secondary: semantic.textSecondary,
      disabled: semantic.textMuted,
    },
    divider: semantic.borderDefault,
  },

  shape: {
    borderRadius: radius.r12,
  },

  typography: {
    fontFamily,
    h1: { fontWeight: t.display.weight, fontSize: t.display.size, lineHeight: t.display.lineHeight },
    h2: { fontWeight: t.h1.weight, fontSize: t.h1.size, lineHeight: t.h1.lineHeight },
    h3: { fontWeight: t.h2.weight, fontSize: t.h2.size, lineHeight: t.h2.lineHeight },
    body1: { fontWeight: t.bodyLarge.weight, fontSize: t.bodyLarge.size, lineHeight: t.bodyLarge.lineHeight },
    body2: { fontWeight: t.body.weight, fontSize: t.body.size, lineHeight: t.body.lineHeight },
    caption: { fontWeight: t.caption.weight, fontSize: t.caption.size, lineHeight: t.caption.lineHeight },
    overline: {
      fontWeight: t.label.weight,
      fontSize: t.label.size,
      lineHeight: t.label.lineHeight,
      letterSpacing: t.label.letterSpacing,
      textTransform: t.label.textTransform,
    },
    button: { textTransform: 'none', fontWeight: 600 },
  },

  customShadows: shadows,

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: semantic.bgApp,
          color: semantic.textPrimary,
        },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: radius.r12 },
        containedPrimary: {
          boxShadow: shadows.buttonGlow,
          '&:hover': { boxShadow: shadows.buttonGlow },
        },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          borderRadius: radius.r16,
          boxShadow: shadows.cardLift,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        rounded: { borderRadius: radius.r16 },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: radius.full },
      },
    },
  },
});

export default theme;
