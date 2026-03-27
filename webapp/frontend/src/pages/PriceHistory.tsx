import { useEffect, useState } from 'react'
import { getBookings, getPriceHistory, type Booking, type PriceHistory } from '../api/client'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import PriceChart from '../components/PriceChart'
import Icon from '../components/Icon'
import { buildChartData, getCategoryColors } from '../utils/chartData'
import { findBestRun, computeSavings } from '../utils/insights'

export default function PriceHistoryPage() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [selectedBooking, setSelectedBooking] = useState<string>('')
  const [history, setHistory] = useState<PriceHistory | null>(null)
  const [loadingBookings, setLoadingBookings] = useState(true)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getBookings()
      .then((bks) => {
        setBookings(bks)
        if (bks.length > 0) setSelectedBooking(bks[0].name)
      })
      .catch(() => setError('Failed to load bookings'))
      .finally(() => setLoadingBookings(false))
  }, [])

  useEffect(() => {
    if (!selectedBooking) return
    setLoadingHistory(true)
    setHistory(null)
    getPriceHistory(selectedBooking)
      .then(setHistory)
      .catch(() => setError('Failed to load price history'))
      .finally(() => setLoadingHistory(false))
  }, [selectedBooking])

  if (loadingBookings) return <LoadingSpinner label="Loading…" />
  if (error) return <div className="p-6 text-error">{error}</div>

  const categories = history ? Object.keys(history.categories) : []
  const colors = getCategoryColors(categories)
  const chartData = history
    ? buildChartData(history.run_dates, history.categories)
    : []

  const holdingCatPrices =
    history && history.holding_vehicle_type
      ? history.categories[history.holding_vehicle_type]
      : null
  const bestRun = holdingCatPrices
    ? findBestRun(history!.run_dates, holdingCatPrices)
    : null

  const latestPrices = history
    ? Object.values(history.categories)
        .map((prices) => prices[prices.length - 1])
        .filter((p): p is number => p !== undefined)
    : []
  const currentBest = latestPrices.length > 0 ? Math.min(...latestPrices) : null
  const savings = history ? computeSavings(history.holding_price, currentBest) : null

  return (
    <div data-testid="page-price-history" className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-headline font-black text-on-surface">Price History</h1>
        <select
          className="input-field w-auto min-w-48"
          value={selectedBooking}
          onChange={(e) => setSelectedBooking(e.target.value)}
        >
          {bookings.map((b) => (
            <option key={b.name} value={b.name}>
              {b.name}
            </option>
          ))}
        </select>
      </div>

      {loadingHistory && <LoadingSpinner label="Loading price history…" />}

      {!loadingHistory && history && (
        <>
          <Card title="Price Trends">
            {chartData.length === 0 ? (
              <EmptyState
                title="No price data"
                description="Run the tracker to collect price data."
                icon="show_chart"
              />
            ) : (
              <PriceChart
                data={chartData}
                categories={categories}
                colors={colors}
                holdingPrice={history.holding_price}
              />
            )}
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card variant="gradient" title="Best Time to Book">
              {bestRun ? (
                <div className="flex items-start gap-3">
                  <Icon name="star" size={20} className="text-primary mt-0.5" />
                  <div>
                    <p className="text-sm font-body text-on-surface">
                      <span className="text-tertiary font-semibold">{bestRun.date}</span>
                    </p>
                    <p className="text-xs font-body text-on-surface-variant mt-1">
                      {history.holding_vehicle_type} at{' '}
                      <span className="text-tertiary font-medium">${bestRun.price.toFixed(2)}</span>
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm font-body text-on-surface-variant">No holding vehicle set.</p>
              )}
            </Card>

            <Card variant="gradient" title="Savings Summary">
              {savings !== null ? (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm font-body">
                    <span className="text-on-surface-variant">Current best</span>
                    <span className="text-on-surface font-medium">
                      {currentBest !== null ? `$${currentBest.toFixed(2)}` : '—'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm font-body">
                    <span className="text-on-surface-variant">Holding price</span>
                    <span className="text-on-surface font-medium">
                      {history.holding_price !== null ? `$${history.holding_price.toFixed(2)}` : '—'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm font-body pt-2">
                    <span className="text-on-surface-variant">Savings</span>
                    <span className={`font-headline font-bold ${savings >= 0 ? 'text-tertiary' : 'text-error'}`}>
                      {savings >= 0 ? '+' : ''}${savings.toFixed(2)}
                    </span>
                  </div>
                </div>
              ) : (
                <p className="text-sm font-body text-on-surface-variant">No holding price set for comparison.</p>
              )}
            </Card>
          </div>
        </>
      )}

      {!loadingHistory && !history && bookings.length === 0 && (
        <EmptyState
          icon="show_chart"
          title="No bookings"
          description="Add a booking to view price history."
        />
      )}
    </div>
  )
}
