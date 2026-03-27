import Icon from './Icon'

interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
}

export default function EmptyState({ icon = 'inbox', title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <Icon name={icon} size={48} className="text-surface-container-highest mb-4" />
      <p className="text-on-surface-variant font-headline font-bold">{title}</p>
      {description && <p className="text-on-surface-variant/60 text-sm font-body mt-1">{description}</p>}
    </div>
  )
}
