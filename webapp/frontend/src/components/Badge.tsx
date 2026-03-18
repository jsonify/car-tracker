type BadgeVariant = 'green' | 'red' | 'yellow' | 'blue' | 'gray'

interface BadgeProps {
  label: string
  variant?: BadgeVariant
}

const variants: Record<BadgeVariant, string> = {
  green: 'bg-green-900/60 text-green-300 border-green-700/50',
  red: 'bg-red-900/60 text-red-300 border-red-700/50',
  yellow: 'bg-yellow-900/60 text-yellow-300 border-yellow-700/50',
  blue: 'bg-blue-900/60 text-blue-300 border-blue-700/50',
  gray: 'bg-gray-800 text-gray-400 border-gray-700',
}

export default function Badge({ label, variant = 'gray' }: BadgeProps) {
  return (
    <span
      data-testid="badge"
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${variants[variant]}`}
    >
      {label}
    </span>
  )
}
