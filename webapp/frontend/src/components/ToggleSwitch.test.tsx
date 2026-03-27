import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ToggleSwitch from './ToggleSwitch'

describe('ToggleSwitch', () => {
  it('renders with role=switch', () => {
    render(<ToggleSwitch checked={false} onChange={() => {}} />)
    expect(screen.getByRole('switch')).toBeInTheDocument()
  })

  it('reflects checked state via aria-checked', () => {
    render(<ToggleSwitch checked={true} onChange={() => {}} />)
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'true')
  })

  it('reflects unchecked state', () => {
    render(<ToggleSwitch checked={false} onChange={() => {}} />)
    expect(screen.getByRole('switch')).toHaveAttribute('aria-checked', 'false')
  })

  it('calls onChange when clicked', () => {
    const handler = vi.fn()
    render(<ToggleSwitch checked={false} onChange={handler} />)
    fireEvent.click(screen.getByRole('switch'))
    expect(handler).toHaveBeenCalledWith(true)
  })

  it('passes inverse value on click', () => {
    const handler = vi.fn()
    render(<ToggleSwitch checked={true} onChange={handler} />)
    fireEvent.click(screen.getByRole('switch'))
    expect(handler).toHaveBeenCalledWith(false)
  })

  it('renders label when provided', () => {
    render(<ToggleSwitch checked={false} onChange={() => {}} label="Alerts" />)
    expect(screen.getByText('Alerts')).toBeInTheDocument()
  })

  it('does not fire onChange when disabled', () => {
    const handler = vi.fn()
    render(<ToggleSwitch checked={false} onChange={handler} disabled />)
    fireEvent.click(screen.getByRole('switch'))
    expect(handler).not.toHaveBeenCalled()
  })

  it('applies primary color when checked', () => {
    render(<ToggleSwitch checked={true} onChange={() => {}} />)
    expect(screen.getByRole('switch')).toHaveClass('bg-primary')
  })
})
