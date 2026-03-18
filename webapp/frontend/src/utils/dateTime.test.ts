import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { isExpired, formatDate, formatTime } from './dateTime'

describe('isExpired', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-03-18'))
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns true for past date', () => {
    expect(isExpired('2026-03-10')).toBe(true)
  })

  it('returns false for today', () => {
    expect(isExpired('2026-03-18')).toBe(false)
  })

  it('returns false for future date', () => {
    expect(isExpired('2026-04-01')).toBe(false)
  })
})

describe('formatDate', () => {
  it('formats a date string', () => {
    expect(formatDate('2026-04-02')).toBe('Apr 2, 2026')
  })

  it('formats beginning of year', () => {
    expect(formatDate('2026-01-01')).toBe('Jan 1, 2026')
  })

  it('formats end of year', () => {
    expect(formatDate('2026-12-31')).toBe('Dec 31, 2026')
  })
})

describe('formatTime', () => {
  it('formats morning time', () => {
    expect(formatTime('10:00')).toBe('10:00 AM')
  })

  it('formats noon', () => {
    expect(formatTime('12:00')).toBe('12:00 PM')
  })

  it('formats afternoon', () => {
    expect(formatTime('14:30')).toBe('2:30 PM')
  })

  it('formats midnight', () => {
    expect(formatTime('00:00')).toBe('12:00 AM')
  })

  it('formats 11 PM', () => {
    expect(formatTime('23:00')).toBe('11:00 PM')
  })
})
