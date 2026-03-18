import { describe, it, expect } from 'vitest'
import { findBestRun, computeSavings } from './insights'

describe('findBestRun', () => {
  it('finds the run with the lowest price', () => {
    const dates = ['2026-03-01', '2026-03-02', '2026-03-03']
    const prices = [300, 250, 280]
    expect(findBestRun(dates, prices)).toEqual({ date: '2026-03-02', price: 250 })
  })

  it('returns null for empty arrays', () => {
    expect(findBestRun([], [])).toBeNull()
    expect(findBestRun(['2026-03-01'], [])).toBeNull()
  })

  it('returns the only element for single-element arrays', () => {
    expect(findBestRun(['2026-03-01'], [100])).toEqual({ date: '2026-03-01', price: 100 })
  })

  it('handles tie by returning first occurrence', () => {
    const dates = ['2026-03-01', '2026-03-02']
    const prices = [100, 100]
    expect(findBestRun(dates, prices)).toEqual({ date: '2026-03-01', price: 100 })
  })
})

describe('computeSavings', () => {
  it('returns positive savings when holding price > current best', () => {
    expect(computeSavings(300, 250)).toBe(50)
  })

  it('returns negative savings when holding price < current best', () => {
    expect(computeSavings(200, 250)).toBe(-50)
  })

  it('returns zero when prices are equal', () => {
    expect(computeSavings(200, 200)).toBe(0)
  })

  it('returns null when either value is null', () => {
    expect(computeSavings(null, 200)).toBeNull()
    expect(computeSavings(200, null)).toBeNull()
    expect(computeSavings(null, null)).toBeNull()
  })
})
