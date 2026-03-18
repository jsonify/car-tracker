import type { VolatileCategory } from '../api/client'

export function rankVolatility(categories: VolatileCategory[]): VolatileCategory[] {
  return [...categories].sort((a, b) => b.range - a.range)
}
