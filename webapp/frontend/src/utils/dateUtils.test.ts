import { describe, it, expect } from 'vitest'
import { formatRunDate } from './dateUtils'

describe('formatRunDate', () => {
  it('formats ISO timestamp to short month and day', () => {
    expect(formatRunDate('2026-03-27T02:18:08.737821+00:00')).toBe('Mar 27')
  })

  it('formats ISO timestamp with microseconds', () => {
    expect(formatRunDate('2026-03-31T11:09:38.884851+00:00')).toBe('Mar 31')
  })

  it('formats April date correctly', () => {
    expect(formatRunDate('2026-04-01T11:11:33.113454+00:00')).toBe('Apr 1')
  })

  it('returns empty string for empty input', () => {
    expect(formatRunDate('')).toBe('')
  })

  it('returns original string for invalid ISO', () => {
    expect(formatRunDate('not-a-date')).toBe('not-a-date')
  })
})
