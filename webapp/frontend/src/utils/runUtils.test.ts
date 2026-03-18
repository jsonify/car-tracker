import { describe, it, expect } from 'vitest'
import { isHoldingRun, isHoldingVehicle } from './runUtils'
import type { RunSummary } from '../api/client'

const makeRun = (holding_price: number | null): RunSummary => ({
  id: 1,
  run_at: '2026-03-18T10:00:00',
  pickup_location: 'LAX',
  pickup_date: '2026-04-01',
  dropoff_date: '2026-04-08',
  booking_name: 'test',
  holding_price,
  holding_vehicle_type: null,
  vehicle_count: 5,
})

describe('isHoldingRun', () => {
  it('returns true when holding_price is set', () => {
    expect(isHoldingRun(makeRun(299))).toBe(true)
  })

  it('returns false when holding_price is null', () => {
    expect(isHoldingRun(makeRun(null))).toBe(false)
  })

  it('returns true for holding_price of 0', () => {
    expect(isHoldingRun(makeRun(0))).toBe(true)
  })
})

describe('isHoldingVehicle', () => {
  it('returns true when vehicle name matches holding type', () => {
    expect(isHoldingVehicle('Economy Car', 'Economy Car')).toBe(true)
  })

  it('returns false when vehicle name does not match', () => {
    expect(isHoldingVehicle('SUV', 'Economy Car')).toBe(false)
  })

  it('returns false when holding type is null', () => {
    expect(isHoldingVehicle('Economy Car', null)).toBe(false)
  })

  it('is case-sensitive', () => {
    expect(isHoldingVehicle('economy car', 'Economy Car')).toBe(false)
  })
})
