import { describe, it, expect } from 'vitest'
import { formatCurrency, toggleSort } from './tableUtils'

describe('formatCurrency', () => {
  it('formats whole numbers', () => {
    expect(formatCurrency(299)).toBe('$299.00')
  })

  it('formats decimals', () => {
    expect(formatCurrency(299.5)).toBe('$299.50')
    expect(formatCurrency(299.99)).toBe('$299.99')
  })

  it('formats zero', () => {
    expect(formatCurrency(0)).toBe('$0.00')
  })

  it('formats large numbers', () => {
    expect(formatCurrency(1234.56)).toBe('$1234.56')
  })
})

describe('toggleSort', () => {
  it('toggles order on same column from asc to desc', () => {
    expect(toggleSort('name', 'name', 'asc')).toEqual({ sort: 'name', order: 'desc' })
  })

  it('toggles order on same column from desc to asc', () => {
    expect(toggleSort('name', 'name', 'desc')).toEqual({ sort: 'name', order: 'asc' })
  })

  it('resets to asc when switching columns', () => {
    expect(toggleSort('name', 'price', 'desc')).toEqual({ sort: 'price', order: 'asc' })
  })

  it('sets asc for new column regardless of current order', () => {
    expect(toggleSort('date', 'brand', 'asc')).toEqual({ sort: 'brand', order: 'asc' })
  })
})
