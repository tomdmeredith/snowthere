interface LastUpdatedProps {
  date: string
}

export function LastUpdated({ date }: LastUpdatedProps) {
  const formatted = new Date(date).toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  })

  return (
    <p className="text-sm text-stone-500">
      Last updated {formatted}
    </p>
  )
}
