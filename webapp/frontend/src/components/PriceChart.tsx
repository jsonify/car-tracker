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

interface PriceChartProps {
  data: ChartPoint[]
  categories: string[]
  colors: Record<string, string>
  holdingPrice: number | null
}

export default function PriceChart({ data, categories, colors, holdingPrice }: PriceChartProps) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data} margin={{ top: 8, right: 20, left: 10, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="date"
          tick={{ fill: '#9ca3af', fontSize: 11 }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: '#9ca3af', fontSize: 11 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => `$${v}`}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
          labelStyle={{ color: '#9ca3af', fontSize: 12 }}
          formatter={(value: number) => [`$${value.toFixed(2)}`, undefined]}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: '#9ca3af' }} />
        {holdingPrice !== null && (
          <ReferenceLine
            y={holdingPrice}
            stroke="#fbbf24"
            strokeDasharray="4 4"
            label={{ value: `Holding $${holdingPrice.toFixed(2)}`, fill: '#fbbf24', fontSize: 11, position: 'right' }}
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
