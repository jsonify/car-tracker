import { render, screen, waitFor, fireEvent } from '@testing-library/react'
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

  it('shows Active badge for future bookings', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByText('Active')).toBeInTheDocument()
    })
  })

  it('shows holding price formatted', async () => {
    render(<Bookings />)
    await waitFor(() => {
      expect(screen.getByText('$300.00')).toBeInTheDocument()
    })
  })

  it('opens modal when Add Booking clicked', async () => {
    render(<Bookings />)
    await waitFor(() => screen.getByText('Add Booking'))
    fireEvent.click(screen.getByText('Add Booking'))
    expect(screen.getByText('Add Booking', { selector: 'h2' })).toBeInTheDocument()
  })

  it('opens edit modal when Edit clicked', async () => {
    render(<Bookings />)
    await waitFor(() => screen.getByText('Edit'))
    fireEvent.click(screen.getByText('Edit'))
    expect(screen.getByText('Edit Booking')).toBeInTheDocument()
  })

  it('shows confirm on first delete click', async () => {
    render(<Bookings />)
    await waitFor(() => screen.getByText('Delete'))
    fireEvent.click(screen.getByText('Delete'))
    expect(screen.getByText('Confirm?')).toBeInTheDocument()
  })
})
