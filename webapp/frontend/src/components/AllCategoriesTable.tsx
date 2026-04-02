import { useState } from 'react'
import { formatRunDate } from '../utils/dateUtils'

interface AllCategoriesTableProps {
  categories: Record<string, number[]>
  runDates: string[]
}

export default function AllCategoriesTable({ categories, runDates }: AllCategoriesTableProps) {
  const [sortAsc, setSortAsc] = useState(true)

  const catNames = Object.keys(categories)

  if (catNames.length === 0 || runDates.length === 0) {
    return (
      <p data-testid="empty-message" className="text-sm font-body text-on-surface-variant">
        No data available.
      </p>
    )
  }

  const sorted = [...catNames].sort((a, b) => {
    const aLast = categories[a][categories[a].length - 1] ?? 0
    const bLast = categories[b][categories[b].length - 1] ?? 0
    return sortAsc ? aLast - bLast : bLast - aLast
  })

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm font-body border-collapse">
        <thead>
          <tr className="border-b border-outline-variant">
            <th className="text-left py-2 pr-4 text-on-surface-variant font-medium text-xs whitespace-nowrap">
              Category
            </th>
            {runDates.map((d) => (
              <th
                key={d}
                className="text-right py-2 px-3 text-on-surface-variant font-medium text-xs whitespace-nowrap"
              >
                {formatRunDate(d)}
              </th>
            ))}
            <th
              data-testid="sort-latest"
              onClick={() => setSortAsc((v) => !v)}
              className="text-right py-2 pl-3 text-primary font-medium text-xs whitespace-nowrap cursor-pointer select-none hover:text-primary/80"
            >
              Latest {sortAsc ? '↑' : '↓'}
            </th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((cat) => {
            const prices = categories[cat]
            const latest = prices[prices.length - 1]
            return (
              <tr
                key={cat}
                className="border-b border-outline-variant/30 hover:bg-surface-container-high/50 transition-colors"
              >
                <td className="py-2 pr-4 text-on-surface whitespace-nowrap">{cat}</td>
                {runDates.map((d, i) => (
                  <td key={d} className="py-2 px-3 text-right text-on-surface-variant tabular-nums">
                    {prices[i] !== undefined ? `$${prices[i].toFixed(2)}` : '—'}
                  </td>
                ))}
                <td className="py-2 pl-3 text-right text-on-surface font-medium tabular-nums">
                  {latest !== undefined ? `$${latest.toFixed(2)}` : '—'}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
