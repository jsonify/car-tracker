import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    expect(screen.getByTestId('app-root')).toBeInTheDocument()
  })

  it('shows loading message', () => {
    render(<App />)
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })
})
