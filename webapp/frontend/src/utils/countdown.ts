export function daysRemaining(pickupDate: string): number {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const pickup = new Date(pickupDate)
  pickup.setHours(0, 0, 0, 0)
  const diff = pickup.getTime() - today.getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

export function urgencyVariant(days: number): 'red' | 'yellow' | 'green' {
  if (days <= 7) return 'red'
  if (days <= 30) return 'yellow'
  return 'green'
}
