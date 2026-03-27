import { useState, useEffect } from 'react'
import type { Booking } from '../api/client'
import Icon from './Icon'
import ToggleSwitch from './ToggleSwitch'

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
  city: null,
  alert_enabled: false,
  target_price: null,
  email_notifications: true,
}

export default function BookingModal({ booking, onClose, onSave }: BookingModalProps) {
  const [form, setForm] = useState<Booking>(emptyBooking)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setForm(booking ? { ...emptyBooking, ...booking } : emptyBooking)
  }, [booking])

  const set = (key: keyof Booking, value: string | number | boolean | null) => {
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
      <div className="glass rounded-xl w-full max-w-lg p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-headline font-black text-on-surface">
            {booking ? 'Edit Booking' : 'Add Booking'}
          </h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface transition-colors">
            <Icon name="close" size={20} />
          </button>
        </div>
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
          <div className="grid grid-cols-2 gap-3">
            <Field label="Pickup Location">
              <input
                className="input-field"
                value={form.pickup_location}
                onChange={(e) => set('pickup_location', e.target.value)}
                required
              />
            </Field>
            <Field label="City (optional)">
              <input
                className="input-field"
                value={form.city ?? ''}
                onChange={(e) => set('city', e.target.value || null)}
                placeholder="San Francisco"
              />
            </Field>
          </div>
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
          <div className="grid grid-cols-2 gap-3">
            <Field label="Target Price (optional)">
              <input
                className="input-field"
                type="number"
                step="0.01"
                value={form.target_price ?? ''}
                onChange={(e) =>
                  set('target_price', e.target.value ? parseFloat(e.target.value) : null)
                }
                placeholder="250.00"
              />
            </Field>
            <div className="flex flex-col justify-end pb-1 gap-3">
              <ToggleSwitch
                checked={form.alert_enabled}
                onChange={(v) => set('alert_enabled', v)}
                label="Alerts"
              />
              <ToggleSwitch
                checked={form.email_notifications}
                onChange={(v) => set('email_notifications', v)}
                label="Email"
              />
            </div>
          </div>
          {error && <p className="text-sm text-error">{error}</p>}
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
      <label className="block text-xs font-body text-on-surface-variant mb-1">{label}</label>
      {children}
    </div>
  )
}
