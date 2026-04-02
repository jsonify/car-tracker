import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { ChartPoint } from '../utils/chartData'
import { colors as tokens, fonts } from '../styles/tokens'
import { formatRunDate } from '../utils/dateUtils'

interface PriceChartProps {
  data: ChartPoint[]
  categories: string[]
  colors: Record<string, string>
  holdingPrice: number | null
}

export default function PriceChart({ data, categories, colors, holdingPrice }: PriceChartProps) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 110, left: 10, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={tokens.outlineVariant} />
        <XAxis
          dataKey="date"
          tickFormatter={formatRunDate}
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 11, fontFamily: fonts.body }}
          tickLine={false}
          stroke={tokens.outlineVariant}
        />
        <YAxis
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 11, fontFamily: fonts.body }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => `$${v}`}
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
          labelFormatter={formatRunDate}
          formatter={(value: number, name: string) => [`$${value.toFixed(2)}`, name]}
        />
        <Legend
          wrapperStyle={{ fontSize: 12, fontFamily: fonts.body, color: tokens.onSurfaceVariant }}
        />
        {holdingPrice !== null && (
          <ReferenceLine
            y={holdingPrice}
            stroke={tokens.primary}
            strokeDasharray="4 4"
            label={{
              value: `Holding $${holdingPrice.toFixed(2)}`,
              fill: tokens.primary,
              fontSize: 11,
              fontFamily: fonts.headline,
              position: 'insideTopRight',
            }}
          />
        )}
        {categories.map((cat) => (
          <Line
            key={cat}
            type="monotone"
            dataKey={cat}
            stroke={colors[cat]}
            dot={false}
            strokeWidth={2}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
