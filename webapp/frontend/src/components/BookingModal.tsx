import { useState, useEffect } from 'react'
import type { Booking } from '../api/client'

interface BookingModalProps {
  booking?: Booking | null
  onClose: () => void
  onSave: (b: Booking) => Promise<void>
}

const emptyBooking: Booking = {
  name: '',
  pickup_location: '',
  pickup_date: '',
  pickup_time: '',
  dropoff_date: '',
  dropoff_time: '',
  holding_price: null,
  holding_vehicle_type: null,
}

export default function BookingModal({ booking, onClose, onSave }: BookingModalProps) {
  const [form, setForm] = useState<Booking>(emptyBooking)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setForm(booking ? { ...booking } : emptyBooking)
  }, [booking])

  const set = (key: keyof Booking, value: string | number | null) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await onSave(form)
      onClose()
    } catch {
      setError('Failed to save booking.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-lg p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-gray-100 mb-4">
          {booking ? 'Edit Booking' : 'Add Booking'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Name">
            <input
              className="input-field"
              value={form.name}
              onChange={(e) => set('name', e.target.value)}
              required
              disabled={!!booking}
            />
          </Field>
          <Field label="Pickup Location">
            <input
              className="input-field"
              value={form.pickup_location}
              onChange={(e) => set('pickup_location', e.target.value)}
              required
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Pickup Date (YYYY-MM-DD)">
              <input
                className="input-field"
                value={form.pickup_date}
                onChange={(e) => set('pickup_date', e.target.value)}
                placeholder="2026-04-01"
                required
              />
            </Field>
            <Field label="Pickup Time (HH:MM)">
              <input
                className="input-field"
                value={form.pickup_time}
                onChange={(e) => set('pickup_time', e.target.value)}
                placeholder="10:00"
                required
              />
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Drop-off Date (YYYY-MM-DD)">
              <input
                className="input-field"
                value={form.dropoff_date}
                onChange={(e) => set('dropoff_date', e.target.value)}
                placeholder="2026-04-08"
                required
              />
            </Field>
            <Field label="Drop-off Time (HH:MM)">
              <input
                className="input-field"
                value={form.dropoff_time}
                onChange={(e) => set('dropoff_time', e.target.value)}
                placeholder="10:00"
                required
              />
            </Field>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Holding Price (optional)">
              <input
                className="input-field"
                type="number"
                step="0.01"
                value={form.holding_price ?? ''}
                onChange={(e) =>
                  set('holding_price', e.target.value ? parseFloat(e.target.value) : null)
                }
                placeholder="299.00"
              />
            </Field>
            <Field label="Holding Vehicle Type (optional)">
              <input
                className="input-field"
                value={form.holding_vehicle_type ?? ''}
                onChange={(e) => set('holding_vehicle_type', e.target.value || null)}
                placeholder="Economy Car"
              />
            </Field>
          </div>
          {error && <p className="text-sm text-red-400">{error}</p>}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs text-gray-400 mb-1">{label}</label>
      {children}
    </div>
  )
}
