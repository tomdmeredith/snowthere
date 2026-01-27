import Link from 'next/link'
import { MapPin, Star, ChevronRight } from 'lucide-react'
import type { GuideResort } from '@/lib/guides'

interface GuideFeaturedResortsProps {
  resorts: GuideResort[]
  title?: string
}

export function GuideFeaturedResorts({
  resorts,
  title = 'Featured Resorts',
}: GuideFeaturedResortsProps) {
  if (!resorts || resorts.length === 0) return null

  // Sort by display_order
  const sortedResorts = [...resorts].sort((a, b) => a.display_order - b.display_order)

  return (
    <section className="py-8">
      <h2 className="font-display text-2xl font-bold text-gray-900 mb-6">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedResorts.map((gr) => {
          const resort = gr.resort
          if (!resort) return null

          const score = resort.family_metrics?.family_overall_score

          return (
            <Link
              key={gr.resort_id}
              href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
              className="group bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md hover:border-coral-200 transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 group-hover:text-coral-500 transition-colors truncate">
                    {resort.name}
                  </h3>
                  <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                    <MapPin className="w-3.5 h-3.5" />
                    {resort.country}
                  </p>
                </div>

                {score && (
                  <div className="flex items-center gap-1 bg-coral-50 text-coral-600 px-2 py-1 rounded-lg text-sm font-semibold">
                    <Star className="w-3.5 h-3.5 fill-current" />
                    {score.toFixed(1)}
                  </div>
                )}
              </div>

              {gr.highlight_reason && (
                <p className="text-sm text-gray-600 mt-3 line-clamp-2">
                  {gr.highlight_reason}
                </p>
              )}

              <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                <span className="text-sm text-coral-500 font-medium group-hover:text-coral-600">
                  View Resort
                </span>
                <ChevronRight className="w-4 h-4 text-coral-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
