import { Metadata } from 'next'
import Link from 'next/link'
import { Suspense } from 'react'
import { SITE_URL } from '@/lib/constants'
import { sanitizeJSON } from '@/lib/sanitize'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight } from 'lucide-react'
import { SearchInput } from '@/components/resort/SearchInput'
import { ResortFilters } from '@/components/resort/ResortFilters'
import { ResortGrid } from '@/components/resort/ResortGrid'
import {
  type ResortListItem,
  type FilterParams,
  applyAllFilters,
  sortResorts,
  parseSortOption,
  parseAgeRanges,
  getAgeDisplayText,
} from '@/lib/resort-filters'

export const metadata: Metadata = {
  title: 'Browse Family Ski Resorts',
  description:
    'Find the perfect family ski resort worldwide. Browse by country, family score, and more. Complete trip guides with honest parent reviews.',
  alternates: {
    canonical: `${SITE_URL}/resorts`,
  },
  openGraph: {
    url: `${SITE_URL}/resorts`,
  },
}

async function getResorts(): Promise<ResortListItem[]> {
  const { data, error } = await supabase
    .from('resorts')
    .select(`
      id,
      slug,
      name,
      country,
      region,
      family_metrics:resort_family_metrics(
        family_overall_score,
        best_age_min,
        best_age_max
      ),
      content:resort_content(
        tagline
      ),
      images:resort_images(
        image_url,
        image_type
      ),
      costs:resort_costs(
        estimated_family_daily,
        currency
      )
    `)
    .eq('status', 'published')
    .order('family_overall_score', {
      ascending: false,
      nullsFirst: false,
      foreignTable: 'resort_family_metrics',
    })

  if (error) {
    console.error('Error fetching resorts:', error)
    return []
  }

  return data as ResortListItem[]
}

export const revalidate = 3600

export default async function ResortsPage({
  searchParams,
}: {
  searchParams: FilterParams
}) {
  const allResorts = await getResorts()

  // Apply filters
  const filteredResorts = applyAllFilters(allResorts, searchParams)
  const sort = parseSortOption(searchParams.sort)
  const sortedResorts = sortResorts(filteredResorts, sort)

  // For display text
  const selectedAges = parseAgeRanges(searchParams.ages)
  const ageDisplayText = getAgeDisplayText(selectedAges)

  // Compute country counts from unfiltered set
  const countryCounts = allResorts.reduce(
    (acc, r) => {
      acc[r.country] = (acc[r.country] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )
  const countries = Object.entries(countryCounts)
    .sort(([, a], [, b]) => b - a)
    .map(([name, count]) => ({ name, count }))

  // Build ItemList JSON-LD from filtered results
  const itemListJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Family Ski Resorts',
    description:
      'Family-friendly ski resorts worldwide with trip guides and family scores.',
    numberOfItems: sortedResorts.length,
    itemListElement: sortedResorts.map((resort, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: resort.name,
      url: `${SITE_URL}/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`,
      ...(resort.content?.tagline
        ? { description: resort.content.tagline }
        : {}),
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: sanitizeJSON(itemListJsonLd) }}
      />
      <Navbar />
      <main id="main-content" className="min-h-screen bg-white">
        {/* Breadcrumb */}
        <nav className="bg-dark-50 py-4 border-b border-dark-100">
          <div className="container-page">
            <ol className="breadcrumb">
              <li>
                <Link
                  href="/"
                  className="hover:text-gold-600 transition-colors"
                >
                  Home
                </Link>
              </li>
              <li className="breadcrumb-separator">
                <ChevronRight className="w-4 h-4" />
              </li>
              <li className="text-dark-900 font-medium">Resorts</li>
            </ol>
          </div>
        </nav>

        {/* Hero Header */}
        <header className="relative py-20 sm:py-28 overflow-hidden">
          <div className="absolute inset-0 hero-gradient" />
          <div className="container-page relative z-10">
            <div className="animate-in animate-in-1 max-w-3xl">
              <span className="font-accent text-2xl text-teal-600 block mb-4">
                Find your perfect family resort
              </span>
              <h1 className="title-giant text-dark-800">
                Browse Family Ski Resorts
              </h1>
              <p className="mt-8 text-xl text-dark-600 leading-relaxed max-w-2xl">
                {sortedResorts.length > 0 ? (
                  selectedAges.length > 0 ? (
                    <>
                      <strong className="text-coral-500">
                        {sortedResorts.length}
                      </strong>{' '}
                      resorts perfect for {ageDisplayText} with complete trip
                      guides, cost breakdowns, and detailed family information.
                    </>
                  ) : (
                    <>
                      <strong className="text-coral-500">
                        {sortedResorts.length}
                      </strong>{' '}
                      family-friendly resorts worldwide with complete trip
                      guides, cost breakdowns, and detailed family information.
                    </>
                  )
                ) : (
                  'Explore our growing collection of family-friendly ski resorts from around the world.'
                )}
              </p>
            </div>

            {/* Search + Quiz CTA */}
            <div className="mt-10 flex flex-col sm:flex-row gap-4 max-w-xl animate-in animate-in-2">
              <Suspense>
                <SearchInput />
              </Suspense>
              <Button size="lg" asChild>
                <Link href="/quiz">Find Your Match</Link>
              </Button>
            </div>
          </div>
        </header>

        {/* Filter Bar */}
        <ResortFilters
          basePath="/resorts"
          searchParams={searchParams}
          countries={countries}
          totalResorts={allResorts.length}
          filteredCount={sortedResorts.length}
        />

        {/* Resort Listings */}
        <div className="container-page py-16 lg:py-20">
          <ResortGrid
            resorts={sortedResorts}
            sort={sort}
            basePath="/resorts"
          />
        </div>

        {/* Newsletter CTA */}
        <section className="bg-gradient-to-br from-mint-50/50 via-white to-coral-50/30 border-t border-dark-100 py-20">
          <div className="container-page">
            <div
              className="relative overflow-hidden p-10 sm:p-12 max-w-2xl mx-auto text-center"
              style={{
                borderRadius: '40px',
                background:
                  'linear-gradient(145deg, rgba(149, 225, 211, 0.15) 0%, rgba(255, 107, 107, 0.08) 100%)',
                border: '2px solid rgba(149, 225, 211, 0.3)',
              }}
            >
              <div className="absolute top-4 right-4 w-16 h-16 bg-coral-100 rounded-full opacity-50 blur-2xl" />
              <div className="absolute bottom-4 left-4 w-12 h-12 bg-teal-100 rounded-full opacity-50 blur-2xl" />

              <div className="relative z-10">
                <span className="font-accent text-2xl text-teal-600">
                  Don&apos;t see your favorite resort?
                </span>
                <h2 className="mt-3 font-display text-2xl sm:text-3xl font-bold text-dark-800">
                  We&apos;re adding new resorts every week
                </h2>
                <p className="mt-4 text-lg text-dark-600">
                  Sign up to get notified when we add resorts you care about.
                </p>
                <Button size="lg" className="mt-8" asChild>
                  <Link href="/#newsletter">Join the Newsletter</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  )
}
