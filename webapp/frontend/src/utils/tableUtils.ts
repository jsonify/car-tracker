export function formatCurrency(n: number): string {
  return `$${n.toFixed(2)}`
}

export function formatRunDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }) + ' ' + date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: false,
  })
}

export function toggleSort(
  current: string,
  col: string,
  order: 'asc' | 'desc'
): { sort: string; order: 'asc' | 'desc' } {
  if (current === col) {
    return { sort: col, order: order === 'asc' ? 'desc' : 'asc' }
  }
  return { sort: col, order: 'asc' }
}
