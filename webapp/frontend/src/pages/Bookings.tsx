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
import Icon from '../components/Icon'
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
  if (error) return <div className="p-6 text-error">{error}</div>

  return (
    <div data-testid="page-bookings" className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-headline font-black text-on-surface">Bookings</h1>
        <button onClick={openAdd} className="btn-primary flex items-center gap-2">
          <Icon name="add" size={18} />
          Add Booking
        </button>
      </div>

      {bookings.length === 0 ? (
        <EmptyState icon="event_note" title="No bookings yet" description="Click Add Booking to get started." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-body text-on-surface-variant uppercase tracking-widest">
                <th className="py-3 px-3">Name</th>
                <th className="py-3 px-3">Location</th>
                <th className="py-3 px-3">City</th>
                <th className="py-3 px-3">Pick-up</th>
                <th className="py-3 px-3">Drop-off</th>
                <th className="py-3 px-3">Vehicle Type</th>
                <th className="py-3 px-3">Holding Price</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Alerts</th>
                <th className="py-3 px-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.map((b) => {
                const expired = isExpired(b.pickup_date)
                return (
                  <tr key={b.name} className="hover:bg-surface-container-high transition-colors">
                    <td className="py-3 px-3 text-on-surface font-medium">{b.name}</td>
                    <td className="py-3 px-3 text-on-surface-variant">{b.pickup_location}</td>
                    <td className="py-3 px-3 text-on-surface-variant">{b.city ?? '—'}</td>
                    <td className="py-3 px-3 text-on-surface-variant whitespace-nowrap">
                      {formatDate(b.pickup_date)}<br />
                      <span className="text-xs">{formatTime(b.pickup_time)}</span>
                    </td>
                    <td className="py-3 px-3 text-on-surface-variant whitespace-nowrap">
                      {formatDate(b.dropoff_date)}<br />
                      <span className="text-xs">{formatTime(b.dropoff_time)}</span>
                    </td>
                    <td className="py-3 px-3 text-on-surface-variant">{b.holding_vehicle_type ?? '—'}</td>
                    <td className="py-3 px-3 text-on-surface-variant">
                      {b.holding_price !== null ? `$${b.holding_price.toFixed(2)}` : '—'}
                    </td>
                    <td className="py-3 px-3">
                      <Badge label={expired ? 'Expired' : 'Active'} variant={expired ? 'error' : 'tertiary'} />
                    </td>
                    <td className="py-3 px-3">
                      {b.alert_enabled ? (
                        <Icon name="notifications_active" size={18} className="text-primary" />
                      ) : (
                        <Icon name="notifications_off" size={18} className="text-on-surface-variant" />
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openEdit(b)}
                          className="text-xs text-secondary hover:text-on-surface transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(b.name)}
                          className={`text-xs transition-colors ${confirmDelete === b.name ? 'text-error font-semibold' : 'text-on-surface-variant hover:text-error'}`}
                        >
                          {confirmDelete === b.name ? 'Confirm?' : 'Delete'}
                        </button>
                        {confirmDelete === b.name && (
                          <button
                            onClick={() => setConfirmDelete(null)}
                            className="text-xs text-on-surface-variant hover:text-on-surface transition-colors"
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
