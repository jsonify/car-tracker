import {
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts'
import type { PriceChangePoint } from '../utils/chartData'
import { colors as tokens, fonts } from '../styles/tokens'

interface PriceChangeChartProps {
  data: PriceChangePoint[]
}

export default function PriceChangeChart({ data }: PriceChangeChartProps) {
  if (data.length === 0) {
    return <p data-testid="empty-message">No data available.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 10, bottom: 60 }}>
        <XAxis
          dataKey="category"
          angle={-45}
          textAnchor="end"
          interval={0}
          fontSize={10}
          tick={{ fill: tokens.onSurfaceVariant, fontFamily: fonts.body }}
          tickLine={false}
          stroke={tokens.outlineVariant}
        />
        <YAxis
          tickFormatter={(v: number) => v >= 0 ? `+$${v}` : `-$${Math.abs(v)}`}
          fontSize={11}
          tick={{ fill: tokens.onSurfaceVariant, fontFamily: fonts.body }}
          tickLine={false}
          axisLine={false}
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
          formatter={(v: number) => [
            v >= 0 ? `+$${v.toFixed(2)}` : `-$${Math.abs(v).toFixed(2)}`,
            'Change',
          ]}
        />
        <ReferenceLine y={0} stroke={tokens.outlineVariant} />
        <Bar dataKey="delta">
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.delta < 0 ? tokens.tertiary : tokens.error}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
