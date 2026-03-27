import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Bookings from './Bookings'

const mockBookings = [
  {
    name: 'Trip1',
    pickup_location: 'SFO',
    pickup_date: '2027-04-01',
    pickup_time: '10:00',
    dropoff_date: '2027-04-08',
    dropoff_time: '10:00',
    holding_price: 300,
    holding_vehicle_type: 'Economy',
    city: 'San Francisco',
    alert_enabled: true,
    target_price: 250,
    email_notifications: true,
  },
]

vi.mock('../api/client', () => ({
  getBookings: vi.fn(() => Promise.resolve(mockBookings)),
  createBooking: vi.fn(),
  updateBooking: vi.fn(),
  deleteBooking: vi.fn(),
}))

describe('Bookings', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders bookings table after loading', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByText('Trip1')).toBeInTheDocument()
      expect(screen.getByText('SFO')).toBeInTheDocument()
    })
  })

  it('shows city column', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByText('San Francisco')).toBeInTheDocument()
    })
  })

  it('shows alert icon for enabled alerts', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByText('notifications_active')).toBeInTheDocument()
    })
  })

  it('renders page test id', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByTestId('page-bookings')).toBeInTheDocument()
    })
  })

  it('shows Add Booking button', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByText('Add Booking')).toBeInTheDocument()
    })
  })
})
