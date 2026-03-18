export default function LoadingSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-gray-500">
      <span className="animate-spin text-xl">⊙</span>
      <span className="text-sm">{label}</span>
    </div>
  )
}
