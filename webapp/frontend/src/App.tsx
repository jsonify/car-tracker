import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Bookings from './pages/Bookings'
import PriceHistory from './pages/PriceHistory'
import Vehicles from './pages/Vehicles'
import Runs from './pages/Runs'

export default function App() {
  return (
    <BrowserRouter>
      <div data-testid="app-root" className="flex min-h-screen bg-gray-950">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/bookings" element={<Bookings />} />
            <Route path="/price-history" element={<PriceHistory />} />
            <Route path="/vehicles" element={<Vehicles />} />
            <Route path="/runs" element={<Runs />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
