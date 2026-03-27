/**
 * Velocity Dark Design System — Token Reference
 *
 * These values mirror the @theme tokens in index.css.
 * Use these when you need design system values in JS/TS
 * (e.g., Recharts colors, dynamic styles).
 */

export const colors = {
  primary: '#fe9821',
  primaryContainer: '#ea8908',
  secondary: '#a68cff',
  tertiary: '#81ecff',
  error: '#ff7351',

  surface: '#0e0d14',
  surfaceContainer: '#1a1921',
  surfaceContainerHigh: '#201e28',
  surfaceContainerHighest: '#26252f',

  onSurface: '#f4eff9',
  onSurfaceVariant: '#ada9b3',
  outlineVariant: '#3d3a45',
} as const;

export const fonts = {
  headline: '"Manrope", system-ui, sans-serif',
  body: '"Inter", system-ui, sans-serif',
} as const;

export const elevation = {
  /** Base surface — deepest layer */
  level0: colors.surface,
  /** Cards, containers */
  level1: colors.surfaceContainer,
  /** Hover states, raised cards */
  level2: colors.surfaceContainerHigh,
  /** Active states, modals */
  level3: colors.surfaceContainerHighest,
} as const;

/**
 * Chart color palette for Recharts series.
 * Order: primary, secondary, tertiary, error, then muted variants.
 */
export const chartColors = [
  colors.primary,
  colors.secondary,
  colors.tertiary,
  colors.error,
  '#d4a052', // muted gold
  '#7cb3c4', // muted teal
  '#c49bff', // light violet
  '#ffab7a', // light coral
] as const;

/**
 * Trend colors for positive/negative indicators.
 */
export const trendColors = {
  positive: colors.tertiary,
  negative: colors.error,
  neutral: colors.onSurfaceVariant,
} as const;
