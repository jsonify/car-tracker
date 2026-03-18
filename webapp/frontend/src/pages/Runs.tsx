import { useEffect, useState } from 'react'
import { getRuns, getRunVehicles, type RunSummary, type VehicleRow } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
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
  if (error) return <div className="p-6 text-red-400">{error}</div>

  return (
    <div data-testid="page-runs" className="p-6">
      <h1 className="text-xl font-semibold text-gray-100 mb-4">Runs Log</h1>

      {runs.length === 0 ? (
        <EmptyState icon="🔄" title="No runs yet" description="Runs are recorded when the tracker scrapes prices." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-gray-800 text-left text-xs text-gray-500 uppercase tracking-wider">
                <th className="py-2 px-3">ID</th>
                <th className="py-2 px-3">Date</th>
                <th className="py-2 px-3">Booking</th>
                <th className="py-2 px-3">Location</th>
                <th className="py-2 px-3">Vehicles</th>
                <th className="py-2 px-3">Holding Price</th>
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
                      className={`border-b border-gray-800 cursor-pointer hover:bg-gray-800/40 ${
                        holding ? 'bg-yellow-900/20' : ''
                      }`}
                    >
                      <td className="py-2 px-3 text-gray-500">#{run.id}</td>
                      <td className="py-2 px-3 text-gray-400 whitespace-nowrap">
                        {new Date(run.run_at).toLocaleString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="py-2 px-3 text-gray-200">{run.booking_name}</td>
                      <td className="py-2 px-3 text-gray-400">{run.pickup_location}</td>
                      <td className="py-2 px-3 text-gray-400">{run.vehicle_count}</td>
                      <td className="py-2 px-3 text-gray-400">
                        {run.holding_price !== null ? formatCurrency(run.holding_price) : '—'}
                      </td>
                    </tr>
                    {expanded && (
                      <tr key={`${run.id}-detail`} className="border-b border-gray-800">
                        <td colSpan={6} className="px-4 py-3 bg-gray-900/60">
                          {loadingV ? (
                            <LoadingSpinner label="Loading vehicles…" />
                          ) : vehicles.length === 0 ? (
                            <p className="text-sm text-gray-500">No vehicles found for this run.</p>
                          ) : (
                            <table className="w-full text-sm">
                              <thead>
                                <tr className="text-xs text-gray-500 uppercase tracking-wider text-left">
                                  <th className="py-1 px-2">#</th>
                                  <th className="py-1 px-2">Name</th>
                                  <th className="py-1 px-2">Brand</th>
                                  <th className="py-1 px-2">Total Price</th>
                                  <th className="py-1 px-2">$/Day</th>
                                </tr>
                              </thead>
                              <tbody>
                                {vehicles.map((v) => {
                                  const isHolding = isHoldingVehicle(v.name, run.holding_vehicle_type)
                                  return (
                                    <tr
                                      key={v.id}
                                      className={`border-t border-gray-800 ${isHolding ? 'bg-indigo-900/20' : ''}`}
                                    >
                                      <td className="py-1 px-2 text-gray-500">{v.position}</td>
                                      <td className="py-1 px-2 text-gray-200">{v.name}</td>
                                      <td className="py-1 px-2 text-gray-400">{v.brand ?? '—'}</td>
                                      <td className="py-1 px-2 text-gray-200 font-medium">{formatCurrency(v.total_price)}</td>
                                      <td className="py-1 px-2 text-gray-400">{formatCurrency(v.price_per_day)}</td>
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
