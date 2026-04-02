import { describe, it, expect } from 'vitest'
import {
  buildChartData,
  getCategoryColors,
  buildPriceRangeData,
  buildLatestPricesData,
  buildPriceChangeData,
  buildHoldingComparisonData,
} from './chartData'

describe('buildChartData', () => {
  it('builds chart data from run dates and categories', () => {
    const runDates = ['2026-03-01', '2026-03-02']
    const categories = { Economy: [100, 110], SUV: [200, 220] }
    const result = buildChartData(runDates, categories)
    expect(result).toHaveLength(2)
    expect(result[0]).toEqual({ date: '2026-03-01', Economy: 100, SUV: 200 })
    expect(result[1]).toEqual({ date: '2026-03-02', Economy: 110, SUV: 220 })
  })

  it('returns empty array for no dates', () => {
    expect(buildChartData([], {})).toEqual([])
  })

  it('handles missing price index gracefully', () => {
    const runDates = ['2026-03-01', '2026-03-02']
    const categories = { Economy: [100] } // only one price
    const result = buildChartData(runDates, categories)
    expect(result[1].Economy).toBe(0)
  })
})

describe('getCategoryColors', () => {
  it('assigns a color to each category', () => {
    const colors = getCategoryColors(['Economy', 'SUV'])
    expect(colors['Economy']).toBe('#818cf8')
    expect(colors['SUV']).toBe('#34d399')
  })

  it('wraps around color palette when more categories than colors', () => {
    const cats = Array.from({ length: 9 }, (_, i) => `Cat${i}`)
    const colors = getCategoryColors(cats)
    expect(colors['Cat8']).toBe('#818cf8') // wraps to index 0
  })

  it('returns empty object for empty categories', () => {
    expect(getCategoryColors([])).toEqual({})
  })
})

describe('buildPriceRangeData', () => {
  const categories = {
    Economy: [200, 220, 190, 210],
    SUV: [350, 340, 360],
  }

  it('returns min, max, and range for each visible category', () => {
    const result = buildPriceRangeData(categories, ['Economy', 'SUV'])
    expect(result).toHaveLength(2)
    const eco = result.find((r) => r.category === 'Economy')!
    expect(eco.min).toBe(190)
    expect(eco.max).toBe(220)
    expect(eco.range).toBe(30)
  })

  it('only includes visible categories', () => {
    const result = buildPriceRangeData(categories, ['Economy'])
    expect(result).toHaveLength(1)
    expect(result[0].category).toBe('Economy')
  })

  it('handles single data point (min === max)', () => {
    const result = buildPriceRangeData({ Economy: [250] }, ['Economy'])
    expect(result[0].min).toBe(250)
    expect(result[0].max).toBe(250)
    expect(result[0].range).toBe(0)
  })

  it('skips categories with no data', () => {
    const result = buildPriceRangeData({ Economy: [] }, ['Economy'])
    expect(result).toHaveLength(0)
  })

  it('returns empty array when visibleCats is empty', () => {
    expect(buildPriceRangeData(categories, [])).toEqual([])
  })
})

describe('buildLatestPricesData', () => {
  const categories = {
    Economy: [200, 220, 180],
    SUV: [350, 340, 360],
    Compact: [250, 260, 240],
  }

  it('returns latest price for each visible category', () => {
    const result = buildLatestPricesData(categories, ['Economy'])
    expect(result[0].price).toBe(180)
  })

  it('sorts results cheapest first', () => {
    const result = buildLatestPricesData(categories, ['Economy', 'SUV', 'Compact'])
    expect(result.map((r) => r.price)).toEqual([180, 240, 360])
  })

  it('skips categories with no data', () => {
    const result = buildLatestPricesData({ Economy: [] }, ['Economy'])
    expect(result).toHaveLength(0)
  })

  it('returns empty array when visibleCats is empty', () => {
    expect(buildLatestPricesData(categories, [])).toEqual([])
  })
})

describe('buildPriceChangeData', () => {
  const categories = {
    Economy: [200, 210, 180],   // dropped 20
    SUV: [350, 360, 370],       // rose 20
    Compact: [250, 250, 250],   // unchanged
  }

  it('returns delta from first to latest price', () => {
    const result = buildPriceChangeData(categories, ['Economy'])
    expect(result[0].delta).toBe(-20)
  })

  it('returns positive delta for price increases', () => {
    const result = buildPriceChangeData(categories, ['SUV'])
    expect(result[0].delta).toBe(20)
  })

  it('returns zero delta for unchanged price', () => {
    const result = buildPriceChangeData(categories, ['Compact'])
    expect(result[0].delta).toBe(0)
    expect(result[0].pctChange).toBe(0)
  })

  it('calculates percentage change correctly', () => {
    const result = buildPriceChangeData(categories, ['Economy'])
    expect(result[0].pctChange).toBeCloseTo(-10, 1)
  })

  it('handles single data point (no change)', () => {
    const result = buildPriceChangeData({ Economy: [300] }, ['Economy'])
    expect(result[0].delta).toBe(0)
    expect(result[0].pctChange).toBe(0)
  })

  it('skips categories with no data', () => {
    expect(buildPriceChangeData({ Economy: [] }, ['Economy'])).toHaveLength(0)
  })
})

describe('buildHoldingComparisonData', () => {
  const categories = { 'Economy Car': [300, 290, 280] }

  it('returns holdingPrice and currentBest when configured', () => {
    const result = buildHoldingComparisonData(350, 'Economy Car', categories)
    expect(result).not.toBeNull()
    expect(result!.holdingPrice).toBe(350)
    expect(result!.currentBest).toBe(280)
  })

  it('returns null when holdingPrice is null', () => {
    expect(buildHoldingComparisonData(null, 'Economy Car', categories)).toBeNull()
  })

  it('returns null when holdingVehicleType is null', () => {
    expect(buildHoldingComparisonData(350, null, categories)).toBeNull()
  })

  it('returns null when holding vehicle type not in categories', () => {
    expect(buildHoldingComparisonData(350, 'Nonexistent', categories)).toBeNull()
  })

  it('returns null when holding vehicle type has no price data', () => {
    expect(buildHoldingComparisonData(350, 'Economy Car', { 'Economy Car': [] })).toBeNull()
  })
})
