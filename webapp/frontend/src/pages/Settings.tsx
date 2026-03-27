import { useEffect, useState } from 'react'
import {
  getAlertSettings,
  updateAlertSettings,
  getBookings,
  type AlertConfig,
  type Booking,
} from '../api/client'
import Card from '../components/Card'
import ToggleSwitch from '../components/ToggleSwitch'
import LoadingSpinner from '../components/LoadingSpinner'
import Icon from '../components/Icon'

export default function Settings() {
  const [alerts, setAlerts] = useState<AlertConfig[]>([])
  const [bookings, setBookings] = useState<Booking[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    Promise.all([getAlertSettings(), getBookings()])
      .then(([alertData, bookingData]) => {
        setAlerts(alertData.alerts)
        setBookings(bookingData)
      })
      .catch(() => setError('Failed to load settings'))
      .finally(() => setLoading(false))
  }, [])

  const updateAlert = (bookingName: string, patch: Partial<AlertConfig>) => {
    setAlerts((prev) =>
      prev.map((a) => (a.booking_name === bookingName ? { ...a, ...patch } : a))
    )
    setSuccess(false)
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const result = await updateAlertSettings(alerts)
      setAlerts(result.alerts)
      setSuccess(true)
    } catch {
      setError('Failed to save settings.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingSpinner label="Loading settings…" />

  // Build alert list: merge existing alerts with bookings that have none
  const alertMap = new Map(alerts.map((a) => [a.booking_name, a]))
  const mergedAlerts: AlertConfig[] = bookings.map((b) =>
    alertMap.get(b.name) ?? {
      booking_name: b.name,
      alert_enabled: false,
      target_price: null,
      email_notifications: true,
    }
  )

  return (
    <div data-testid="page-settings" className="p-6 space-y-6">
      <h1 className="text-lg font-headline font-black text-on-surface">Settings & Alerts</h1>

      {error && (
        <div className="flex items-center gap-2 text-error text-sm font-body bg-error/10 rounded-lg px-4 py-3">
          <Icon name="error" size={18} />
          {error}
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 text-tertiary text-sm font-body bg-tertiary/10 rounded-lg px-4 py-3">
          <Icon name="check_circle" size={18} />
          Settings saved successfully.
        </div>
      )}

      <Card title="Alert Monitors">
        {mergedAlerts.length === 0 ? (
          <p className="text-sm font-body text-on-surface-variant">No bookings available. Add a booking first.</p>
        ) : (
          <div className="space-y-4">
            {mergedAlerts.map((alert) => (
              <div
                key={alert.booking_name}
                className="flex flex-col sm:flex-row sm:items-center gap-4 rounded-lg bg-surface-container-high p-4"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-body font-medium text-on-surface truncate">
                    {alert.booking_name}
                  </p>
                </div>
                <div className="flex items-center gap-6 flex-wrap">
                  <ToggleSwitch
                    checked={alert.alert_enabled}
                    onChange={(v) => updateAlert(alert.booking_name, { alert_enabled: v })}
                    label="Alerts"
                  />
                  <ToggleSwitch
                    checked={alert.email_notifications}
                    onChange={(v) => updateAlert(alert.booking_name, { email_notifications: v })}
                    label="Email"
                  />
                  <div className="flex items-center gap-2">
                    <label className="text-xs font-body text-on-surface-variant">Target $</label>
                    <input
                      type="number"
                      step="0.01"
                      className="input-field w-24 text-sm"
                      value={alert.target_price ?? ''}
                      onChange={(e) =>
                        updateAlert(alert.booking_name, {
                          target_price: e.target.value ? parseFloat(e.target.value) : null,
                        })
                      }
                      placeholder="250"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <div className="flex justify-end">
        <button onClick={handleSave} disabled={saving} className="btn-primary">
          {saving ? 'Saving…' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
