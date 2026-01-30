import Link from 'next/link'
import { Mountain, Globe } from 'lucide-react'
import { Button } from '@/components/ui'
import {
  type ResortListItem,
  type SortOption,
  groupByCountry,
} from '@/lib/resort-filters'
import { ResortCard } from './ResortCard'

interface ResortGridProps {
  resorts: ResortListItem[]
  sort: SortOption
  /** Base path for the clear filters link */
  basePath: string
  /** Optional country slug override for cards */
  countrySlug?: string
  /** Optional custom empty state subtitle */
  emptySubtitle?: string
}

export function ResortGrid({
  resorts,
  sort,
  basePath,
  countrySlug,
  emptySubtitle,
}: ResortGridProps) {
  // Empty state
  if (resorts.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="mx-auto w-20 h-20 rounded-full bg-dark-100 flex items-center justify-center mb-8">
          <Mountain className="w-10 h-10 text-dark-300" />
        </div>
        <h2 className="font-display text-2xl font-bold text-dark-800 mb-3">
          No resorts match your filters
        </h2>
        <p className="text-lg text-dark-600 mb-6">
          {emptySubtitle || 'Try removing a filter or searching for something else.'}
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button asChild>
            <Link href={basePath}>Clear all filters</Link>
          </Button>
          <Button variant="ghost" asChild>
            <Link href="/#newsletter">Get notified of new resorts</Link>
          </Button>
        </div>
      </div>
    )
  }

  // Group by country when sorting by score (default), flat list otherwise
  if (sort === 'score') {
    const grouped = groupByCountry(resorts)
    const countries = Object.keys(grouped).sort()

    return (
      <div className="space-y-20">
        {countries.map((country) => (
          <section key={country} className="animate-in animate-in-3">
            <div className="flex items-center gap-5 mb-10">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 shadow-teal">
                <Globe className="w-7 h-7 text-teal-600" />
              </div>
              <div>
                <h2 className="font-display text-3xl font-bold text-dark-800">
                  {country}
                </h2>
                <p className="text-dark-500 font-medium">
                  {grouped[country].length}{' '}
                  {grouped[country].length === 1 ? 'resort' : 'resorts'}
                </p>
              </div>
            </div>

            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {grouped[country].map((resort) => (
                <ResortCard
                  key={resort.id}
                  resort={resort}
                  countrySlug={countrySlug}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    )
  }

  // Flat list for price/name sort
  return (
    <div className="animate-in animate-in-3">
      <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {resorts.map((resort) => (
          <ResortCard
            key={resort.id}
            resort={resort}
            countrySlug={countrySlug}
          />
        ))}
      </div>
    </div>
  )
}
