import { describe, it, expect, vi, beforeEach } from 'vitest'
import api, {
  getBookings,
  createBooking,
  getRuns,
  getPriceHistory,
  getDashboardSummary,
  getSavings,
  getVolatility,
  getAlertSettings,
  updateAlertSettings,
} from './client'
import type { Booking, AlertConfig } from './client'

// Mock axios instance methods
vi.spyOn(api, 'get').mockResolvedValue({ data: [] })
vi.spyOn(api, 'post').mockResolvedValue({ data: {} })
vi.spyOn(api, 'put').mockResolvedValue({ data: {} })
vi.spyOn(api, 'delete').mockResolvedValue({ data: {} })

beforeEach(() => {
  vi.clearAllMocks()
})

describe('existing API calls', () => {
  it('getBookings calls GET /bookings/', async () => {
    await getBookings()
    expect(api.get).toHaveBeenCalledWith('/bookings/')
  })

  it('createBooking calls POST /bookings/', async () => {
    const booking = {
      name: 'test',
      pickup_location: 'SFO',
      pickup_date: '2026-04-01',
      pickup_time: '10:00',
      dropoff_date: '2026-04-08',
      dropoff_time: '10:00',
      holding_price: null,
      holding_vehicle_type: null,
      city: null,
      alert_enabled: false,
      target_price: null,
      email_notifications: true,
    } satisfies Booking
    await createBooking(booking)
    expect(api.post).toHaveBeenCalledWith('/bookings/', booking)
  })

  it('getRuns calls GET /runs/', async () => {
    await getRuns()
    expect(api.get).toHaveBeenCalledWith('/runs/')
  })

  it('getPriceHistory calls GET /bookings/{name}/price-history', async () => {
    await getPriceHistory('trip1')
    expect(api.get).toHaveBeenCalledWith('/bookings/trip1/price-history')
  })

  it('getDashboardSummary calls GET /dashboard/summary', async () => {
    await getDashboardSummary()
    expect(api.get).toHaveBeenCalledWith('/dashboard/summary')
  })
})

describe('getSavings', () => {
  it('calls GET /bookings/{name}/savings', async () => {
    await getSavings('trip1')
    expect(api.get).toHaveBeenCalledWith('/bookings/trip1/savings')
  })
})

describe('getVolatility', () => {
  it('calls GET /analytics/volatility without params', async () => {
    await getVolatility()
    expect(api.get).toHaveBeenCalledWith('/analytics/volatility', { params: undefined })
  })

  it('passes booking_name as query param', async () => {
    await getVolatility('trip1')
    expect(api.get).toHaveBeenCalledWith('/analytics/volatility', {
      params: { booking_name: 'trip1' },
    })
  })
})

describe('getAlertSettings', () => {
  it('calls GET /settings/alerts', async () => {
    await getAlertSettings()
    expect(api.get).toHaveBeenCalledWith('/settings/alerts')
  })
})

describe('updateAlertSettings', () => {
  it('calls PUT /settings/alerts with payload', async () => {
    const alerts: AlertConfig[] = [
      { booking_name: 'trip1', alert_enabled: true, target_price: 250, email_notifications: true },
    ]
    await updateAlertSettings(alerts)
    expect(api.put).toHaveBeenCalledWith('/settings/alerts', { alerts })
  })
})
