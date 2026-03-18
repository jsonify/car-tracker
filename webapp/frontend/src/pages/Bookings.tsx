import { useEffect, useState } from 'react'
import {
  getBookings,
  createBooking,
  updateBooking,
  deleteBooking,
  type Booking,
} from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Badge from '../components/Badge'
import BookingModal from '../components/BookingModal'
import { isExpired, formatDate, formatTime } from '../utils/dateTime'

export default function Bookings() {
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [editingBooking, setEditingBooking] = useState<Booking | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

  const load = () => {
    setLoading(true)
    getBookings()
      .then(setBookings)
      .catch(() => setError('Failed to load bookings'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleSave = async (b: Booking) => {
    if (editingBooking) {
      await updateBooking(editingBooking.name, b)
    } else {
      await createBooking(b)
    }
    load()
  }

  const handleDelete = async (name: string) => {
    if (confirmDelete !== name) {
      setConfirmDelete(name)
      return
    }
    await deleteBooking(name)
    setConfirmDelete(null)
    load()
  }

  const openAdd = () => { setEditingBooking(null); setModalOpen(true) }
  const openEdit = (b: Booking) => { setEditingBooking(b); setModalOpen(true) }
  const closeModal = () => { setModalOpen(false); setEditingBooking(null) }

  if (loading) return <LoadingSpinner label="Loading bookings…" />
  if (error) return <div className="p-6 text-red-400">{error}</div>

  return (
    <div data-testid="page-bookings" className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold text-gray-100">Bookings</h1>
        <button onClick={openAdd} className="btn-primary">+ Add Booking</button>
      </div>

      {bookings.length === 0 ? (
        <EmptyState icon="📋" title="No bookings yet" description="Click Add Booking to get started." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wider">
                <th className="py-2 px-3">Name</th>
                <th className="py-2 px-3">Location</th>
                <th className="py-2 px-3">Pick-up</th>
                <th className="py-2 px-3">Drop-off</th>
                <th className="py-2 px-3">Vehicle Type</th>
                <th className="py-2 px-3">Holding Price</th>
                <th className="py-2 px-3">Status</th>
                <th className="py-2 px-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => {
                const expired = isExpired(b.pickup_date)
                return (
                  <tr key={b.name} className="border-b border-gray-800 hover:bg-gray-800/40">
                    <td className="py-2 px-3 text-gray-200 font-medium">{b.name}</td>
                    <td className="py-2 px-3 text-gray-400">{b.pickup_location}</td>
                    <td className="py-2 px-3 text-gray-400 whitespace-nowrap">
                      {formatDate(b.pickup_date)}<br />
                      <span className="text-xs text-gray-500">{formatTime(b.pickup_time)}</span>
                    </td>
                    <td className="py-2 px-3 text-gray-400 whitespace-nowrap">
                      {formatDate(b.dropoff_date)}<br />
                      <span className="text-xs text-gray-500">{formatTime(b.dropoff_time)}</span>
                    </td>
                    <td className="py-2 px-3 text-gray-400">{b.holding_vehicle_type ?? '—'}</td>
                    <td className="py-2 px-3 text-gray-400">
                      {b.holding_price !== null ? `$${b.holding_price.toFixed(2)}` : '—'}
                    </td>
                    <td className="py-2 px-3">
                      <Badge label={expired ? 'Expired' : 'Active'} variant={expired ? 'red' : 'green'} />
                    </td>
                    <td className="py-2 px-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEdit(b)}
                          className="text-xs text-blue-400 hover:text-blue-300"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(b.name)}
                          className={`text-xs ${confirmDelete === b.name ? 'text-red-400 font-semibold' : 'text-gray-500 hover:text-red-400'}`}
                        >
                          {confirmDelete === b.name ? 'Confirm?' : 'Delete'}
                        </button>
                        {confirmDelete === b.name && (
                          <button
                            onClick={() => setConfirmDelete(null)}
                            className="text-xs text-gray-500 hover:text-gray-300"
                          >
                            Cancel
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen && (
        <BookingModal
          booking={editingBooking}
          onClose={closeModal}
          onSave={handleSave}
        />
      )}
    </div>
  )
}
