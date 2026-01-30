import { Metadata } from 'next'
import Link from 'next/link'
import { Suspense } from 'react'
import { notFound } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { SITE_URL } from '@/lib/constants'
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
  slugToCountryName,
  countryToSlug,
  applyAllFilters,
  sortResorts,
  parseSortOption,
  parseAgeRanges,
  getAgeDisplayText,
} from '@/lib/resort-filters'

interface PageProps {
  params: { country: string }
  searchParams: FilterParams
}

async function getResortsByCountry(
  countryName: string
): Promise<ResortListItem[]> {
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
    .eq('country', countryName)
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

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const countryName = slugToCountryName(params.country)
  const resorts = await getResortsByCountry(countryName)

  if (resorts.length === 0) {
    return { title: 'Country Not Found' }
  }

  const canonicalUrl = `${SITE_URL}/resorts/${countryToSlug(countryName)}`

  return {
    title: `Family Ski Resorts in ${countryName}`,
    description: `${resorts.length} kid-friendly ski resorts in ${countryName}. Family scores, best ages, and honest parent reviews for every resort.`,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      type: 'website',
      title: `Family Ski Resorts in ${countryName} | Snowthere`,
      description: `${resorts.length} kid-friendly ski resorts in ${countryName}. Family scores, best ages, and honest parent reviews for every resort.`,
      url: canonicalUrl,
      siteName: 'Snowthere',
      locale: 'en_US',
    },
  }
}

export const revalidate = 3600

export default async function CountryResortsPage({
  params,
  searchParams,
}: PageProps) {
  const countryName = slugToCountryName(params.country)
  const slug = countryToSlug(countryName)
  const allResorts = await getResortsByCountry(countryName)

  if (allResorts.length === 0) {
    notFound()
  }

  // Country is locked by route — don't apply country filter from params
  const filterParams: FilterParams = {
    ages: searchParams.ages,
    budget: searchParams.budget,
    sort: searchParams.sort,
    q: searchParams.q,
  }
  const filteredResorts = applyAllFilters(allResorts, filterParams)
  const sort = parseSortOption(searchParams.sort)
  const sortedResorts = sortResorts(filteredResorts, sort)

  const selectedAges = parseAgeRanges(searchParams.ages)
  const ageDisplayText = getAgeDisplayText(selectedAges)

  return (
    <>
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
              <li>
                <Link
                  href="/resorts"
                  className="hover:text-gold-600 transition-colors"
                >
                  Resorts
                </Link>
              </li>
              <li className="breadcrumb-separator">
                <ChevronRight className="w-4 h-4" />
              </li>
              <li className="text-dark-900 font-medium">{countryName}</li>
            </ol>
          </div>
        </nav>

        {/* Hero Header */}
        <header className="relative py-20 sm:py-28 overflow-hidden">
          <div className="absolute inset-0 hero-gradient" />
          <div className="container-page relative z-10">
            <div className="animate-in animate-in-1 max-w-3xl">
              <span className="font-accent text-2xl text-teal-600 block mb-4">
                Family skiing in {countryName}
              </span>
              <h1 className="title-giant text-dark-800">
                {countryName} Family Ski Resorts
              </h1>
              <p className="mt-8 text-xl text-dark-600 leading-relaxed max-w-2xl">
                {sortedResorts.length > 0 ? (
                  selectedAges.length > 0 ? (
                    <>
                      <strong className="text-coral-500">
                        {sortedResorts.length}
                      </strong>{' '}
                      resorts in {countryName} perfect for {ageDisplayText} with
                      complete trip guides, cost breakdowns, and detailed family
                      information.
                    </>
                  ) : (
                    <>
                      <strong className="text-coral-500">
                        {sortedResorts.length}
                      </strong>{' '}
                      family-friendly resorts in {countryName} with complete trip
                      guides, cost breakdowns, and detailed family information.
                    </>
                  )
                ) : (
                  `No resorts found matching your filters in ${countryName}.`
                )}
              </p>
            </div>

            {/* Search + Quiz CTA */}
            <div className="mt-10 flex flex-col sm:flex-row gap-4 max-w-xl animate-in animate-in-2">
              <Suspense>
                <SearchInput
                  placeholder={`Search ${countryName} resorts...`}
                />
              </Suspense>
              <Button size="lg" asChild>
                <Link href="/quiz">Find Your Match</Link>
              </Button>
            </div>
          </div>
        </header>

        {/* Filter Bar (no country pills — country is locked by route) */}
        <ResortFilters
          basePath={`/resorts/${slug}`}
          searchParams={filterParams}
          totalResorts={allResorts.length}
          filteredCount={sortedResorts.length}
        />

        {/* Resort Listings */}
        <div className="container-page py-16 lg:py-20">
          <ResortGrid
            resorts={sortedResorts}
            sort={sort}
            basePath={`/resorts/${slug}`}
            countrySlug={slug}
            emptySubtitle={`Try adjusting your filters or browse all ${countryName} resorts.`}
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
                  Looking for more {countryName} resorts?
                </span>
                <h2 className="mt-3 font-display text-2xl sm:text-3xl font-bold text-dark-800">
                  We&apos;re adding new resorts every week
                </h2>
                <p className="mt-4 text-lg text-dark-600">
                  Sign up to get notified when we add more {countryName}{' '}
                  resorts.
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
