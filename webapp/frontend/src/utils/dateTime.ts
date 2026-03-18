export function isExpired(pickupDate: string): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const pickup = new Date(pickupDate)
  pickup.setHours(0, 0, 0, 0)
  return pickup < today
}

export function formatDate(d: string): string {
  const date = new Date(d + 'T00:00:00')
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function formatTime(t: string): string {
  const [hourStr, minuteStr] = t.split(':')
  const hour = parseInt(hourStr, 10)
  const minute = minuteStr || '00'
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 === 0 ? 12 : hour % 12
  return `${h12}:${minute} ${ampm}`
}
