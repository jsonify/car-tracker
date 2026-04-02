export interface ChartPoint {
  date: string
  [category: string]: number | string
}

export interface PriceRangePoint {
  category: string
  min: number
  max: number
  range: number
}

export interface LatestPricePoint {
  category: string
  price: number
}

export interface PriceChangePoint {
  category: string
  delta: number
  pctChange: number
}

export interface HoldingComparisonData {
  holdingPrice: number
  currentBest: number
}

const COLORS = [
  '#818cf8',
  '#34d399',
  '#fb923c',
  '#f472b6',
  '#a78bfa',
  '#38bdf8',
  '#fbbf24',
  '#4ade80',
]

export function buildChartData(
  runDates: string[],
  categories: Record<string, number[]>
): ChartPoint[] {
  return runDates.map((date, i) => {
    const point: ChartPoint = { date }
    for (const [cat, prices] of Object.entries(categories)) {
      point[cat] = prices[i] ?? 0
    }
    return point
  })
}

export function getCategoryColors(categories: string[]): Record<string, string> {
  return Object.fromEntries(
    categories.map((cat, i) => [cat, COLORS[i % COLORS.length]])
  )
}

export function buildPriceRangeData(
  categories: Record<string, number[]>,
  visibleCats: string[]
): PriceRangePoint[] {
  return visibleCats
    .filter((cat) => categories[cat] && categories[cat].length > 0)
    .map((cat) => {
      const prices = categories[cat]
      const min = Math.min(...prices)
      const max = Math.max(...prices)
      return { category: cat, min, max, range: max - min }
    })
}

export function buildLatestPricesData(
  categories: Record<string, number[]>,
  visibleCats: string[]
): LatestPricePoint[] {
  return visibleCats
    .filter((cat) => categories[cat] && categories[cat].length > 0)
    .map((cat) => {
      const prices = categories[cat]
      return { category: cat, price: prices[prices.length - 1] }
    })
    .sort((a, b) => a.price - b.price)
}

export function buildPriceChangeData(
  categories: Record<string, number[]>,
  visibleCats: string[]
): PriceChangePoint[] {
  return visibleCats
    .filter((cat) => categories[cat] && categories[cat].length > 0)
    .map((cat) => {
      const prices = categories[cat]
      const first = prices[0]
      const last = prices[prices.length - 1]
      const delta = last - first
      const pctChange = first !== 0 ? (delta / first) * 100 : 0
      return { category: cat, delta, pctChange }
    })
}

export function buildHoldingComparisonData(
  holdingPrice: number | null,
  holdingVehicleType: string | null,
  categories: Record<string, number[]>
): HoldingComparisonData | null {
  if (holdingPrice === null || holdingVehicleType === null) return null
  const prices = categories[holdingVehicleType]
  if (!prices || prices.length === 0) return null
  const currentBest = prices[prices.length - 1]
  return { holdingPrice, currentBest }
}
