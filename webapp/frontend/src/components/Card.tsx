type CardVariant = 'standard' | 'glass' | 'gradient'

interface CardProps {
  title?: string
  variant?: CardVariant
  children: React.ReactNode
  className?: string
}

const variantClasses: Record<CardVariant, string> = {
  standard: 'bg-surface-container hover:bg-surface-container-high',
  glass: 'glass',
  gradient: 'bg-surface-container hover:bg-surface-container-high bg-gradient-to-br from-primary/5 to-secondary/5',
}

export default function Card({ title, variant = 'standard', children, className = '' }: CardProps) {
  return (
    <div className={`rounded-xl p-5 transition-colors ${variantClasses[variant]} ${className}`}>
      {title && (
        <h2 className="text-xs font-headline font-bold text-on-surface-variant uppercase tracking-widest mb-3">
          {title}
        </h2>
      )}
      {children}
    </div>
  )
}
