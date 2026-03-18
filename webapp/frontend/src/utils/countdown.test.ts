import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { daysRemaining, urgencyVariant } from './countdown'

describe('daysRemaining', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-18'))
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns 0 for today', () => {
    expect(daysRemaining('2026-03-18')).toBe(0)
  })

  it('returns positive days for future date', () => {
    expect(daysRemaining('2026-03-25')).toBe(7)
  })

  it('returns negative days for past date', () => {
    expect(daysRemaining('2026-03-11')).toBe(-7)
  })

  it('returns 1 for tomorrow', () => {
    expect(daysRemaining('2026-03-19')).toBe(1)
  })
})

describe('urgencyVariant', () => {
  it('returns red for <= 7 days', () => {
    expect(urgencyVariant(0)).toBe('red')
    expect(urgencyVariant(7)).toBe('red')
    expect(urgencyVariant(-1)).toBe('red')
  })

  it('returns yellow for 8-30 days', () => {
    expect(urgencyVariant(8)).toBe('yellow')
    expect(urgencyVariant(30)).toBe('yellow')
  })

  it('returns green for > 30 days', () => {
    expect(urgencyVariant(31)).toBe('green')
    expect(urgencyVariant(100)).toBe('green')
  })
})
