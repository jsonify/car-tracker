import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoadingSpinner from './LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders default loading label', () => {
    render(<LoadingSpinner />)
    expect(screen.getByText('Loading…')).toBeInTheDocument()
  })

  it('renders custom label', () => {
    render(<LoadingSpinner label="Fetching data…" />)
    expect(screen.getByText('Fetching data…')).toBeInTheDocument()
  })

  it('renders progress_activity icon', () => {
    render(<LoadingSpinner />)
    expect(screen.getByText('progress_activity')).toBeInTheDocument()
  })

  it('has spin animation class', () => {
    render(<LoadingSpinner />)
    const icon = screen.getByText('progress_activity')
    expect(icon).toHaveClass('animate-spin')
  })
})
