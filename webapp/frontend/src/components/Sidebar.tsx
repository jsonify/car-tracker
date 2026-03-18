import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/', label: 'Dashboard', icon: '◆' },
  { to: '/bookings', label: 'Bookings', icon: '✦' },
  { to: '/price-history', label: 'Price History', icon: '↗' },
  { to: '/vehicles', label: 'Vehicles', icon: '⊞' },
  { to: '/runs', label: 'Runs Log', icon: '≡' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="px-5 py-5 border-b border-gray-800">
        <h1 className="text-sm font-semibold text-indigo-400 tracking-widest uppercase">
          Car Tracker
        </h1>
        <p className="text-xs text-gray-500 mt-0.5">Costco Travel</p>
      </div>

      <nav className="flex-1 py-4 px-2 space-y-0.5">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
              }`
            }
          >
            <span className="text-base leading-none">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
