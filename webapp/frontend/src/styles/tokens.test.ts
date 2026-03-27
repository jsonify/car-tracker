import { colors, fonts, elevation, chartColors, trendColors } from './tokens';

describe('Velocity Dark tokens', () => {
  describe('colors', () => {
    it('defines primary as amber', () => {
      expect(colors.primary).toBe('#fe9821');
    });

    it('defines primary-container as darker amber', () => {
      expect(colors.primaryContainer).toBe('#ea8908');
    });

    it('defines secondary as violet', () => {
      expect(colors.secondary).toBe('#a68cff');
    });

    it('defines tertiary as cyan', () => {
      expect(colors.tertiary).toBe('#81ecff');
    });

    it('defines error as coral', () => {
      expect(colors.error).toBe('#ff7351');
    });

    it('defines surface as deep obsidian', () => {
      expect(colors.surface).toBe('#0e0d14');
    });

    it('defines all surface container tiers', () => {
      expect(colors.surfaceContainer).toBe('#1a1921');
      expect(colors.surfaceContainerHigh).toBe('#201e28');
      expect(colors.surfaceContainerHighest).toBe('#26252f');
    });

    it('defines on-surface text colors', () => {
      expect(colors.onSurface).toBe('#f4eff9');
      expect(colors.onSurfaceVariant).toBe('#ada9b3');
    });
  });

  describe('fonts', () => {
    it('uses Manrope for headlines', () => {
      expect(fonts.headline).toContain('Manrope');
    });

    it('uses Inter for body', () => {
      expect(fonts.body).toContain('Inter');
    });
  });

  describe('elevation', () => {
    it('maps levels to surface tiers', () => {
      expect(elevation.level0).toBe(colors.surface);
      expect(elevation.level1).toBe(colors.surfaceContainer);
      expect(elevation.level2).toBe(colors.surfaceContainerHigh);
      expect(elevation.level3).toBe(colors.surfaceContainerHighest);
    });
  });

  describe('chartColors', () => {
    it('starts with primary, secondary, tertiary, error', () => {
      expect(chartColors[0]).toBe(colors.primary);
      expect(chartColors[1]).toBe(colors.secondary);
      expect(chartColors[2]).toBe(colors.tertiary);
      expect(chartColors[3]).toBe(colors.error);
    });

    it('has at least 8 colors for chart series', () => {
      expect(chartColors.length).toBeGreaterThanOrEqual(8);
    });
  });

  describe('trendColors', () => {
    it('uses tertiary for positive', () => {
      expect(trendColors.positive).toBe(colors.tertiary);
    });

    it('uses error for negative', () => {
      expect(trendColors.negative).toBe(colors.error);
    });

    it('uses on-surface-variant for neutral', () => {
      expect(trendColors.neutral).toBe(colors.onSurfaceVariant);
    });
  });
});
