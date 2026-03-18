interface CardProps {
  title?: string
  children: React.ReactNode
  className?: string
}

export default function Card({ title, children, className = '' }: CardProps) {
  return (
    <div className={`bg-gray-900 border border-gray-800 rounded-xl p-5 ${className}`}>
      {title && (
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          {title}
        </h2>
      )}
      {children}
    </div>
  )
}
