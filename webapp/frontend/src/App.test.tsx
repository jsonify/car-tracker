import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from './App'

// Mock all pages to avoid API calls
vi.mock('./pages/Dashboard', () => ({ default: () => <div data-testid="page-dashboard">Dashboard</div> }))
vi.mock('./pages/Bookings', () => ({ default: () => <div>Bookings</div> }))
vi.mock('./pages/PriceHistory', () => ({ default: () => <div>PriceHistory</div> }))
vi.mock('./pages/Vehicles', () => ({ default: () => <div>Vehicles</div> }))
vi.mock('./pages/Runs', () => ({ default: () => <div>Runs</div> }))
vi.mock('./pages/Settings', () => ({ default: () => <div>Settings</div> }))

describe('App', () => {
  it('renders app root with Velocity Dark bg-surface', () => {
    render(<App />)
    expect(screen.getByTestId('app-root')).toHaveClass('bg-surface')
  })

  it('renders sidebar', () => {
    render(<App />)
    expect(screen.getByText('Car Tracker')).toBeInTheDocument()
  })

  it('renders dashboard by default', () => {
    render(<App />)
    expect(screen.getByTestId('page-dashboard')).toBeInTheDocument()
  })

  it('renders top app bar with search', () => {
    render(<App />)
    expect(screen.getByPlaceholderText('Search…')).toBeInTheDocument()
  })

  it('renders settings link in sidebar', () => {
    render(<App />)
    expect(screen.getByRole('link', { name: /settings/i })).toBeInTheDocument()
  })
})
