import { Metadata } from 'next'
import Link from 'next/link'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { Button, ScoreBadge } from '@/components/ui'
import { Navbar } from '@/components/layout/Navbar'
import {
  ChevronRight,
  Mountain,
  Globe,
  MapPin,
  Search,
  Filter,
  X,
} from 'lucide-react'

// Convert URL slug to proper country name
function slugToCountryName(slug: string): string {
  return decodeURIComponent(slug)
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

// Convert country name to URL slug
function countryToSlug(country: string): string {
  return country.toLowerCase().replace(/\s+/g, '-')
}

// Age range types matching AgeSelector
type AgeRange = '0-3' | '4-7' | '8-12' | '13+'

// Age range bounds for filtering
const AGE_BOUNDS: Record<AgeRange, { min: number; max: number }> = {
  '0-3': { min: 0, max: 3 },
  '4-7': { min: 4, max: 7 },
  '8-12': { min: 8, max: 12 },
  '13+': { min: 13, max: 99 },
}

// Age range labels for display
const AGE_LABELS: Record<AgeRange, string> = {
  '0-3': '0-3 years',
  '4-7': '4-7 years',
  '8-12': '8-12 years',
  '13+': '13+ years',
}

// Parse ages from URL query string
function parseAgeRanges(agesParam: string | undefined): AgeRange[] {
  if (!agesParam) return []

  const validRanges: AgeRange[] = ['0-3', '4-7', '8-12', '13+']
  return agesParam
    .split(',')
    .filter((age): age is AgeRange => validRanges.includes(age as AgeRange))
}

// Check if two age ranges overlap
function rangesOverlap(
  resortMin: number,
  resortMax: number,
  filterMin: number,
  filterMax: number
): boolean {
  return resortMin <= filterMax && resortMax >= filterMin
}

// Filter resorts by selected age ranges
function filterByAgeRanges(
  resorts: ResortWithMetrics[],
  selectedAges: AgeRange[]
): ResortWithMetrics[] {
  if (selectedAges.length === 0) return resorts

  return resorts.filter((resort) => {
    const metrics = resort.family_metrics

    // If resort has no age data, include it (don't exclude for missing data)
    if (!metrics?.best_age_min || !metrics?.best_age_max) {
      return true
    }

    // Check if resort age range overlaps with ANY selected age range
    return selectedAges.some((ageRange) => {
      const bounds = AGE_BOUNDS[ageRange]
      return rangesOverlap(
        metrics.best_age_min!,
        metrics.best_age_max!,
        bounds.min,
        bounds.max
      )
    })
  })
}

// Get display text for selected ages
function getAgeDisplayText(selectedAges: AgeRange[]): string {
  if (selectedAges.length === 0) return ''
  if (selectedAges.length === 4) return 'all ages'

  // Find min and max across all selected ranges
  const allMins = selectedAges.map((age) => AGE_BOUNDS[age].min)
  const allMaxes = selectedAges.map((age) => AGE_BOUNDS[age].max)
  const overallMin = Math.min(...allMins)
  const overallMax = Math.max(...allMaxes)

  if (overallMax >= 99) {
    return `ages ${overallMin}+`
  }
  return `ages ${overallMin}-${overallMax}`
}

interface ResortWithMetrics {
  id: string
  slug: string
  name: string
  country: string
  region: string
  family_metrics: {
    family_overall_score: number | null
    best_age_min: number | null
    best_age_max: number | null
  } | null
  content: {
    tagline: string | null
  } | null
  images: { image_url: string; image_type: string }[] | null
}

interface PageProps {
  params: { country: string }
  searchParams: { ages?: string }
}

async function getResortsByCountry(countryName: string): Promise<ResortWithMetrics[]> {
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
      )
    `)
    .eq('country', countryName)
    .eq('status', 'published')
    .order('family_overall_score', { ascending: false, nullsFirst: false, foreignTable: 'resort_family_metrics' })

  if (error) {
    console.error('Error fetching resorts:', error)
    return []
  }

  return data as ResortWithMetrics[]
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const countryName = slugToCountryName(params.country)
  const resorts = await getResortsByCountry(countryName)

  if (resorts.length === 0) {
    return {
      title: 'Country Not Found | Snowthere',
    }
  }

  return {
    title: `Family Ski Resorts in ${countryName} | Snowthere`,
    description: `${resorts.length} kid-friendly ski resorts in ${countryName}. Family scores, best ages, and honest parent reviews for every resort.`,
  }
}

export const revalidate = 3600 // Revalidate every hour

export default async function CountryResortsPage({ params, searchParams }: PageProps) {
  const countryName = slugToCountryName(params.country)
  const countrySlug = countryToSlug(countryName)
  const resorts = await getResortsByCountry(countryName)

  // 404 if no resorts found for this country
  if (resorts.length === 0) {
    notFound()
  }

  // Parse age filters from URL
  const selectedAges = parseAgeRanges(searchParams.ages)
  const filteredResorts = filterByAgeRanges(resorts, selectedAges)
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
                <Link href="/" className="hover:text-gold-600 transition-colors">
                  Home
                </Link>
              </li>
              <li className="breadcrumb-separator">
                <ChevronRight className="w-4 h-4" />
              </li>
              <li>
                <Link href="/resorts" className="hover:text-gold-600 transition-colors">
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

        {/* Hero Header - Design-5 Warm Gradient */}
        <header className="relative py-20 sm:py-28 overflow-hidden">
          {/* Design-5: Warm gradient background */}
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
                {filteredResorts.length > 0 ? (
                  selectedAges.length > 0 ? (
                    <>
                      <strong className="text-coral-500">{filteredResorts.length}</strong> resorts in {countryName} perfect for {ageDisplayText} with complete trip guides, cost breakdowns, and detailed family information.
                    </>
                  ) : (
                    <>
                      <strong className="text-coral-500">{filteredResorts.length}</strong> family-friendly resorts in {countryName} with complete trip guides, cost breakdowns, and detailed family information.
                    </>
                  )
                ) : (
                  `No resorts found matching your filters in ${countryName}.`
                )}
              </p>
            </div>

            {/* Design-5: Pill-shaped Search/Filter */}
            <div className="mt-10 flex flex-col sm:flex-row gap-4 max-w-xl animate-in animate-in-2">
              <div className="flex-1 relative">
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
                <input
                  type="text"
                  placeholder={`Search ${countryName} resorts...`}
                  className="w-full pl-14 pr-6 py-4 rounded-full bg-white border-2 border-dark-200 text-dark-800 placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-coral-400 focus:border-transparent shadow-card transition-all"
                />
              </div>
              <Button variant="ghost" size="lg" className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filters
              </Button>
            </div>
          </div>
        </header>

        {/* Active Filter Chips - Design-5 Pill Style */}
        {selectedAges.length > 0 && (
          <div className="bg-white border-b border-dark-100">
            <div className="container-page py-5">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-sm text-dark-500 font-semibold">Filtering by:</span>
                {selectedAges.map((age) => {
                  // Create URL with this age removed
                  const remainingAges = selectedAges.filter((a) => a !== age)
                  const href = remainingAges.length > 0
                    ? `/resorts/${countrySlug}?ages=${remainingAges.join(',')}`
                    : `/resorts/${countrySlug}`

                  return (
                    <Link
                      key={age}
                      href={href}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-coral-100 text-coral-700 rounded-full text-sm font-semibold hover:bg-coral-200 hover:scale-105 transition-all duration-300 group"
                    >
                      {AGE_LABELS[age]}
                      <X className="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  )
                })}
                {selectedAges.length > 1 && (
                  <Link
                    href={`/resorts/${countrySlug}`}
                    className="text-sm font-medium text-dark-500 hover:text-coral-600 underline underline-offset-2 transition-colors"
                  >
                    Clear all
                  </Link>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Resort Listings - Design-5 */}
        <div className="container-page py-16 lg:py-20">
          {filteredResorts.length === 0 ? (
            <div className="text-center py-20">
              <div className="mx-auto w-20 h-20 rounded-full bg-dark-100 flex items-center justify-center mb-8">
                <Mountain className="w-10 h-10 text-dark-300" />
              </div>
              <h2 className="font-display text-2xl font-bold text-dark-800 mb-3">
                No resorts match your filters
              </h2>
              <p className="text-lg text-dark-600 mb-6">
                Try adjusting your age filters or browse all {countryName} resorts.
              </p>
              <Button asChild>
                <Link href={`/resorts/${countrySlug}`}>
                  View all {resorts.length} resorts
                </Link>
              </Button>
            </div>
          ) : (
            <div className="animate-in animate-in-3">
              {/* Country header - Design-5 playful style */}
              <div className="flex items-center gap-5 mb-10">
                <div className="p-4 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 shadow-teal">
                  <Globe className="w-7 h-7 text-teal-600" />
                </div>
                <div>
                  <h2 className="font-display text-3xl font-bold text-dark-800">
                    {countryName}
                  </h2>
                  <p className="text-dark-500 font-medium">
                    {filteredResorts.length} {filteredResorts.length === 1 ? 'resort' : 'resorts'}
                    {selectedAges.length > 0 && ` for ${ageDisplayText}`}
                  </p>
                </div>
              </div>

              {/* Resort grid - Design-5 cards with scale + shadow hover */}
              <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                {filteredResorts.map((resort) => (
                  <Link
                    key={resort.id}
                    href={`/resorts/${countrySlug}/${resort.slug}`}
                    className="group"
                  >
                    <div className="resort-card">
                      {/* Resort hero image with fallback */}
                      <div className="resort-card-image aspect-[16/9] bg-gradient-to-br from-teal-100 via-mint-100 to-teal-50 relative overflow-hidden">
                        {(() => {
                          const heroImage = resort.images?.find(img => img.image_type === 'hero')?.image_url
                            || resort.images?.find(img => img.image_type === 'atmosphere')?.image_url
                            || resort.images?.[0]?.image_url
                          return heroImage ? (
                            <Image
                              src={heroImage}
                              alt={`${resort.name} ski resort`}
                              fill
                              className="object-cover transition-transform duration-500 group-hover:scale-105"
                              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <Mountain className="w-14 h-14 text-teal-300 transition-transform duration-500" />
                            </div>
                          )
                        })()}
                      </div>

                      <div className="p-6">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h3 className="font-display text-xl font-semibold text-dark-800 group-hover:text-coral-500 transition-colors">
                              {resort.name}
                            </h3>
                            <p className="mt-1.5 text-dark-500 flex items-center gap-1.5">
                              <MapPin className="w-4 h-4" />
                              {resort.region ? `${resort.region}, ${countryName}` : countryName}
                            </p>
                          </div>

                          {resort.family_metrics?.family_overall_score && (
                            <ScoreBadge
                              score={resort.family_metrics.family_overall_score}
                              badgeSize="sm"
                              showMax={false}
                            />
                          )}
                        </div>

                        {resort.content?.tagline && (
                          <p className="mt-4 text-sm text-dark-500 italic">
                            &ldquo;{resort.content.tagline}&rdquo;
                          </p>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Newsletter CTA - Design-5 Playful Card */}
        <section className="bg-gradient-to-br from-mint-50/50 via-white to-coral-50/30 border-t border-dark-100 py-20">
          <div className="container-page">
            <div className="relative overflow-hidden p-10 sm:p-12 max-w-2xl mx-auto text-center" style={{ borderRadius: '40px', background: 'linear-gradient(145deg, rgba(149, 225, 211, 0.15) 0%, rgba(255, 107, 107, 0.08) 100%)', border: '2px solid rgba(149, 225, 211, 0.3)' }}>
              {/* Decorative elements */}
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
                  Sign up to get notified when we add more {countryName} resorts.
                </p>
                <Button size="lg" className="mt-8" asChild>
                  <Link href="/">
                    Join the Newsletter
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-dark-100 bg-dark-50 py-12">
          <div className="container-page">
            <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
              <div className="text-center sm:text-left">
                <Link href="/" className="font-display text-xl font-bold text-dark-800">
                  Snowthere
                </Link>
                <p className="mt-2 text-sm text-dark-500">
                  Family ski guides made with love for ski families.
                </p>
              </div>

              <div className="flex flex-wrap justify-center gap-6">
                <Link href="/" className="text-sm text-dark-600 hover:text-gold-600 transition-colors">
                  Home
                </Link>
                <Link href="/resorts" className="text-sm text-dark-600 hover:text-gold-600 transition-colors">
                  Resorts
                </Link>
                <Link href="/about" className="text-sm text-dark-600 hover:text-gold-600 transition-colors">
                  About
                </Link>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-dark-100 text-center">
              <p className="text-xs text-dark-400">
                © {new Date().getFullYear()} Snowthere. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      </main>
    </>
  )
}
