import { useEffect, useState } from 'react'
import { getRuns, getRunVehicles, type RunSummary, type VehicleRow } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Icon from '../components/Icon'
import { formatCurrency } from '../utils/tableUtils'
import { isHoldingRun, isHoldingVehicle } from '../utils/runUtils'

export default function Runs() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [vehicleMap, setVehicleMap] = useState<Record<number, VehicleRow[]>>({})
  const [loadingVehicles, setLoadingVehicles] = useState<Record<number, boolean>>({})

  useEffect(() => {
    getRuns()
      .then(setRuns)
      .catch(() => setError('Failed to load runs'))
      .finally(() => setLoading(false))
  }, [])

  const toggleRow = (run: RunSummary) => {
    if (expandedId === run.id) {
      setExpandedId(null)
      return
    }
    setExpandedId(run.id)
    if (vehicleMap[run.id]) return
    setLoadingVehicles((prev) => ({ ...prev, [run.id]: true }))
    getRunVehicles(run.id)
      .then((vehicles) => setVehicleMap((prev) => ({ ...prev, [run.id]: vehicles })))
      .catch(() => setVehicleMap((prev) => ({ ...prev, [run.id]: [] })))
      .finally(() => setLoadingVehicles((prev) => ({ ...prev, [run.id]: false })))
  }

  if (loading) return <LoadingSpinner label="Loading runs…" />
  if (error) return <div className="p-6 text-error">{error}</div>

  return (
    <div data-testid="page-runs" className="p-6">
      <h1 className="text-lg font-headline font-black text-on-surface mb-5">Runs Log</h1>

      {runs.length === 0 ? (
        <EmptyState icon="history" title="No runs yet" description="Runs are recorded when the tracker scrapes prices." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs font-body text-on-surface-variant uppercase tracking-widest">
                <th className="py-3 px-3">ID</th>
                <th className="py-3 px-3">Date</th>
                <th className="py-3 px-3">Booking</th>
                <th className="py-3 px-3">Location</th>
                <th className="py-3 px-3">Vehicles</th>
                <th className="py-3 px-3">Holding Price</th>
                <th className="py-3 px-3 w-8"></th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => {
                const holding = isHoldingRun(run)
                const expanded = expandedId === run.id
                const vehicles = vehicleMap[run.id] ?? []
                const loadingV = loadingVehicles[run.id]

                return (
                  <>
                    <tr
                      key={run.id}
                      onClick={() => toggleRow(run)}
                      className={`cursor-pointer hover:bg-surface-container-high transition-colors ${
                        holding ? 'bg-primary/5' : ''
                      }`}
                    >
                      <td className="py-3 px-3 text-on-surface-variant">#{run.id}</td>
                      <td className="py-3 px-3 text-on-surface-variant whitespace-nowrap">
                        {new Date(run.run_at).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="py-3 px-3 text-on-surface">{run.booking_name}</td>
                      <td className="py-3 px-3 text-on-surface-variant">{run.pickup_location}</td>
                      <td className="py-3 px-3 text-on-surface-variant">{run.vehicle_count}</td>
                      <td className="py-3 px-3 text-on-surface-variant">
                        {run.holding_price !== null ? formatCurrency(run.holding_price) : '—'}
                      </td>
                      <td className="py-3 px-3">
                        <Icon
                          name={expanded ? 'expand_less' : 'expand_more'}
                          size={18}
                          className="text-on-surface-variant"
                        />
                      </td>
                    </tr>
                    {expanded && (
                      <tr key={`${run.id}-detail`}>
                        <td colSpan={7} className="px-4 py-3 bg-surface-container-high/50">
                          {loadingV ? (
                            <LoadingSpinner label="Loading vehicles…" />
                          ) : vehicles.length === 0 ? (
                            <p className="text-sm font-body text-on-surface-variant">No vehicles found for this run.</p>
                          ) : (
                            <table className="w-full text-sm">
                              <thead>
                                <tr className="text-xs font-body text-on-surface-variant uppercase tracking-widest text-left">
                                  <th className="py-2 px-2">#</th>
                                  <th className="py-2 px-2">Name</th>
                                  <th className="py-2 px-2">Brand</th>
                                  <th className="py-2 px-2">Total Price</th>
                                  <th className="py-2 px-2">$/Day</th>
                                </tr>
                              </thead>
                              <tbody>
                                {vehicles.map((v) => {
                                  const isHolding = isHoldingVehicle(v.name, run.holding_vehicle_type)
                                  return (
                                    <tr
                                      key={v.id}
                                      className={isHolding ? 'bg-primary/10' : ''}
                                    >
                                      <td className="py-2 px-2 text-on-surface-variant">{v.position}</td>
                                      <td className="py-2 px-2 text-on-surface">{v.name}</td>
                                      <td className="py-2 px-2 text-on-surface-variant">{v.brand ?? '—'}</td>
                                      <td className="py-2 px-2 text-on-surface font-medium">{formatCurrency(v.total_price)}</td>
                                      <td className="py-2 px-2 text-on-surface-variant">{formatCurrency(v.price_per_day)}</td>
                                    </tr>
                                  )
                                })}
                              </tbody>
                            </table>
                          )}
                        </td>
                      </tr>
                    )}
                  </>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
