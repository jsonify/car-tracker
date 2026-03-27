import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

export default api

// --- Types ---

export interface Booking {
  name: string
  pickup_location: string
  pickup_date: string
  pickup_time: string
  dropoff_date: string
  dropoff_time: string
  holding_price: number | null
  holding_vehicle_type: string | null
  city: string | null
  alert_enabled: boolean
  target_price: number | null
  email_notifications: boolean
}

export interface RunSummary {
  id: number
  run_at: string
  pickup_location: string
  pickup_date: string
  dropoff_date: string
  booking_name: string
  holding_price: number | null
  holding_vehicle_type: string | null
  vehicle_count: number
}

export interface VehicleRow {
  id: number
  run_id: number
  run_at: string
  booking_name: string
  position: number
  name: string
  brand: string | null
  total_price: number
  price_per_day: number
}

export interface PriceHistory {
  booking_name: string
  run_dates: string[]
  categories: Record<string, number[]>
  holding_price: number | null
  holding_vehicle_type: string | null
}

export interface BookingSummary {
  name: string
  pickup_date: string
  dropoff_date: string
  pickup_location: string
  holding_price: number | null
  holding_vehicle_type: string | null
  best_current_price: number | null
  savings: number | null
  days_remaining: number
}

export interface VolatileCategory {
  booking_name: string
  category: string
  min_price: number
  max_price: number
  range: number
}

export interface DashboardSummary {
  active_booking_count: number
  total_run_count: number
  total_savings: number
  alert_count: number
  bookings: BookingSummary[]
  volatile_categories: VolatileCategory[]
  recent_runs: RunSummary[]
}

export interface SavingsData {
  booking_name: string
  holding_price: number | null
  current_best: number | null
  delta: number | null
  percentage_change: number | null
}

export interface VolatilityData {
  booking_name: string
  category: string
  min_price: number
  max_price: number
  price_range: number
  std_dev: number
  trend: 'up' | 'down' | 'stable'
  sample_count: number
}

export interface AlertConfig {
  booking_name: string
  alert_enabled: boolean
  target_price: number | null
  email_notifications: boolean
}

export interface AlertSettingsResponse {
  alerts: AlertConfig[]
}

// --- API calls ---

export const getBookings = () => api.get<Booking[]>('/bookings/').then(r => r.data)
export const createBooking = (b: Booking) => api.post<Booking>('/bookings/', b).then(r => r.data)
export const updateBooking = (name: string, b: Booking) => api.put<Booking>(`/bookings/${name}`, b).then(r => r.data)
export const deleteBooking = (name: string) => api.delete(`/bookings/${name}`)

export const getRuns = () => api.get<RunSummary[]>('/runs/').then(r => r.data)
export const getRunVehicles = (id: number) => api.get<VehicleRow[]>(`/runs/${id}/vehicles`).then(r => r.data)

export const getVehicles = (params?: Record<string, string | number>) =>
  api.get<VehicleRow[]>('/vehicles/', { params }).then(r => r.data)

export const getPriceHistory = (bookingName: string) =>
  api.get<PriceHistory>(`/bookings/${bookingName}/price-history`).then(r => r.data)

export const getDashboardSummary = () =>
  api.get<DashboardSummary>('/dashboard/summary').then(r => r.data)

export const getSavings = (bookingName: string) =>
  api.get<SavingsData>(`/bookings/${bookingName}/savings`).then(r => r.data)

export const getVolatility = (bookingName?: string) =>
  api.get<VolatilityData[]>('/analytics/volatility', {
    params: bookingName ? { booking_name: bookingName } : undefined,
  }).then(r => r.data)

export const getAlertSettings = () =>
  api.get<AlertSettingsResponse>('/settings/alerts').then(r => r.data)

export const updateAlertSettings = (alerts: AlertConfig[]) =>
  api.put<AlertSettingsResponse>('/settings/alerts', { alerts }).then(r => r.data)
