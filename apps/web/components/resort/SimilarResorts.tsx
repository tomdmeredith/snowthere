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
    <section id="similar-resorts" className="space-y-8">
      {/* Section Header - Design-5 */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-coral-50 border border-coral-200 shadow-coral">
          <Mountain className="w-6 h-6 text-coral-600" />
        </div>
        <div>
          <div className="flex items-center gap-3">
            <span className="h-1 w-6 bg-gradient-to-r from-coral-400 to-coral-500 rounded-full" />
            <h2 className="font-display text-3xl font-bold text-dark-800">
              Similar Resorts
            </h2>
          </div>
          <p className="text-dark-500 mt-1 font-medium">
            Families who loved {currentResortName} also enjoyed these
          </p>
        </div>
      </div>

      {/* Resort Cards Grid - Design-5 */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {resorts.map((resort, index) => (
          <Link
            key={resort.resort_id}
            href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
            className="group"
          >
            <div className="relative overflow-hidden rounded-3xl border border-dark-100 bg-white shadow-card transition-all duration-300 hover:border-coral-200 hover:shadow-card-hover hover:scale-[1.02]">
              {/* Top decorative gradient - Design-5 playful colors */}
              <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-coral-400 via-gold-300 to-teal-400" />

              {/* Card Content */}
              <div className="p-6">
                {/* Resort Name and Country */}
                <div className="mb-4">
                  <h3 className="font-display text-xl font-bold text-dark-800 group-hover:text-coral-600 transition-colors">
                    {resort.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-2">
                    <MapPin className="w-4 h-4 text-coral-400" />
                    <span className="text-sm text-dark-500 font-medium">{resort.country}</span>
                  </div>
                </div>

                {/* Scores Row - Design-5 badges */}
                <div className="flex flex-wrap items-center gap-2 mb-4">
                  {/* Family Score - coral gradient */}
                  {resort.family_overall_score && (
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-coral-500 to-coral-600 shadow-coral">
                      <Star className="w-4 h-4 text-white fill-white/50" />
                      <span className="text-sm font-bold text-white">
                        {resort.family_overall_score}/10
                      </span>
                    </div>
                  )}

                  {/* Similarity Badge - playful styling */}
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-dark-100 to-dark-50 border border-dark-200">
                    <Sparkles className="w-4 h-4 text-gold-500" />
                    <span className="text-sm font-semibold text-dark-700">
                      {Math.round(resort.similarity_score * 100)}% match
                    </span>
                  </div>
                </div>

                {/* Shared Features - Design-5 */}
                {resort.shared_features && resort.shared_features.length > 0 && (
                  <div className="space-y-2 mb-4">
                    {resort.shared_features.slice(0, 2).map((feature, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-2 text-sm text-dark-600"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-coral-400 to-gold-400" />
                        {feature}
                      </div>
                    ))}
                  </div>
                )}

                {/* View Link - Design-5 */}
                <div className="flex items-center gap-2 text-sm font-semibold text-dark-500 group-hover:text-coral-600 transition-colors pt-2 border-t border-dark-100">
                  <span>View resort</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1.5 transition-transform" />
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* See More Link - Design-5 pill button */}
      {resorts.length >= 3 && (
        <div className="text-center pt-2">
          <Link
            href={`/resorts?similar=${currentResortName.toLowerCase().replace(/\s+/g, '-')}`}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-semibold text-dark-700 bg-gradient-to-r from-gold-100 to-gold-50 hover:from-gold-200 hover:to-gold-100 border border-gold-200 shadow-card hover:shadow-gold hover:scale-105 transition-all duration-300"
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
 * Skeleton loader for SimilarResorts component - Design-5
 */
export function SimilarResortsSkeleton() {
  return (
    <section className="space-y-8">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-coral-100 animate-pulse" />
        <div className="space-y-2">
          <div className="h-7 w-44 bg-dark-100 rounded-lg animate-pulse" />
          <div className="h-4 w-60 bg-dark-50 rounded animate-pulse" />
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-3xl border border-dark-100 bg-white shadow-card p-6"
          >
            <div className="h-1.5 w-full bg-gradient-to-r from-coral-100 via-gold-100 to-teal-100 rounded-full mb-4 animate-pulse" />
            <div className="space-y-3">
              <div className="h-6 w-3/4 bg-dark-100 rounded-lg animate-pulse" />
              <div className="h-4 w-1/2 bg-dark-50 rounded animate-pulse" />
              <div className="flex gap-2 mt-4">
                <div className="h-8 w-20 bg-coral-100 rounded-full animate-pulse" />
                <div className="h-8 w-24 bg-dark-100 rounded-full animate-pulse" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
