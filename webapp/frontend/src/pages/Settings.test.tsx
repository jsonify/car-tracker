import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Settings from './Settings'

const mockAlerts = {
  alerts: [
    { booking_name: 'Trip1', alert_enabled: true, target_price: 250, email_notifications: true },
  ],
}

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
    city: null,
    alert_enabled: true,
    target_price: 250,
    email_notifications: true,
  },
]

const mockUpdateAlertSettings = vi.fn(() => Promise.resolve(mockAlerts))

vi.mock('../api/client', () => ({
  getAlertSettings: vi.fn(() => Promise.resolve(mockAlerts)),
  getBookings: vi.fn(() => Promise.resolve(mockBookings)),
  updateAlertSettings: (...args: unknown[]) => mockUpdateAlertSettings(...args),
}))

describe('Settings', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders settings page', async () => {
    render(<Settings />)
    await waitFor(() => {
      expect(screen.getByTestId('page-settings')).toBeInTheDocument()
    })
  })

  it('displays booking alert config', async () => {
    render(<Settings />)
    await waitFor(() => {
      expect(screen.getByText('Trip1')).toBeInTheDocument()
    })
  })

  it('renders alert toggles', async () => {
    render(<Settings />)
    await waitFor(() => {
      expect(screen.getByText('Alerts')).toBeInTheDocument()
      expect(screen.getByText('Email')).toBeInTheDocument()
    })
  })

  it('saves settings on button click', async () => {
    render(<Settings />)
    await waitFor(() => screen.getByText('Save Settings'))
    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      expect(mockUpdateAlertSettings).toHaveBeenCalled()
    })
  })

  it('shows success message after save', async () => {
    render(<Settings />)
    await waitFor(() => screen.getByText('Save Settings'))
    fireEvent.click(screen.getByText('Save Settings'))
    await waitFor(() => {
      expect(screen.getByText('Settings saved successfully.')).toBeInTheDocument()
    })
  })

  it('renders target price input with value', async () => {
    render(<Settings />)
    await waitFor(() => {
      expect(screen.getByDisplayValue('250')).toBeInTheDocument()
    })
  })
})
