export function findBestRun(
  runDates: string[],
  prices: number[]
): { date: string; price: number } | null {
  if (!runDates.length || !prices.length) return null
  let minIdx = 0
  for (let i = 1; i < prices.length; i++) {
    if (prices[i] < prices[minIdx]) minIdx = i
  }
  return { date: runDates[minIdx], price: prices[minIdx] }
}

export function computeSavings(
  holdingPrice: number | null,
  currentBest: number | null
): number | null {
  if (holdingPrice === null || currentBest === null) return null
  return holdingPrice - currentBest
}
