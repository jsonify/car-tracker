import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Badge from './Badge'

describe('Badge', () => {
  it('renders label', () => {
    render(<Badge label="Active" />)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('defaults to muted variant', () => {
    render(<Badge label="Default" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('bg-surface-container-highest')
  })

  it('applies primary variant', () => {
    render(<Badge label="Hot" variant="primary" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('text-primary')
  })

  it('applies secondary variant', () => {
    render(<Badge label="Info" variant="secondary" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('text-secondary')
  })

  it('applies tertiary variant', () => {
    render(<Badge label="Cool" variant="tertiary" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('text-tertiary')
  })

  it('applies error variant', () => {
    render(<Badge label="Over" variant="error" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('text-error')
  })

  it('renders with rounded-full pill style', () => {
    render(<Badge label="Pill" />)
    const el = screen.getByTestId('badge')
    expect(el).toHaveClass('rounded-full')
  })
})
