import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import AllCategoriesTable from './AllCategoriesTable'

const runDates = [
  '2026-03-27T02:18:08+00:00',
  '2026-03-31T11:09:38+00:00',
  '2026-04-01T11:11:33+00:00',
]

const categories: Record<string, number[]> = {
  'Economy Car': [200, 210, 180],
  'Standard Car': [250, 260, 240],
  'Compact SUV': [300, 310, 290],
}

describe('AllCategoriesTable', () => {
  it('renders a row for each category', () => {
    render(<AllCategoriesTable categories={categories} runDates={runDates} />)
    expect(screen.getByText('Economy Car')).toBeInTheDocument()
    expect(screen.getByText('Standard Car')).toBeInTheDocument()
    expect(screen.getByText('Compact SUV')).toBeInTheDocument()
  })

  it('renders formatted dates as column headers', () => {
    render(<AllCategoriesTable categories={categories} runDates={runDates} />)
    expect(screen.getByText('Mar 27')).toBeInTheDocument()
    expect(screen.getByText('Mar 31')).toBeInTheDocument()
    expect(screen.getByText('Apr 1')).toBeInTheDocument()
  })

  it('renders prices formatted as currency', () => {
    render(<AllCategoriesTable categories={categories} runDates={runDates} />)
    expect(screen.getByText('$200.00')).toBeInTheDocument()
    // $180.00 appears in both the run date column and Latest column
    expect(screen.getAllByText('$180.00').length).toBeGreaterThanOrEqual(1)
  })

  it('sorts by latest price ascending by default', () => {
    render(<AllCategoriesTable categories={categories} runDates={runDates} />)
    const rows = screen.getAllByRole('row').slice(1) // skip header
    const firstCell = rows[0].querySelector('td')
    expect(firstCell?.textContent).toBe('Economy Car')
  })

  it('toggles sort direction when latest column header is clicked', () => {
    render(<AllCategoriesTable categories={categories} runDates={runDates} />)
    const latestHeader = screen.getByTestId('sort-latest')
    fireEvent.click(latestHeader)
    const rows = screen.getAllByRole('row').slice(1)
    const firstCell = rows[0].querySelector('td')
    expect(firstCell?.textContent).toBe('Compact SUV')
  })

  it('renders empty state when no categories', () => {
    render(<AllCategoriesTable categories={{}} runDates={[]} />)
    expect(screen.getByTestId('empty-message')).toBeInTheDocument()
  })
})
