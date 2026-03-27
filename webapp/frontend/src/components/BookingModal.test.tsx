import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import BookingModal from './BookingModal'

const noop = async () => {}

describe('BookingModal', () => {
  it('renders Add Booking title when no booking', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    expect(screen.getByText('Add Booking')).toBeInTheDocument()
  })

  it('renders Edit Booking title when booking provided', () => {
    const booking = {
      name: 'Test',
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
    }
    render(<BookingModal booking={booking} onClose={() => {}} onSave={noop} />)
    expect(screen.getByText('Edit Booking')).toBeInTheDocument()
  })

  it('renders city field', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    expect(screen.getByPlaceholderText('San Francisco')).toBeInTheDocument()
  })

  it('renders target price field', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    expect(screen.getByPlaceholderText('250.00')).toBeInTheDocument()
  })

  it('renders alert toggle', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    expect(screen.getByText('Alerts')).toBeInTheDocument()
  })

  it('renders email toggle', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  it('calls onClose when cancel clicked', () => {
    const closeFn = vi.fn()
    render(<BookingModal onClose={closeFn} onSave={noop} />)
    fireEvent.click(screen.getByText('Cancel'))
    expect(closeFn).toHaveBeenCalled()
  })

  it('renders save button', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    expect(screen.getByText('Save')).toBeInTheDocument()
  })

  it('disables name field when editing', () => {
    const booking = {
      name: 'Existing',
      pickup_location: 'LAX',
      pickup_date: '2026-05-01',
      pickup_time: '09:00',
      dropoff_date: '2026-05-08',
      dropoff_time: '09:00',
      holding_price: null,
      holding_vehicle_type: null,
      city: null,
      alert_enabled: false,
      target_price: null,
      email_notifications: true,
    }
    render(<BookingModal booking={booking} onClose={() => {}} onSave={noop} />)
    const nameInput = screen.getByDisplayValue('Existing')
    expect(nameInput).toBeDisabled()
  })

  it('calls onSave on submit', async () => {
    const saveFn = vi.fn(() => Promise.resolve())
    const closeFn = vi.fn()
    render(<BookingModal onClose={closeFn} onSave={saveFn} />)
    fireEvent.submit(screen.getByText('Save').closest('form')!)
    await waitFor(() => {
      expect(saveFn).toHaveBeenCalled()
    })
  })

  it('shows error on save failure', async () => {
    const saveFn = vi.fn(() => Promise.reject(new Error('fail')))
    render(<BookingModal onClose={() => {}} onSave={saveFn} />)
    fireEvent.submit(screen.getByText('Save').closest('form')!)
    await waitFor(() => {
      expect(screen.getByText('Failed to save booking.')).toBeInTheDocument()
    })
  })

  it('updates target price via placeholder', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    const targetInput = screen.getByPlaceholderText('250.00')
    fireEvent.change(targetInput, { target: { value: '200' } })
    expect(screen.getByDisplayValue('200')).toBeInTheDocument()
  })

  it('updates city field', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    const cityInput = screen.getByPlaceholderText('San Francisco')
    fireEvent.change(cityInput, { target: { value: 'Los Angeles' } })
    expect(screen.getByDisplayValue('Los Angeles')).toBeInTheDocument()
  })

  it('updates vehicle type field', () => {
    render(<BookingModal onClose={() => {}} onSave={noop} />)
    const input = screen.getByPlaceholderText('Economy Car')
    fireEvent.change(input, { target: { value: 'SUV' } })
    expect(screen.getByDisplayValue('SUV')).toBeInTheDocument()
  })
})
