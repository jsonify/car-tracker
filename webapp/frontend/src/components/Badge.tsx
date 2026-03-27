type BadgeVariant = 'primary' | 'secondary' | 'tertiary' | 'error' | 'muted'

interface BadgeProps {
  label: string
  variant?: BadgeVariant
}

const variants: Record<BadgeVariant, string> = {
  primary: 'bg-primary/15 text-primary',
  secondary: 'bg-secondary/15 text-secondary',
  tertiary: 'bg-tertiary/15 text-tertiary',
  error: 'bg-error/15 text-error',
  muted: 'bg-surface-container-highest text-on-surface-variant',
}

export default function Badge({ label, variant = 'muted' }: BadgeProps) {
  return (
    <span
      data-testid="badge"
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-body font-medium ${variants[variant]}`}
    >
      {label}
    </span>
  )
}
