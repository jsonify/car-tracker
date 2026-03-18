import { useEffect, useState } from 'react'
import { getDashboardSummary, type DashboardSummary } from '../api/client'
import Card from '../components/Card'
import Badge from '../components/Badge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import { daysRemaining, urgencyVariant } from '../utils/countdown'
import { rankVolatility } from '../utils/volatility'

const urgencyClasses: Record<'red' | 'yellow' | 'green', string> = {
  red: 'bg-red-900/40 border-red-700/50',
  yellow: 'bg-yellow-900/40 border-yellow-700/50',
  green: 'bg-green-900/40 border-green-700/50',
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getDashboardSummary()
      .then(setData)
      .catch(() => setError('Failed to load dashboard data'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner label="Loading dashboard…" />
  if (error) return <div className="p-6 text-red-400">{error}</div>
  if (!data) return <EmptyState title="No data available" />

  const totalSavings = data.bookings.reduce((sum, b) => sum + (b.savings ?? 0), 0)
  const topVolatile = rankVolatility(data.volatile_categories).slice(0, 3)

  return (
    <div data-testid="page-dashboard" className="p-6 space-y-6">
      <h1 className="text-xl font-semibold text-gray-100">Dashboard</h1>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Active Bookings</p>
          <p className="text-3xl font-bold text-gray-100">{data.active_booking_count}</p>
        </Card>
        <Card>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Total Runs</p>
          <p className="text-3xl font-bold text-gray-100">{data.total_run_count}</p>
        </Card>
        <Card>
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Total Savings</p>
          <p className={`text-3xl font-bold ${totalSavings >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {totalSavings >= 0 ? '+' : ''}${totalSavings.toFixed(2)}
          </p>
        </Card>
      </div>

      {/* Booking timeline */}
      <Card title="Booking Timeline">
        {data.bookings.length === 0 ? (
          <EmptyState title="No active bookings" description="Add a booking to get started." />
        ) : (
          <div className="space-y-3">
            {data.bookings.map((b) => {
              const days = daysRemaining(b.pickup_date)
              const variant = urgencyVariant(days)
              return (
                <div
                  key={b.name}
                  className={`border rounded-lg px-4 py-3 flex items-center justify-between ${urgencyClasses[variant]}`}
                >
                  <div>
                    <p className="text-sm font-medium text-gray-100">{b.name}</p>
                    <p className="text-xs text-gray-400">{b.pickup_location}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    {b.savings !== null && (
                      <Badge
                        label={`${b.savings >= 0 ? '+' : ''}$${b.savings.toFixed(2)}`}
                        variant={b.savings >= 0 ? 'green' : 'red'}
                      />
                    )}
                    <span className="text-xs text-gray-400 whitespace-nowrap">
                      {days > 0 ? `${days}d left` : days === 0 ? 'Today' : 'Past'}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Price volatility */}
        <Card title="Price Volatility (Top 3)">
          {topVolatile.length === 0 ? (
            <EmptyState title="No volatility data" />
          ) : (
            <div className="space-y-2">
              {topVolatile.map((v) => (
                <div key={`${v.booking_name}-${v.category}`} className="flex items-center justify-between py-1">
                  <div>
                    <p className="text-sm text-gray-200">{v.category}</p>
                    <p className="text-xs text-gray-500">{v.booking_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-yellow-400">±${v.range.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">
                      ${v.min_price.toFixed(0)} – ${v.max_price.toFixed(0)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Recent runs */}
        <Card title="Recent Runs">
          {data.recent_runs.length === 0 ? (
            <EmptyState title="No recent runs" />
          ) : (
            <div className="space-y-2">
              {data.recent_runs.map((r) => (
                <div key={r.id} className="flex items-center justify-between py-1 border-b border-gray-800 last:border-0">
                  <div>
                    <p className="text-sm text-gray-200">{r.booking_name}</p>
                    <p className="text-xs text-gray-500">{r.pickup_location}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">{r.vehicle_count} vehicles</p>
                    <p className="text-xs text-gray-500">
                      {new Date(r.run_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
