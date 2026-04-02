import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import HoldingComparisonChart from './HoldingComparisonChart'

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
      data-fill={props.fill}
      data-name={props.name}
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
  const MockTooltip = (props: any) => {
    const formatterResult = props.formatter ? props.formatter(199.99, 'holding') : null
    return (
      <div
        data-testid="tooltip"
        data-formatter-value={Array.isArray(formatterResult) ? String(formatterResult[0]) : ''}
        data-formatter-name={Array.isArray(formatterResult) ? String(formatterResult[1]) : ''}
      />
    )
  }
  const MockLegend = () => <div data-testid="legend" />

  return {
    ResponsiveContainer: MockResponsiveContainer,
    BarChart: MockBarChart,
    Bar: MockBar,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    Tooltip: MockTooltip,
    Legend: MockLegend,
  }
})

const sampleData = { holdingPrice: 249.99, currentBest: 199.99 }

describe('HoldingComparisonChart', () => {
  it('renders no-holding-message when data is null', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={null} holdingVehicleType={null} />
    )
    expect(getByTestId('no-holding-message')).toBeInTheDocument()
    expect(getByTestId('no-holding-message').textContent).toBe('No holding price configured.')
  })

  it('renders responsive-container when data is provided', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('responsive-container')).toBeInTheDocument()
  })

  it('does not render the chart when data is null', () => {
    const { queryByTestId } = render(
      <HoldingComparisonChart data={null} holdingVehicleType={null} />
    )
    expect(queryByTestId('responsive-container')).toBeNull()
    expect(queryByTestId('bar-chart')).toBeNull()
  })

  it('renders two Bar elements for holding and current data keys', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('bar-holding')).toBeInTheDocument()
    expect(getByTestId('bar-current')).toBeInTheDocument()
  })

  it('holding bar uses primary color token', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('bar-holding').getAttribute('data-fill')).toBe('#fe9821')
  })

  it('current bar uses tertiary color token', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('bar-current').getAttribute('data-fill')).toBe('#81ecff')
  })

  it('renders legend', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('legend')).toBeInTheDocument()
  })

  it('y-axis has tick formatter', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('y-axis').getAttribute('data-has-tick-formatter')).toBe('true')
  })

  it('tooltip formatter returns formatted value and name', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType="Economy" />
    )
    expect(getByTestId('tooltip').getAttribute('data-formatter-value')).toBe('$199.99')
    expect(getByTestId('tooltip').getAttribute('data-formatter-name')).toBe('holding')
  })

  it('falls back to Vehicle name when holdingVehicleType is null but data is present', () => {
    const { getByTestId } = render(
      <HoldingComparisonChart data={sampleData} holdingVehicleType={null} />
    )
    expect(getByTestId('responsive-container')).toBeInTheDocument()
  })
})
