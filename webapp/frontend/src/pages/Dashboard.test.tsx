import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Dashboard from './Dashboard'

const mockSummary = {
  active_booking_count: 3,
  total_run_count: 12,
  total_savings: 45.5,
  alert_count: 2,
  bookings: [
    {
      name: 'Trip1',
      pickup_date: '2027-01-15',
      dropoff_date: '2027-01-22',
      pickup_location: 'SFO',
      holding_price: 300,
      holding_vehicle_type: 'Economy',
      best_current_price: 280,
      savings: 20,
      days_remaining: 30,
    },
  ],
  volatile_categories: [
    { booking_name: 'Trip1', category: 'Economy', min_price: 200, max_price: 350, range: 150 },
  ],
  recent_runs: [
    { id: 1, run_at: '2026-03-25T10:00:00', pickup_location: 'SFO', pickup_date: '2027-01-15', dropoff_date: '2027-01-22', booking_name: 'Trip1', holding_price: 300, holding_vehicle_type: 'Economy', vehicle_count: 5 },
  ],
}

vi.mock('../api/client', () => ({
  getDashboardSummary: vi.fn(() => Promise.resolve(mockSummary)),
}))

describe('Dashboard', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders stats cards after loading', async () => {
    render(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('12')).toBeInTheDocument()
      expect(screen.getByText('$45.50')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
    })
  })

  it('renders booking timeline', async () => {
    render(<Dashboard />)
    await waitFor(() => {
      expect(screen.getAllByText('Trip1').length).toBeGreaterThanOrEqual(1)
      expect(screen.getAllByText('SFO').length).toBeGreaterThanOrEqual(1)
    })
  })

  it('renders volatility section', async () => {
    render(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByText('Economy')).toBeInTheDocument()
      expect(screen.getByText('±$150.00')).toBeInTheDocument()
    })
  })

  it('renders page test id', async () => {
    render(<Dashboard />)
    await waitFor(() => {
      expect(screen.getByTestId('page-dashboard')).toBeInTheDocument()
    })
  })
})
