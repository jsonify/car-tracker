export interface ChartPoint {
  date: string
  [category: string]: number | string
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
