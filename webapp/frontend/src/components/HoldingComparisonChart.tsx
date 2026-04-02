import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { HoldingComparisonData } from '../utils/chartData'
import { colors as tokens, fonts } from '../styles/tokens'

interface HoldingComparisonChartProps {
  data: HoldingComparisonData | null
  holdingVehicleType: string | null
}

export default function HoldingComparisonChart({
  data,
  holdingVehicleType,
}: HoldingComparisonChartProps) {
  if (data === null) {
    return (
      <p
        data-testid="no-holding-message"
        className="text-sm font-body text-on-surface-variant"
      >
        No holding price configured.
      </p>
    )
  }

  const chartData = [
    {
      name: holdingVehicleType ?? 'Vehicle',
      holding: data.holdingPrice,
      current: data.currentBest,
    },
  ]

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={chartData} margin={{ top: 16, right: 16, left: 10, bottom: 8 }}>
        <XAxis
          dataKey="name"
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 11, fontFamily: fonts.body }}
          tickLine={false}
          stroke={tokens.outlineVariant}
          fontSize={11}
        />
        <YAxis
          tickFormatter={(v: number) => `$${v}`}
          domain={['auto', 'auto']}
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 11, fontFamily: fonts.body }}
          tickLine={false}
          axisLine={false}
          fontSize={11}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: tokens.surfaceContainerHigh,
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          }}
          labelStyle={{ color: tokens.onSurfaceVariant, fontSize: 12, fontFamily: fonts.headline, fontWeight: 700 }}
          itemStyle={{ color: tokens.onSurface, fontSize: 12, fontFamily: fonts.body }}
          formatter={(v: number, name: string) => [`$${v.toFixed(2)}`, name]}
        />
        <Legend
          wrapperStyle={{ fontSize: 12, fontFamily: fonts.body, color: tokens.onSurfaceVariant }}
        />
        <Bar
          dataKey="holding"
          fill={tokens.primary}
          name="Holding"
          radius={[3, 3, 0, 0]}
          maxBarSize={60}
        />
        <Bar
          dataKey="current"
          fill={tokens.tertiary}
          name="Current Best"
          radius={[3, 3, 0, 0]}
          maxBarSize={60}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
