import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import PriceChangeChart from './PriceChangeChart'
import { colors as tokens } from '../styles/tokens'
import type { PriceChangePoint } from '../utils/chartData'

// Mock recharts to avoid canvas issues in tests
vi.mock('recharts', () => {
  const MockResponsiveContainer = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  )
  const MockBarChart = ({ children, ...props }: any) => (
    <div data-testid="bar-chart" data-margin={JSON.stringify(props.margin)}>{children}</div>
  )
  const MockBar = ({ children, ...props }: any) => (
    <div data-testid="bar" data-datakey={props.dataKey}>{children}</div>
  )
  const MockCell = (props: any) => (
    <div data-testid="cell" data-fill={props.fill} />
  )
  const MockXAxis = (props: any) => (
    <div
      data-testid="x-axis"
      data-datakey={props.dataKey}
      data-angle={props.angle}
      data-text-anchor={props.textAnchor}
      data-interval={String(props.interval)}
      data-font-size={String(props.fontSize)}
    />
  )
  const MockYAxis = (props: any) => (
    <div
      data-testid="y-axis"
      data-has-tick-formatter={typeof props.tickFormatter === 'function' ? 'true' : 'false'}
      data-font-size={String(props.fontSize)}
    />
  )
  const MockTooltip = (props: any) => {
    const formatterResult = props.formatter ? props.formatter(5.5) : null
    const formatterResultNeg = props.formatter ? props.formatter(-3.25) : null
    return (
      <div
        data-testid="tooltip"
        data-formatter-positive={Array.isArray(formatterResult) ? String(formatterResult[0]) : ''}
        data-formatter-negative={Array.isArray(formatterResultNeg) ? String(formatterResultNeg[0]) : ''}
        data-formatter-label={Array.isArray(formatterResult) ? String(formatterResult[1]) : ''}
      />
    )
  }
  const MockReferenceLine = (props: any) => (
    <div
      data-testid="reference-line"
      data-y={String(props.y)}
      data-stroke={props.stroke}
    />
  )

  return {
    ResponsiveContainer: MockResponsiveContainer,
    BarChart: MockBarChart,
    Bar: MockBar,
    Cell: MockCell,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    Tooltip: MockTooltip,
    ReferenceLine: MockReferenceLine,
  }
})

const sampleData: PriceChangePoint[] = [
  { category: 'Economy', delta: -15.5, pctChange: -7.75 },
  { category: 'Compact', delta: 10.0, pctChange: 4.0 },
  { category: 'SUV', delta: -5.25, pctChange: -2.1 },
]

describe('PriceChangeChart', () => {
  it('renders responsive-container when data provided', () => {
    const { getByTestId } = render(<PriceChangeChart data={sampleData} />)
    expect(getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('renders empty-message when data is empty', () => {
    const { getByTestId } = render(<PriceChangeChart data={[]} />)
    expect(getByTestId('empty-message')).toBeInTheDocument()
    expect(getByTestId('empty-message').textContent).toBe('No data available.')
  })

  it('does not render responsive-container when data is empty', () => {
    const { queryByTestId } = render(<PriceChangeChart data={[]} />)
    expect(queryByTestId('responsive-container')).toBeNull()
  })

  it('renders a bar for each data point', () => {
    const { getAllByTestId } = render(<PriceChangeChart data={sampleData} />)
    // Each data point should produce a Cell element inside the Bar
    const cells = getAllByTestId('cell')
    expect(cells).toHaveLength(sampleData.length)
  })

  it('colors negative delta bars with tertiary (price dropped = good)', () => {
    const { getAllByTestId } = render(<PriceChangeChart data={sampleData} />)
    const cells = getAllByTestId('cell')
    // Economy delta=-15.5 → tertiary
    expect(cells[0].getAttribute('data-fill')).toBe(tokens.tertiary)
  })

  it('colors positive delta bars with error (price rose = bad)', () => {
    const { getAllByTestId } = render(<PriceChangeChart data={sampleData} />)
    const cells = getAllByTestId('cell')
    // Compact delta=10.0 → error
    expect(cells[1].getAttribute('data-fill')).toBe(tokens.error)
  })

  it('renders reference line at y=0', () => {
    const { getByTestId } = render(<PriceChangeChart data={sampleData} />)
    const refLine = getByTestId('reference-line')
    expect(refLine.getAttribute('data-y')).toBe('0')
    expect(refLine.getAttribute('data-stroke')).toBe(tokens.outlineVariant)
  })

  it('YAxis has tickFormatter function', () => {
    const { getByTestId } = render(<PriceChangeChart data={sampleData} />)
    expect(getByTestId('y-axis').getAttribute('data-has-tick-formatter')).toBe('true')
  })

  it('tooltip formatter shows positive sign for positive deltas', () => {
    const { getByTestId } = render(<PriceChangeChart data={sampleData} />)
    const tooltip = getByTestId('tooltip')
    // v=5.5 → "+$5.50"
    expect(tooltip.getAttribute('data-formatter-positive')).toBe('+$5.50')
  })

  it('tooltip formatter shows negative sign for negative deltas', () => {
    const { getByTestId } = render(<PriceChangeChart data={sampleData} />)
    const tooltip = getByTestId('tooltip')
    // v=-3.25 → "-$3.25"
    expect(tooltip.getAttribute('data-formatter-negative')).toBe('-$3.25')
  })

  it('tooltip formatter label is "Change"', () => {
    const { getByTestId } = render(<PriceChangeChart data={sampleData} />)
    const tooltip = getByTestId('tooltip')
    expect(tooltip.getAttribute('data-formatter-label')).toBe('Change')
  })
})
