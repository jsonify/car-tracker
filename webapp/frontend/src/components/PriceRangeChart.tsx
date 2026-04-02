import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { PriceRangePoint } from '../utils/chartData'
import { colors as tokens, fonts } from '../styles/tokens'

interface PriceRangeChartProps {
  data: PriceRangePoint[]
}

interface RangeBarPoint {
  category: string
  base: number
  range: number
  min: number
  max: number
}

export default function PriceRangeChart({ data }: PriceRangeChartProps) {
  if (data.length === 0) {
    return <p data-testid="empty-message">No data available.</p>
  }

  const chartData: RangeBarPoint[] = data.map((d) => ({
    category: d.category,
    base: d.min,
    range: d.max - d.min,
    min: d.min,
    max: d.max,
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart
        data={chartData}
        margin={{ top: 8, right: 16, left: 10, bottom: 60 }}
      >
        <CartesianGrid
          vertical={false}
          stroke={tokens.outlineVariant}
          strokeDasharray="3 3"
        />
        <XAxis
          dataKey="category"
          tick={{
            fill: tokens.onSurfaceVariant,
            fontSize: 10,
            fontFamily: fonts.body,
            textAnchor: 'end',
          }}
          tickLine={false}
          stroke={tokens.outlineVariant}
          interval={0}
          angle={-45}
        />
        <YAxis
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 11, fontFamily: fonts.body }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => `$${v}`}
          domain={['auto', 'auto']}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: tokens.surfaceContainerHigh,
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          }}
          labelStyle={{
            color: tokens.onSurfaceVariant,
            fontSize: 12,
            fontFamily: fonts.headline,
            fontWeight: 700,
          }}
          itemStyle={{ color: tokens.onSurface, fontSize: 12, fontFamily: fonts.body }}
          labelFormatter={(label: string) => label}
          formatter={(value: number, name: string, props: any) => {
            if (name === 'base') {
              return [null, null]
            }
            const max: number = props?.payload?.max ?? value
            return [`$${max.toFixed(2)}`, 'Max']
          }}
        />
        {/* Invisible base bar — creates the floating effect */}
        <Bar
          dataKey="base"
          stackId="r"
          fill="transparent"
          isAnimationActive={false}
        />
        {/* Visible range bar */}
        <Bar
          dataKey="range"
          stackId="r"
          fill={tokens.secondary}
          radius={[3, 3, 0, 0]}
          isAnimationActive={false}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
