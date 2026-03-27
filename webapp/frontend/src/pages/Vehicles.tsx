import { useEffect, useState, useCallback } from 'react'
import { getVehicles, getBookings, type VehicleRow, type Booking } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Icon from '../components/Icon'
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
    if (sort !== col) return <Icon name="unfold_more" size={14} className="text-on-surface-variant/40 ml-1 inline-block" />
    return (
      <Icon
        name={order === 'asc' ? 'arrow_upward' : 'arrow_downward'}
        size={14}
        className="text-primary ml-1 inline-block"
      />
    )
  }

  return (
    <div data-testid="page-vehicles" className="p-6">
      <h1 className="text-lg font-headline font-black text-on-surface mb-5">Vehicles</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-5">
        <select
          className="input-field w-auto"
          value={filterBooking}
          onChange={(e) => { setFilterBooking(e.target.value); setOffset(0) }}
        >
          <option value="">All Bookings</option>
          {bookings.map((b) => (
            <option key={b.name} value={b.name}>{b.name}</option>
          ))}
        </select>
        <div className="relative">
          <Icon name="search" size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            className="input-field pl-9 w-48"
            placeholder="Search category…"
            value={filterCategory}
            onChange={(e) => { setFilterCategory(e.target.value); setOffset(0) }}
          />
        </div>
      </div>

      {loading ? (
        <LoadingSpinner label="Loading vehicles…" />
      ) : error ? (
        <div className="text-error">{error}</div>
      ) : vehicles.length === 0 ? (
        <EmptyState icon="directions_car" title="No vehicles found" description="Try adjusting your filters." />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-body text-on-surface-variant uppercase tracking-widest">
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
                      className="py-3 px-3 cursor-pointer select-none hover:text-on-surface transition-colors"
                      onClick={() => handleSort(key)}
                    >
                      {label}
                      <SortIndicator col={key} />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {vehicles.map((v, i) => (
                  <tr
                    key={v.id}
                    className={`hover:bg-surface-container-high transition-colors ${
                      i % 2 === 1 ? 'bg-surface-container/50' : ''
                    }`}
                  >
                    <td className="py-3 px-3 text-on-surface-variant whitespace-nowrap">{formatRunDate(v.run_at)}</td>
                    <td className="py-3 px-3 text-on-surface-variant">{v.booking_name}</td>
                    <td className="py-3 px-3 text-on-surface">{v.name}</td>
                    <td className="py-3 px-3 text-on-surface-variant">{v.brand ?? '—'}</td>
                    <td className="py-3 px-3 text-on-surface font-medium">{formatCurrency(v.total_price)}</td>
                    <td className="py-3 px-3 text-on-surface-variant">{formatCurrency(v.price_per_day)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center gap-3 mt-4 text-sm font-body text-on-surface-variant">
            <button
              onClick={() => setOffset(Math.max(0, offset - LIMIT))}
              disabled={offset === 0}
              className="btn-secondary disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span>Showing {offset + 1}–{offset + vehicles.length}</span>
            <button
              onClick={() => setOffset(offset + LIMIT)}
              disabled={vehicles.length < LIMIT}
              className="btn-secondary disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
