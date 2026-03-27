import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import StatsCard from './StatsCard'

describe('StatsCard', () => {
  it('renders label and value', () => {
    render(<StatsCard label="Total Savings" value="$450" />)
    expect(screen.getByText('Total Savings')).toBeInTheDocument()
    expect(screen.getByText('$450')).toBeInTheDocument()
  })

  it('renders icon when provided', () => {
    render(<StatsCard label="Active" value="5" icon="event_note" />)
    expect(screen.getByText('event_note')).toBeInTheDocument()
  })

  it('renders trend when provided', () => {
    render(
      <StatsCard
        label="Savings"
        value="$100"
        trend={{ direction: 'up', text: '+12% this week' }}
      />
    )
    expect(screen.getByText('+12% this week')).toBeInTheDocument()
    expect(screen.getByText('trending_up')).toBeInTheDocument()
  })

  it('renders down trend', () => {
    render(
      <StatsCard
        label="Price"
        value="$300"
        trend={{ direction: 'down', text: '-5%' }}
      />
    )
    expect(screen.getByText('trending_down')).toBeInTheDocument()
  })

  it('renders neutral trend', () => {
    render(
      <StatsCard
        label="Avg"
        value="$200"
        trend={{ direction: 'neutral', text: 'No change' }}
      />
    )
    expect(screen.getByText('trending_flat')).toBeInTheDocument()
  })

  it('omits trend section when not provided', () => {
    const { container } = render(<StatsCard label="Test" value="0" />)
    expect(container.querySelector('.flex.items-center.gap-1')).toBeNull()
  })

  it('appends custom className', () => {
    const { container } = render(<StatsCard label="X" value="1" className="col-span-2" />)
    expect(container.firstChild).toHaveClass('col-span-2')
  })
})
