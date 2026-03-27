import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import Card from './Card'

describe('Card', () => {
  it('renders children', () => {
    render(<Card>hello world</Card>)
    expect(screen.getByText('hello world')).toBeInTheDocument()
  })

  it('renders title when provided', () => {
    render(<Card title="My Card">content</Card>)
    expect(screen.getByText('My Card')).toBeInTheDocument()
  })

  it('omits title element when not provided', () => {
    const { container } = render(<Card>content</Card>)
    expect(container.querySelector('h2')).toBeNull()
  })

  it('applies standard variant by default', () => {
    const { container } = render(<Card>content</Card>)
    expect(container.firstChild).toHaveClass('bg-surface-container')
  })

  it('applies glass variant', () => {
    const { container } = render(<Card variant="glass">content</Card>)
    expect(container.firstChild).toHaveClass('glass')
  })

  it('applies gradient variant', () => {
    const { container } = render(<Card variant="gradient">content</Card>)
    const el = container.firstChild as HTMLElement
    expect(el.className).toContain('bg-gradient-to-br')
  })

  it('appends custom className', () => {
    const { container } = render(<Card className="mt-4">content</Card>)
    expect(container.firstChild).toHaveClass('mt-4')
  })
})
