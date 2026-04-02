import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import PriceHistoryPage from './PriceHistory'

const mockBookings = [
  {
    name: 'SFO Trip',
    pickup_location: 'SFO',
    pickup_date: '2027-01-15',
    pickup_time: '10:00',
    dropoff_date: '2027-01-22',
    dropoff_time: '10:00',
    holding_price: 300,
    holding_vehicle_type: 'Economy Car',
    city: null,
    alert_enabled: false,
    target_price: null,
    email_notifications: false,
  },
]

const mockHistory = {
  booking_name: 'SFO Trip',
  run_dates: [
    '2026-03-27T02:18:08+00:00',
    '2026-03-31T11:09:38+00:00',
    '2026-04-01T11:11:33+00:00',
  ],
  categories: {
    'Economy Car': [200, 210, 180],
    'Standard Car': [250, 260, 240],
    'Compact SUV': [300, 310, 290],
  },
  holding_price: 300,
  holding_vehicle_type: 'Economy Car',
}

vi.mock('../api/client', () => ({
  getBookings: vi.fn(() => Promise.resolve(mockBookings)),
  getPriceHistory: vi.fn(() => Promise.resolve(mockHistory)),
}))

vi.mock('../components/PriceChart', () => ({
  default: () => <div data-testid="price-chart" />,
}))

vi.mock('../components/PriceRangeChart', () => ({
  default: () => <div data-testid="price-range-chart" />,
}))

vi.mock('../components/LatestPricesChart', () => ({
  default: () => <div data-testid="latest-prices-chart" />,
}))

vi.mock('../components/PriceChangeChart', () => ({
  default: () => <div data-testid="price-change-chart" />,
}))

vi.mock('../components/HoldingComparisonChart', () => ({
  default: () => <div data-testid="holding-comparison-chart" />,
}))

vi.mock('../components/AllCategoriesTable', () => ({
  default: () => <div data-testid="all-categories-table" />,
}))

describe('PriceHistoryPage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('renders page test id', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByTestId('page-price-history')).toBeInTheDocument()
    })
  })

  it('renders the booking selector after loading', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('SFO Trip')).toBeInTheDocument()
    })
  })

  it('renders the Price Trends card', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('Price Trends')).toBeInTheDocument()
      expect(screen.getByTestId('price-chart')).toBeInTheDocument()
    })
  })

  it('renders the Best Time to Book card', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('Best Time to Book')).toBeInTheDocument()
    })
  })

  it('renders the Savings Summary card', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('Savings Summary')).toBeInTheDocument()
    })
  })

  it('renders the charts grid with all 4 new chart cards', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByTestId('charts-grid')).toBeInTheDocument()
      expect(screen.getByTestId('price-range-chart')).toBeInTheDocument()
      expect(screen.getByTestId('latest-prices-chart')).toBeInTheDocument()
      expect(screen.getByTestId('price-change-chart')).toBeInTheDocument()
      expect(screen.getByTestId('holding-comparison-chart')).toBeInTheDocument()
    })
  })

  it('renders the All Categories Overview table', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('All Categories Overview')).toBeInTheDocument()
      expect(screen.getByTestId('all-categories-table')).toBeInTheDocument()
    })
  })

  it('renders chart section titles', async () => {
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('Price Range')).toBeInTheDocument()
      expect(screen.getByText('Latest Prices')).toBeInTheDocument()
      expect(screen.getByText('Price Change')).toBeInTheDocument()
      expect(screen.getByText('Holding vs Current')).toBeInTheDocument()
    })
  })

  it('renders empty state when no bookings', async () => {
    const { getBookings } = await import('../api/client')
    vi.mocked(getBookings).mockResolvedValueOnce([])
    render(<PriceHistoryPage />)
    await waitFor(() => {
      expect(screen.getByText('No bookings')).toBeInTheDocument()
    })
  })
})
