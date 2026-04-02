import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { LatestPricePoint } from '../utils/chartData'
import { colors as tokens, fonts } from '../styles/tokens'

interface LatestPricesChartProps {
  data: LatestPricePoint[]
}

export default function LatestPricesChart({ data }: LatestPricesChartProps) {
  if (data.length === 0) {
    return <p data-testid="empty-message">No data available.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(200, data.length * 28)}>
      <BarChart
        layout="vertical"
        data={data}
        margin={{ top: 8, right: 16, left: 0, bottom: 8 }}
      >
        <CartesianGrid horizontal={false} stroke={tokens.outlineVariant} />
        <YAxis
          dataKey="category"
          type="category"
          width={120}
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 10, fontFamily: fonts.body }}
          tickLine={false}
          axisLine={false}
        />
        <XAxis
          type="number"
          tickFormatter={(v) => `$${v}`}
          tick={{ fill: tokens.onSurfaceVariant, fontSize: 11, fontFamily: fonts.body }}
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
          formatter={(v: number) => [`$${v.toFixed(2)}`, 'Latest Price']}
        />
        <Bar
          dataKey="price"
          fill={tokens.primary}
          radius={[0, 3, 3, 0]}
          maxBarSize={20}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
