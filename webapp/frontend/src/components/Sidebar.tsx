import { NavLink } from 'react-router-dom'
import Icon from './Icon'

const navItems = [
  { to: '/', label: 'Dashboard', icon: 'dashboard' },
  { to: '/bookings', label: 'Bookings', icon: 'event_note' },
  { to: '/price-history', label: 'Price History', icon: 'trending_up' },
  { to: '/vehicles', label: 'Vehicles', icon: 'directions_car' },
  { to: '/runs', label: 'Runs Log', icon: 'history' },
  { to: '/settings', label: 'Settings', icon: 'settings' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 shrink-0 bg-surface-container flex flex-col h-screen sticky top-0">
      <div className="px-5 py-5">
        <h1 className="text-sm font-headline font-black text-primary tracking-widest uppercase">
          Car Tracker
        </h1>
        <p className="text-xs text-on-surface-variant mt-0.5 font-body">Costco Travel</p>
      </div>

      <nav className="flex-1 py-2 px-3 space-y-1">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-body transition-colors ${
                isActive
                  ? 'bg-surface-container-high text-primary border-r-4 border-primary'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
              }`
            }
          >
            <Icon name={icon} size={20} filled={false} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 mt-auto">
        <button className="w-full gradient-primary text-surface font-headline font-bold text-sm py-2.5 rounded-lg flex items-center justify-center gap-2 hover:brightness-110 transition-all">
          <Icon name="add" size={18} />
          New Search
        </button>
      </div>
    </aside>
  )
}
