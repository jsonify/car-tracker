import { useEffect, useState } from 'react'
import { getBookings, getPriceHistory, type Booking, type PriceHistory } from '../api/client'
import Card from '../components/Card'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import PriceChart from '../components/PriceChart'
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
  if (error) return <div className="p-6 text-red-400">{error}</div>

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
        <h1 className="text-xl font-semibold text-gray-100">Price History</h1>
        <select
          className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
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

          <Card title="Insights">
            <div className="space-y-4">
              {bestRun && (
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
                    Best Time to Book
                  </p>
                  <p className="text-sm text-gray-200">
                    <span className="text-green-400 font-semibold">{bestRun.date}</span>{' '}—{' '}
                    {history.holding_vehicle_type} at{' '}
                    <span className="text-green-400">${bestRun.price.toFixed(2)}</span>
                  </p>
                </div>
              )}
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
                  Savings Summary
                </p>
                {savings !== null ? (
                  <p className="text-sm text-gray-200">
                    Current best:{' '}
                    <span className="text-gray-100 font-medium">
                      {currentBest !== null ? `$${currentBest.toFixed(2)}` : '—'}
                    </span>{' '}
                    vs holding:{' '}
                    <span className="text-gray-100 font-medium">
                      {history.holding_price !== null
                        ? `$${history.holding_price.toFixed(2)}`
                        : '—'}
                    </span>{' '}
                    →{' '}
                    <span
                      className={
                        savings >= 0
                          ? 'text-green-400 font-semibold'
                          : 'text-red-400 font-semibold'
                      }
                    >
                      {savings >= 0 ? '+' : ''}${savings.toFixed(2)} savings
                    </span>
                  </p>
                ) : (
                  <p className="text-sm text-gray-500">No holding price set for comparison.</p>
                )}
              </div>
            </div>
          </Card>
        </>
      )}

      {!loadingHistory && !history && bookings.length === 0 && (
        <EmptyState
          icon="📈"
          title="No bookings"
          description="Add a booking to view price history."
        />
      )}
    </div>
  )
}
