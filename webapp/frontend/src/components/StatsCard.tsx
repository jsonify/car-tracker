import Icon from './Icon'

interface StatsCardProps {
  label: string
  value: string
  icon?: string
  trend?: { direction: 'up' | 'down' | 'neutral'; text: string }
  className?: string
}

export default function StatsCard({ label, value, icon, trend, className = '' }: StatsCardProps) {
  const trendColor = trend
    ? trend.direction === 'up'
      ? 'text-tertiary'
      : trend.direction === 'down'
        ? 'text-error'
        : 'text-on-surface-variant'
    : ''

  const trendIcon = trend
    ? trend.direction === 'up'
      ? 'trending_up'
      : trend.direction === 'down'
        ? 'trending_down'
        : 'trending_flat'
    : null

  return (
    <div className={`bg-surface-container rounded-xl p-5 hover:bg-surface-container-high transition-colors ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-body text-on-surface-variant uppercase tracking-widest">{label}</p>
          <p className="text-2xl font-headline font-black text-on-surface mt-1">{value}</p>
          {trend && (
            <div className={`flex items-center gap-1 mt-2 text-xs font-body ${trendColor}`}>
              {trendIcon && <Icon name={trendIcon} size={14} />}
              <span>{trend.text}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon name={icon} size={24} className="text-primary" />
          </div>
        )}
      </div>
    </div>
  )
}
