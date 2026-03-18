import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByTestId('app-root')).toBeInTheDocument()
  })

  it('renders sidebar with Car Tracker title', () => {
    render(<App />)
    expect(screen.getByText('Car Tracker')).toBeInTheDocument()
  })

  it('renders sidebar navigation links', () => {
    render(<App />)
    expect(screen.getByRole('navigation')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /bookings/i })).toBeInTheDocument()
  })
})
