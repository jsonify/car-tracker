import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import PriceRangeChart from './PriceRangeChart'

// Mock recharts to avoid canvas issues in tests
vi.mock('recharts', () => {
  const MockResponsiveContainer = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  )
  const MockBarChart = ({ children }: any) => (
    <div data-testid="bar-chart">{children}</div>
  )
  const MockBar = (props: any) => (
    <div
      data-testid={`bar-${props.dataKey}`}
      data-stack-id={props.stackId}
      data-fill={props.fill}
    />
  )
  const MockXAxis = (props: any) => (
    <div data-testid="x-axis" data-datakey={props.dataKey} />
  )
  const MockYAxis = (props: any) => (
    <div
      data-testid="y-axis"
      data-has-tick-formatter={typeof props.tickFormatter === 'function' ? 'true' : 'false'}
    />
  )
  const MockCartesianGrid = () => <div data-testid="cartesian-grid" />
  const MockTooltip = (props: any) => {
    // Simulate calling the formatter with the "base" bar — should return null
    const baseResult = props.formatter ? props.formatter(100, 'base', { payload: { min: 100, max: 250, base: 100, range: 150 } }) : undefined
    // Simulate calling the formatter with the "range" bar
    const rangeResult = props.formatter ? props.formatter(150, 'range', { payload: { min: 100, max: 250, base: 100, range: 150 } }) : undefined
    return (
      <div
        data-testid="tooltip"
        data-base-formatter-null={baseResult === null || (Array.isArray(baseResult) && baseResult[0] === null) ? 'true' : 'false'}
        data-range-formatter-value={Array.isArray(rangeResult) ? String(rangeResult[0]) : ''}
      />
    )
  }

  return {
    ResponsiveContainer: MockResponsiveContainer,
    BarChart: MockBarChart,
    Bar: MockBar,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    CartesianGrid: MockCartesianGrid,
    Tooltip: MockTooltip,
  }
})

const sampleData = [
  { category: 'Economy', min: 180, max: 260, range: 80 },
  { category: 'Compact', min: 220, max: 320, range: 100 },
]

describe('PriceRangeChart', () => {
  it('renders responsive-container when data provided', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    expect(getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('renders empty-message when data is empty', () => {
    const { getByTestId } = render(<PriceRangeChart data={[]} />)
    expect(getByTestId('empty-message')).toBeInTheDocument()
    expect(getByTestId('empty-message').textContent).toBe('No data available.')
  })

  it('does not render responsive-container when data is empty', () => {
    const { queryByTestId } = render(<PriceRangeChart data={[]} />)
    expect(queryByTestId('responsive-container')).toBeNull()
  })

  it('renders two bars with same stackId (floating range pattern)', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    const baseBar = getByTestId('bar-base')
    const rangeBar = getByTestId('bar-range')
    expect(baseBar).toBeInTheDocument()
    expect(rangeBar).toBeInTheDocument()
    expect(baseBar.getAttribute('data-stack-id')).toBe(rangeBar.getAttribute('data-stack-id'))
  })

  it('base bar has transparent fill', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    expect(getByTestId('bar-base').getAttribute('data-fill')).toBe('transparent')
  })

  it('tooltip formatter returns null for base bar', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    expect(getByTestId('tooltip').getAttribute('data-base-formatter-null')).toBe('true')
  })

  it('tooltip formatter returns max value for range bar', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    expect(getByTestId('tooltip').getAttribute('data-range-formatter-value')).toBe('$250.00')
  })

  it('y-axis has tick formatter', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    expect(getByTestId('y-axis').getAttribute('data-has-tick-formatter')).toBe('true')
  })

  it('x-axis uses category dataKey', () => {
    const { getByTestId } = render(<PriceRangeChart data={sampleData} />)
    expect(getByTestId('x-axis').getAttribute('data-datakey')).toBe('category')
  })
})
