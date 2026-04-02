import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import LatestPricesChart from './LatestPricesChart'
import type { LatestPricePoint } from '../utils/chartData'

// Mock recharts to avoid canvas issues in tests
vi.mock('recharts', () => {
  const MockResponsiveContainer = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  )
  const MockBarChart = ({ children }: any) => (
    <div data-testid="bar-chart">{children}</div>
  )
  const MockBar = (props: any) => (
    <div data-testid="bar" data-fill={props.fill} data-datakey={props.dataKey} />
  )
  const MockXAxis = (props: any) => (
    <div
      data-testid="x-axis"
      data-has-tick-formatter={typeof props.tickFormatter === 'function' ? 'true' : 'false'}
    />
  )
  const MockYAxis = (props: any) => (
    <div data-testid="y-axis" data-datakey={props.dataKey} />
  )
  const MockCartesianGrid = (props: any) => (
    <div data-testid="cartesian-grid" data-horizontal={String(props.horizontal)} />
  )
  const MockTooltip = (props: any) => {
    const formatterResult = props.formatter ? props.formatter(99.99) : null
    return (
      <div
        data-testid="tooltip"
        data-formatter-value={Array.isArray(formatterResult) ? String(formatterResult[0]) : ''}
        data-formatter-name={Array.isArray(formatterResult) ? String(formatterResult[1]) : ''}
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

const sampleData: LatestPricePoint[] = [
  { category: 'Economy', price: 45.99 },
  { category: 'Compact', price: 62.50 },
  { category: 'SUV', price: 89.00 },
]

describe('LatestPricesChart', () => {
  it('renders responsive-container when data is provided', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('renders empty message when data is empty', () => {
    const { getByTestId } = render(<LatestPricesChart data={[]} />)
    expect(getByTestId('empty-message')).toBeInTheDocument()
    expect(getByTestId('empty-message').textContent).toBe('No data available.')
  })

  it('does not render chart when data is empty', () => {
    const { queryByTestId } = render(<LatestPricesChart data={[]} />)
    expect(queryByTestId('responsive-container')).toBeNull()
  })

  it('renders without errors with sample data', () => {
    expect(() => render(<LatestPricesChart data={sampleData} />)).not.toThrow()
  })

  it('renders bar chart with correct dataKey', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('bar').getAttribute('data-datakey')).toBe('price')
  })

  it('renders bar with primary color fill', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('bar').getAttribute('data-fill')).toBe('#fe9821')
  })

  it('renders y-axis with category dataKey', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('y-axis').getAttribute('data-datakey')).toBe('category')
  })

  it('renders x-axis with a tick formatter', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('x-axis').getAttribute('data-has-tick-formatter')).toBe('true')
  })

  it('renders cartesian grid with horizontal=false', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('cartesian-grid').getAttribute('data-horizontal')).toBe('false')
  })

  it('tooltip formatter returns dollar-formatted value and label', () => {
    const { getByTestId } = render(<LatestPricesChart data={sampleData} />)
    expect(getByTestId('tooltip').getAttribute('data-formatter-value')).toBe('$99.99')
    expect(getByTestId('tooltip').getAttribute('data-formatter-name')).toBe('Latest Price')
  })
})
