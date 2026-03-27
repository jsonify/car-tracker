import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from './Sidebar'

function renderSidebar(initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Sidebar />
    </MemoryRouter>
  )
}

describe('Sidebar', () => {
  it('renders app title', () => {
    renderSidebar()
    expect(screen.getByText('Car Tracker')).toBeInTheDocument()
  })

  it('renders all nav links including Settings', () => {
    renderSidebar()
    const nav = screen.getByRole('navigation')
    expect(nav).toHaveTextContent('Dashboard')
    expect(nav).toHaveTextContent('Bookings')
    expect(nav).toHaveTextContent('Price History')
    expect(nav).toHaveTextContent('Vehicles')
    expect(nav).toHaveTextContent('Runs Log')
    expect(nav).toHaveTextContent('Settings')
  })

  it('marks dashboard link as active on /', () => {
    renderSidebar('/')
    const dashLink = screen.getByRole('link', { name: /dashboard/i })
    expect(dashLink.className).toContain('text-primary')
  })

  it('marks bookings link as active on /bookings', () => {
    renderSidebar('/bookings')
    const link = screen.getByRole('link', { name: /bookings/i })
    expect(link.className).toContain('text-primary')
  })

  it('does not mark dashboard active on /bookings', () => {
    renderSidebar('/bookings')
    const dashLink = screen.getByRole('link', { name: /dashboard/i })
    expect(dashLink.className).not.toContain('text-primary')
  })

  it('renders New Search button', () => {
    renderSidebar()
    expect(screen.getByText('New Search')).toBeInTheDocument()
  })

  it('renders Costco Travel subtitle', () => {
    renderSidebar()
    expect(screen.getByText('Costco Travel')).toBeInTheDocument()
  })
})
