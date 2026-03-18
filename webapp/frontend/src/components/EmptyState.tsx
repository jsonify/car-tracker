interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
}

export default function EmptyState({ icon = '◌', title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <span className="text-4xl text-gray-700 mb-4">{icon}</span>
      <p className="text-gray-400 font-medium">{title}</p>
      {description && <p className="text-gray-600 text-sm mt-1">{description}</p>}
    </div>
  )
}
