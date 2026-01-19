'use client'

import Link from 'next/link'
import { ArrowRight, MapPin, Star, Sparkles, Mountain } from 'lucide-react'

interface SimilarResort {
  resort_id: string
  name: string
  country: string
  slug: string
  similarity_score: number
  family_overall_score?: number | null
  shared_features?: string[]
}

interface SimilarResortsProps {
  resorts: SimilarResort[]
  currentResortName: string
  currentCountry: string
}

export function SimilarResorts({
  resorts,
  currentResortName,
  currentCountry
}: SimilarResortsProps) {
  if (!resorts || resorts.length === 0) {
    return null
  }

  return (
    <section id="similar-resorts" className="space-y-6">
      {/* Section Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-br from-slate-100 to-slate-50 border border-slate-200/60">
          <Mountain className="w-5 h-5 text-slate-600" />
        </div>
        <div>
          <h2 className="font-display text-2xl font-semibold text-espresso-800">
            Similar Resorts
          </h2>
          <p className="text-sm text-espresso-500 mt-0.5">
            Families who loved {currentResortName} also enjoyed these
          </p>
        </div>
      </div>

      {/* Resort Cards Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {resorts.map((resort, index) => (
          <Link
            key={resort.resort_id}
            href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
            className="group"
          >
            <div className="relative overflow-hidden rounded-2xl border border-camel-100/80 bg-gradient-to-br from-ivory-50 to-white transition-all duration-300 hover:border-camel-200 hover:shadow-lg hover:shadow-camel-100/50 hover:-translate-y-0.5">
              {/* Top decorative gradient */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-slate-300 via-camel-200 to-pine-200" />

              {/* Card Content */}
              <div className="p-5">
                {/* Resort Name and Country */}
                <div className="mb-4">
                  <h3 className="font-display text-lg font-semibold text-espresso-800 group-hover:text-espresso-600 transition-colors">
                    {resort.name}
                  </h3>
                  <div className="flex items-center gap-1.5 mt-1">
                    <MapPin className="w-3.5 h-3.5 text-camel-400" />
                    <span className="text-sm text-espresso-500">{resort.country}</span>
                  </div>
                </div>

                {/* Scores Row */}
                <div className="flex items-center gap-3 mb-4">
                  {/* Family Score */}
                  {resort.family_overall_score && (
                    <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-pine-50 border border-pine-100">
                      <Star className="w-3.5 h-3.5 text-pine-500 fill-pine-300" />
                      <span className="text-sm font-medium text-pine-700">
                        {resort.family_overall_score}/10
                      </span>
                    </div>
                  )}

                  {/* Similarity Badge */}
                  <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-slate-50 border border-slate-100">
                    <Sparkles className="w-3.5 h-3.5 text-slate-500" />
                    <span className="text-sm font-medium text-slate-700">
                      {Math.round(resort.similarity_score * 100)}% match
                    </span>
                  </div>
                </div>

                {/* Shared Features */}
                {resort.shared_features && resort.shared_features.length > 0 && (
                  <div className="space-y-1.5 mb-4">
                    {resort.shared_features.slice(0, 2).map((feature, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-2 text-xs text-espresso-500"
                      >
                        <span className="w-1 h-1 rounded-full bg-camel-300" />
                        {feature}
                      </div>
                    ))}
                  </div>
                )}

                {/* View Link */}
                <div className="flex items-center gap-1.5 text-sm font-medium text-espresso-500 group-hover:text-espresso-600 transition-colors">
                  <span>View resort</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* See More Link (if many resorts available) */}
      {resorts.length >= 3 && (
        <div className="text-center">
          <Link
            href={`/resorts?similar=${currentResortName.toLowerCase().replace(/\s+/g, '-')}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium text-espresso-600 bg-camel-50 hover:bg-camel-100 border border-camel-100 transition-colors"
          >
            See all similar resorts
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      )}
    </section>
  )
}

/**
 * Skeleton loader for SimilarResorts component
 */
export function SimilarResortsSkeleton() {
  return (
    <section className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-11 h-11 rounded-xl bg-slate-100 animate-pulse" />
        <div className="space-y-2">
          <div className="h-6 w-40 bg-espresso-100 rounded animate-pulse" />
          <div className="h-4 w-56 bg-espresso-50 rounded animate-pulse" />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-2xl border border-camel-100 bg-ivory-50 p-5"
          >
            <div className="space-y-3">
              <div className="h-5 w-3/4 bg-espresso-100 rounded animate-pulse" />
              <div className="h-4 w-1/2 bg-espresso-50 rounded animate-pulse" />
              <div className="flex gap-2 mt-4">
                <div className="h-7 w-16 bg-pine-50 rounded-full animate-pulse" />
                <div className="h-7 w-20 bg-slate-50 rounded-full animate-pulse" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
