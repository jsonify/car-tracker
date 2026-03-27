import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import EmptyState from './EmptyState'

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No data" />)
    expect(screen.getByText('No data')).toBeInTheDocument()
  })

  it('renders description when provided', () => {
    render(<EmptyState title="Empty" description="Try adding something" />)
    expect(screen.getByText('Try adding something')).toBeInTheDocument()
  })

  it('omits description when not provided', () => {
    const { container } = render(<EmptyState title="Empty" />)
    const paragraphs = container.querySelectorAll('p')
    expect(paragraphs).toHaveLength(1)
  })

  it('renders default inbox icon', () => {
    render(<EmptyState title="Empty" />)
    expect(screen.getByText('inbox')).toBeInTheDocument()
  })

  it('renders custom icon', () => {
    render(<EmptyState title="Empty" icon="search" />)
    expect(screen.getByText('search')).toBeInTheDocument()
  })
})
