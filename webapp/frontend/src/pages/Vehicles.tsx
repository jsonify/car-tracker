import { useEffect, useState, useCallback } from 'react'
import { getVehicles, getBookings, type VehicleRow, type Booking } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import { formatCurrency, formatRunDate, toggleSort } from '../utils/tableUtils'

const LIMIT = 50

export default function Vehicles() {
  const [vehicles, setVehicles] = useState<VehicleRow[]>([])
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [filterBooking, setFilterBooking] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [sort, setSort] = useState('run_at')
  const [order, setOrder] = useState<'asc' | 'desc'>('desc')
  const [offset, setOffset] = useState(0)

  const load = useCallback(() => {
    setLoading(true)
    const params: Record<string, string | number> = { limit: LIMIT, offset, sort, order }
    if (filterBooking) params.booking_name = filterBooking
    if (filterCategory) params.category = filterCategory
    getVehicles(params)
      .then(setVehicles)
      .catch(() => setError('Failed to load vehicles'))
      .finally(() => setLoading(false))
  }, [filterBooking, filterCategory, sort, order, offset])

  useEffect(() => {
    getBookings().then(setBookings).catch(() => {})
  }, [])

  useEffect(() => { load() }, [load])

  const handleSort = (col: string) => {
    const next = toggleSort(sort, col, order)
    setSort(next.sort)
    setOrder(next.order)
    setOffset(0)
  }

  const SortIndicator = ({ col }: { col: string }) => {
    if (sort !== col) return <span className="text-gray-600 ml-1">↕</span>
    return <span className="text-indigo-400 ml-1">{order === 'asc' ? '↑' : '↓'}</span>
  }

  return (
    <div data-testid="page-vehicles" className="p-6">
      <h1 className="text-xl font-semibold text-gray-100 mb-4">Vehicles</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <select
          className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
          value={filterBooking}
          onChange={(e) => { setFilterBooking(e.target.value); setOffset(0) }}
        >
          <option value="">All Bookings</option>
          {bookings.map((b) => (
            <option key={b.name} value={b.name}>{b.name}</option>
          ))}
        </select>
        <input
          className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500 w-48"
          placeholder="Search category…"
          value={filterCategory}
          onChange={(e) => { setFilterCategory(e.target.value); setOffset(0) }}
        />
      </div>

      {loading ? (
        <LoadingSpinner label="Loading vehicles…" />
      ) : error ? (
        <div className="text-red-400">{error}</div>
      ) : vehicles.length === 0 ? (
        <EmptyState icon="🚗" title="No vehicles found" description="Try adjusting your filters." />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wider">
                  {[
                    { key: 'run_at', label: 'Run Date' },
                    { key: 'booking_name', label: 'Booking' },
                    { key: 'name', label: 'Vehicle' },
                    { key: 'brand', label: 'Brand' },
                    { key: 'total_price', label: 'Total Price' },
                    { key: 'price_per_day', label: '$/Day' },
                  ].map(({ key, label }) => (
                    <th
                      key={key}
                      className="py-2 px-3 cursor-pointer select-none hover:text-gray-300"
                      onClick={() => handleSort(key)}
                    >
                      {label}
                      <SortIndicator col={key} />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {vehicles.map((v) => (
                  <tr key={v.id} className="border-b border-gray-800 hover:bg-gray-800/40">
                    <td className="py-2 px-3 text-gray-400 whitespace-nowrap">{formatRunDate(v.run_at)}</td>
                    <td className="py-2 px-3 text-gray-400">{v.booking_name}</td>
                    <td className="py-2 px-3 text-gray-200">{v.name}</td>
                    <td className="py-2 px-3 text-gray-400">{v.brand ?? '—'}</td>
                    <td className="py-2 px-3 text-gray-200 font-medium">{formatCurrency(v.total_price)}</td>
                    <td className="py-2 px-3 text-gray-400">{formatCurrency(v.price_per_day)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center gap-3 mt-4 text-sm text-gray-400">
            <button
              onClick={() => setOffset(Math.max(0, offset - LIMIT))}
              disabled={offset === 0}
              className="px-3 py-1 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span>Showing {offset + 1}–{offset + vehicles.length}</span>
            <button
              onClick={() => setOffset(offset + LIMIT)}
              disabled={vehicles.length < LIMIT}
              className="px-3 py-1 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
