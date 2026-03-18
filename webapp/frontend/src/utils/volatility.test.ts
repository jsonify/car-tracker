import { describe, it, expect } from 'vitest'
import { rankVolatility } from './volatility'
import type { VolatileCategory } from '../api/client'

const makeCategory = (category: string, range: number): VolatileCategory => ({
  booking_name: 'test',
  category,
  min_price: 100,
  max_price: 100 + range,
  range,
})

describe('rankVolatility', () => {
  it('sorts categories descending by range', () => {
    const input = [
      makeCategory('Economy', 20),
      makeCategory('SUV', 80),
      makeCategory('Compact', 50),
    ]
    const result = rankVolatility(input)
    expect(result[0].category).toBe('SUV')
    expect(result[1].category).toBe('Compact')
    expect(result[2].category).toBe('Economy')
  })

  it('does not mutate the original array', () => {
    const input = [makeCategory('Economy', 20), makeCategory('SUV', 80)]
    rankVolatility(input)
    expect(input[0].category).toBe('Economy')
  })

  it('returns empty array for empty input', () => {
    expect(rankVolatility([])).toEqual([])
  })

  it('handles single element', () => {
    const input = [makeCategory('SUV', 40)]
    expect(rankVolatility(input)).toHaveLength(1)
  })
})
