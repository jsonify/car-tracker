import { useEffect, useState } from 'react'
import { getDashboardSummary, type DashboardSummary } from '../api/client'
import Card from '../components/Card'
import Badge from '../components/Badge'
import StatsCard from '../components/StatsCard'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Icon from '../components/Icon'
import { daysRemaining, urgencyVariant } from '../utils/countdown'
import { rankVolatility } from '../utils/volatility'

const urgencyBadgeVariant: Record<'red' | 'yellow' | 'green', 'error' | 'primary' | 'tertiary'> = {
  red: 'error',
  yellow: 'primary',
  green: 'tertiary',
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
  if (error) return <div className="p-6 text-error">{error}</div>
  if (!data) return <EmptyState title="No data available" />

  const topVolatile = rankVolatility(data.volatile_categories).slice(0, 3)

  return (
    <div data-testid="page-dashboard" className="p-6 space-y-6">
      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          label="Active Bookings"
          value={String(data.active_booking_count)}
          icon="event_note"
        />
        <StatsCard
          label="Total Runs"
          value={String(data.total_run_count)}
          icon="history"
        />
        <StatsCard
          label="Total Savings"
          value={`$${data.total_savings.toFixed(2)}`}
          icon="savings"
          trend={data.total_savings !== 0 ? {
            direction: data.total_savings > 0 ? 'up' : 'down',
            text: data.total_savings > 0 ? 'Saving money' : 'Prices increased',
          } : undefined}
        />
        <StatsCard
          label="Active Alerts"
          value={String(data.alert_count)}
          icon="notifications_active"
        />
      </div>

      {/* Booking timeline */}
      <Card title="Upcoming Bookings">
        {data.bookings.length === 0 ? (
          <EmptyState title="No active bookings" description="Add a booking to get started." icon="event_note" />
        ) : (
          <div className="space-y-2">
            {data.bookings.map((b) => {
              const days = daysRemaining(b.pickup_date)
              const variant = urgencyVariant(days)
              return (
                <div
                  key={b.name}
                  className="flex items-center justify-between rounded-lg px-4 py-3 bg-surface-container-high hover:bg-surface-container-highest transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Icon name="directions_car" size={20} className="text-on-surface-variant" />
                    <div>
                      <p className="text-sm font-body font-medium text-on-surface">{b.name}</p>
                      <p className="text-xs font-body text-on-surface-variant">{b.pickup_location}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {b.savings !== null && (
                      <Badge
                        label={`${b.savings >= 0 ? '+' : ''}$${b.savings.toFixed(2)}`}
                        variant={b.savings >= 0 ? 'tertiary' : 'error'}
                      />
                    )}
                    <Badge
                      label={days > 0 ? `${days}d left` : days === 0 ? 'Today' : 'Past'}
                      variant={urgencyBadgeVariant[variant]}
                    />
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
            <EmptyState title="No volatility data" icon="trending_flat" />
          ) : (
            <div className="space-y-2">
              {topVolatile.map((v) => (
                <div key={`${v.booking_name}-${v.category}`} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-surface-container-high transition-colors">
                  <div>
                    <p className="text-sm font-body text-on-surface">{v.category}</p>
                    <p className="text-xs font-body text-on-surface-variant">{v.booking_name}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-headline font-bold text-primary">±${v.range.toFixed(2)}</p>
                    <p className="text-xs font-body text-on-surface-variant">
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
            <EmptyState title="No recent runs" icon="history" />
          ) : (
            <div className="space-y-2">
              {data.recent_runs.map((r) => (
                <div key={r.id} className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-surface-container-high transition-colors">
                  <div className="flex items-center gap-3">
                    <Icon name="play_circle" size={18} className="text-on-surface-variant" />
                    <div>
                      <p className="text-sm font-body text-on-surface">{r.booking_name}</p>
                      <p className="text-xs font-body text-on-surface-variant">{r.pickup_location}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-body text-on-surface-variant">{r.vehicle_count} vehicles</p>
                    <p className="text-xs font-body text-on-surface-variant">
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
