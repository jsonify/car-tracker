import Icon from './Icon'

interface TopAppBarProps {
  title?: string
}

export default function TopAppBar({ title }: TopAppBarProps) {
  return (
    <header className="sticky top-0 z-30 glass px-6 py-3 flex items-center gap-4">
      {title && (
        <h1 className="text-lg font-headline font-black text-on-surface">{title}</h1>
      )}
      <div className="flex-1" />
      <div className="relative">
        <Icon name="search" size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
        <input
          type="text"
          placeholder="Search…"
          className="input-field pl-9 w-64"
        />
      </div>
      <button className="p-2 rounded-lg hover:bg-surface-container-high transition-colors text-on-surface-variant">
        <Icon name="filter_list" size={20} />
      </button>
    </header>
  )
}
