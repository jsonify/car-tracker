import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Sidebar from './components/Sidebar'
import TopAppBar from './components/TopAppBar'
import Dashboard from './pages/Dashboard'
import Bookings from './pages/Bookings'
import PriceHistory from './pages/PriceHistory'
import Vehicles from './pages/Vehicles'
import Runs from './pages/Runs'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <div data-testid="app-root" className="flex min-h-screen bg-surface">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-auto">
          <TopAppBar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/bookings" element={<Bookings />} />
              <Route path="/price-history" element={<PriceHistory />} />
              <Route path="/vehicles" element={<Vehicles />} />
              <Route path="/runs" element={<Runs />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
