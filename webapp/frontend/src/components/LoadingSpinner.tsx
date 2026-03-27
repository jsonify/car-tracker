import Icon from './Icon'

export default function LoadingSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-on-surface-variant">
      <Icon name="progress_activity" size={24} className="animate-spin" />
      <span className="text-sm font-body">{label}</span>
    </div>
  )
}
