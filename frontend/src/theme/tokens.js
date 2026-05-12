export const colors = {
  green50: '#F0FDF4',
  green100: '#DCFCE7',
  green500: '#22C55E',
  green600: '#16A34A',
  yellow100: '#FEF3C7',
  yellow400: '#FBBF24',
  orange400: '#FB923C',
  white: '#FFFFFF',
  gray50: '#F9FAFB',
  gray100: '#F3F4F6',
  gray200: '#E5E7EB',
  gray400: '#9CA3AF',
  gray600: '#4B5563',
  gray900: '#111827',
};

export const semantic = {
  bgApp: '#F9FAF7',
  bgSidebar: colors.white,
  bgCard: colors.white,
  textPrimary: colors.gray900,
  textSecondary: colors.gray600,
  textMuted: colors.gray400,
  borderDefault: colors.gray200,
  accentPrimary: colors.green500,
};

export const spacing = [4, 8, 12, 16, 20, 24, 32, 48];

export const radius = {
  r8: 8,
  r12: 12,
  r16: 16,
  r24: 24,
  full: 9999,
};

export const shadows = {
  buttonGlow: '0 6px 16px rgba(34, 197, 94, 0.35)',
  cardLift: '0 4px 24px rgba(17, 24, 39, 0.06)',
  ctaGlow: '0 8px 20px rgba(34, 197, 94, 0.4)',
};

export const fontFamily = '"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

export const typography = {
  display: { weight: 800, size: 32, lineHeight: 1.2 },
  h1: { weight: 800, size: 24, lineHeight: 1.25 },
  h2: { weight: 700, size: 20, lineHeight: 1.3 },
  bodyLarge: { weight: 500, size: 16, lineHeight: 1.5 },
  body: { weight: 400, size: 14, lineHeight: 1.5 },
  caption: { weight: 400, size: 13, lineHeight: 1.4 },
  label: { weight: 600, size: 10, lineHeight: 1.2, letterSpacing: '0.08em', textTransform: 'uppercase' },
};
