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
    render(<Card>content</Card>)
    expect(screen.queryByRole('heading')).toBeNull()
  })
})
