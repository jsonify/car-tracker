import type { RunSummary } from '../api/client'

export function isHoldingRun(run: RunSummary): boolean {
  return run.holding_price !== null
}

export function isHoldingVehicle(vehicleName: string, holdingType: string | null): boolean {
  if (!holdingType) return false
  return vehicleName === holdingType
}
