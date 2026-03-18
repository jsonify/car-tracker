import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Badge from './Badge'

describe('Badge', () => {
  it('renders label', () => {
    render(<Badge label="Active" />)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('applies green variant classes', () => {
    render(<Badge label="Saving" variant="green" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('green')
  })

  it('applies red variant classes', () => {
    render(<Badge label="Over" variant="red" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('red')
  })

  it('defaults to gray variant', () => {
    render(<Badge label="Default" />)
    const el = screen.getByTestId('badge')
    expect(el.className).toContain('gray')
  })
})
