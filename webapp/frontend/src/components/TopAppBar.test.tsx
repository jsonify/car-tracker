import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import TopAppBar from './TopAppBar'

describe('TopAppBar', () => {
  it('renders title when provided', () => {
    render(<TopAppBar title="Dashboard" />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('omits title when not provided', () => {
    const { container } = render(<TopAppBar />)
    expect(container.querySelector('h1')).toBeNull()
  })

  it('renders search input', () => {
    render(<TopAppBar />)
    expect(screen.getByPlaceholderText('Search…')).toBeInTheDocument()
  })

  it('has sticky positioning', () => {
    const { container } = render(<TopAppBar />)
    const header = container.querySelector('header')
    expect(header).toHaveClass('sticky')
  })

  it('applies glassmorphism class', () => {
    const { container } = render(<TopAppBar />)
    const header = container.querySelector('header')
    expect(header).toHaveClass('glass')
  })
})
