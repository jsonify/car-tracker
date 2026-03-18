import { describe, it, expect } from 'vitest'
import { buildChartData, getCategoryColors } from './chartData'

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
