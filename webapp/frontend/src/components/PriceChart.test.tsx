import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import PriceChart from './PriceChart'
import { colors as tokens } from '../styles/tokens'

// Mock recharts to avoid canvas issues in tests
vi.mock('recharts', () => {
  const MockResponsiveContainer = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  )
  const MockLineChart = ({ children, ...props }: any) => (
    <div data-testid="line-chart" data-margin={JSON.stringify(props.margin)}>{children}</div>
  )
  const MockLine = (props: any) => (
    <div data-testid={`line-${props.dataKey}`} data-stroke={props.stroke} />
  )
  const MockXAxis = (props: any) => (
    <div
      data-testid="x-axis"
      data-stroke={props.stroke}
      data-has-tick-formatter={typeof props.tickFormatter === 'function' ? 'true' : 'false'}
    />
  )
  const MockYAxis = () => <div data-testid="y-axis" />
  const MockCartesianGrid = (props: any) => (
    <div data-testid="cartesian-grid" data-stroke={props.stroke} />
  )
  const MockTooltip = (props: any) => {
    const formatterResult = props.formatter ? props.formatter(123.45, 'Economy Car') : null
    return (
      <div
        data-testid="tooltip"
        data-bg={props.contentStyle?.backgroundColor}
        data-has-label-formatter={typeof props.labelFormatter === 'function' ? 'true' : 'false'}
        data-formatter-name={Array.isArray(formatterResult) ? String(formatterResult[1]) : ''}
      />
    )
  }
  const MockReferenceLine = (props: any) => (
    <div
      data-testid="reference-line"
      data-stroke={props.stroke}
      data-y={props.y}
      data-label-position={props.label?.position}
    />
  )
  const MockLegend = () => <div data-testid="legend" />

  return {
    ResponsiveContainer: MockResponsiveContainer,
    LineChart: MockLineChart,
    Line: MockLine,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    CartesianGrid: MockCartesianGrid,
    Tooltip: MockTooltip,
    ReferenceLine: MockReferenceLine,
    Legend: MockLegend,
  }
})

const sampleData = [
  { date: '2026-03-01', Economy: 200, Compact: 250 },
  { date: '2026-03-02', Economy: 210, Compact: 240 },
]

describe('PriceChart', () => {
  it('renders chart container', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy', 'Compact']}
        colors={{ Economy: '#fe9821', Compact: '#a68cff' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('uses Velocity Dark grid color', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('cartesian-grid').getAttribute('data-stroke')).toBe(tokens.outlineVariant)
  })

  it('uses Velocity Dark X axis stroke', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('x-axis').getAttribute('data-stroke')).toBe(tokens.outlineVariant)
  })

  it('uses Velocity Dark tooltip background', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('tooltip').getAttribute('data-bg')).toBe(tokens.surfaceContainerHigh)
  })

  it('renders a line for each category', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy', 'Compact']}
        colors={{ Economy: '#fe9821', Compact: '#a68cff' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('line-Economy')).toBeInTheDocument()
    expect(getByTestId('line-Compact')).toBeInTheDocument()
  })

  it('has right margin wide enough for holding price label', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    const margin = JSON.parse(getByTestId('line-chart').getAttribute('data-margin') ?? '{}')
    expect(margin.right).toBeGreaterThanOrEqual(100)
  })

  it('renders reference line when holding price provided', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={299}
      />
    )
    const refLine = getByTestId('reference-line')
    expect(refLine.getAttribute('data-y')).toBe('299')
    expect(refLine.getAttribute('data-stroke')).toBe(tokens.primary)
  })

  it('passes formatRunDate to XAxis tickFormatter', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('x-axis').getAttribute('data-has-tick-formatter')).toBe('true')
  })

  it('tooltip formatter returns category name (not undefined)', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy', 'Compact']}
        colors={{ Economy: '#fe9821', Compact: '#a68cff' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('tooltip').getAttribute('data-formatter-name')).toBe('Economy Car')
  })

  it('passes labelFormatter to Tooltip', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    expect(getByTestId('tooltip').getAttribute('data-has-label-formatter')).toBe('true')
  })

  it('reference line label is positioned inside chart boundary', () => {
    const { getByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={299}
      />
    )
    const pos = getByTestId('reference-line').getAttribute('data-label-position')
    expect(pos).toMatch(/^inside/)
  })

  it('does not render reference line when holding price is null', () => {
    const { queryByTestId } = render(
      <PriceChart
        data={sampleData}
        categories={['Economy']}
        colors={{ Economy: '#fe9821' }}
        holdingPrice={null}
      />
    )
    expect(queryByTestId('reference-line')).toBeNull()
  })
})
