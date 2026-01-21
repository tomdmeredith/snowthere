import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import { ResortWithDetails } from '@/lib/database.types'
import { createSanitizedHTML } from '@/lib/sanitize'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { QuickTake } from '@/components/resort/QuickTake'
import { FamilyMetricsTable } from '@/components/resort/FamilyMetricsTable'
import { CostTable } from '@/components/resort/CostTable'
import { SkiCalendar } from '@/components/resort/SkiCalendar'
import { FAQSection } from '@/components/resort/FAQSection'
import { AIDisclosure, AIDisclaimerFooter } from '@/components/resort/AIDisclosure'
import { TrailMap } from '@/components/resort/TrailMap'
import { SimilarResorts } from '@/components/resort/SimilarResorts'
import {
  ChevronRight,
  MapPin,
  Star,
  Users,
  Plane,
  Home,
  Ticket,
  Mountain,
  Coffee,
  MessageSquare,
  ArrowRight,
  Sparkles,
  Map,
} from 'lucide-react'

interface Props {
  params: { country: string; slug: string }
}

async function getResort(country: string, slug: string): Promise<ResortWithDetails | null> {
  // Convert URL slug back to country name (e.g., "united-states" -> "United States")
  const countryName = decodeURIComponent(country)
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())

  const { data: resort, error } = await supabase
    .from('resorts')
    .select(`
      *,
      family_metrics:resort_family_metrics(*),
      content:resort_content(*),
      costs:resort_costs(*),
      calendar:ski_quality_calendar(*),
      passes:resort_passes(
        access_type,
        pass:ski_passes(*)
      )
    `)
    .eq('slug', slug)
    .eq('country', countryName)
    .eq('status', 'published')
    .single()

  if (error || !resort) return null

  // Cast resort to any to avoid TypeScript spread issues with Supabase's complex return type
  const resortData = resort as any

  // Transform the passes relation
  const transformedResort: ResortWithDetails = {
    id: resortData.id,
    slug: resortData.slug,
    name: resortData.name,
    country: resortData.country,
    region: resortData.region,
    latitude: resortData.latitude,
    longitude: resortData.longitude,
    status: resortData.status,
    created_at: resortData.created_at,
    updated_at: resortData.updated_at,
    last_refreshed: resortData.last_refreshed,
    trail_map_data: resortData.trail_map_data,
    family_metrics: resortData.family_metrics,
    content: resortData.content,
    costs: resortData.costs,
    calendar: resortData.calendar || [],
    passes: (resortData.passes || []).map((p: any) => ({
      ...p.pass,
      access_type: p.access_type,
    })),
  }

  return transformedResort
}

interface SimilarResortData {
  resort_id: string
  name: string
  country: string
  slug: string
  similarity_score: number
  family_overall_score: number | null
}

async function getSimilarResorts(resortId: string, limit: number = 6): Promise<SimilarResortData[]> {
  // Query from both directions since resort_a_id < resort_b_id constraint
  const { data: similarA } = await supabase
    .from('resort_similarities')
    .select(`
      similarity_score,
      resort_b:resorts!resort_similarities_resort_b_id_fkey(
        id,
        name,
        country,
        slug,
        status
      )
    `)
    .eq('resort_a_id', resortId)
    .gte('similarity_score', 0.3)
    .order('similarity_score', { ascending: false })
    .limit(limit)

  const { data: similarB } = await supabase
    .from('resort_similarities')
    .select(`
      similarity_score,
      resort_a:resorts!resort_similarities_resort_a_id_fkey(
        id,
        name,
        country,
        slug,
        status
      )
    `)
    .eq('resort_b_id', resortId)
    .gte('similarity_score', 0.3)
    .order('similarity_score', { ascending: false })
    .limit(limit)

  // Combine and filter published resorts
  const results: SimilarResortData[] = []

  if (similarA) {
    for (const row of similarA as any[]) {
      if (row.resort_b?.status === 'published') {
        // Fetch family score separately
        const { data: metricsData } = await supabase
          .from('resort_family_metrics')
          .select('family_overall_score')
          .eq('resort_id', row.resort_b.id)
          .single()
        const metrics = metricsData as { family_overall_score: number | null } | null

        results.push({
          resort_id: row.resort_b.id,
          name: row.resort_b.name,
          country: row.resort_b.country,
          slug: row.resort_b.slug,
          similarity_score: row.similarity_score,
          family_overall_score: metrics?.family_overall_score ?? null,
        })
      }
    }
  }

  if (similarB) {
    for (const row of similarB as any[]) {
      if (row.resort_a?.status === 'published') {
        // Fetch family score separately
        const { data: metricsData } = await supabase
          .from('resort_family_metrics')
          .select('family_overall_score')
          .eq('resort_id', row.resort_a.id)
          .single()
        const metrics = metricsData as { family_overall_score: number | null } | null

        results.push({
          resort_id: row.resort_a.id,
          name: row.resort_a.name,
          country: row.resort_a.country,
          slug: row.resort_a.slug,
          similarity_score: row.similarity_score,
          family_overall_score: metrics?.family_overall_score ?? null,
        })
      }
    }
  }

  // Sort by similarity and limit
  return results
    .sort((a, b) => b.similarity_score - a.similarity_score)
    .slice(0, limit)
}

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://snowthere.com'

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const resort = await getResort(params.country, params.slug)
  if (!resort) return { title: 'Resort Not Found' }

  const seoMeta = resort.content?.seo_meta as { title?: string; description?: string } | null
  const metrics = resort.family_metrics
  const costs = resort.costs
  const quickTake = resort.content?.quick_take as string | null

  // Build rich title with family score if available
  const familyScore = metrics?.family_overall_score
  const scoreLabel = familyScore ? ` (${familyScore}/10 Family Score)` : ''
  const title = seoMeta?.title || `${resort.name} Family Ski Guide${scoreLabel} | Snowthere`

  // Build rich description with age range and key details
  const ageRange =
    metrics?.best_age_min && metrics?.best_age_max
      ? `Best for ages ${metrics.best_age_min}-${metrics.best_age_max}. `
      : ''
  const terrainPct = metrics?.kid_friendly_terrain_pct
    ? `${metrics.kid_friendly_terrain_pct}% kid-friendly terrain. `
    : ''
  const dailyCost = costs?.estimated_family_daily
    ? `Est. $${costs.estimated_family_daily}/day for family of 4. `
    : ''

  // Use quick_take for description if available, otherwise build from data
  const description =
    seoMeta?.description ||
    (quickTake
      ? quickTake.slice(0, 155) + (quickTake.length > 155 ? '...' : '')
      : `${ageRange}${terrainPct}${dailyCost}Complete family guide to skiing at ${resort.name}, ${resort.country}. Kid-friendly terrain, real costs, and honest parent reviews.`)

  // Build canonical URL
  const countrySlug = resort.country.toLowerCase().replace(/\s+/g, '-')
  const canonicalUrl = `${BASE_URL}/resorts/${countrySlug}/${resort.slug}`

  // Build keywords from resort data
  const keywords = [
    resort.name,
    `${resort.name} family skiing`,
    `${resort.name} with kids`,
    `${resort.country} ski resorts`,
    `${resort.country} family ski vacation`,
    'family ski resort',
    'skiing with kids',
    'kid-friendly ski resort',
  ]
  if (resort.region) {
    keywords.push(`${resort.region} skiing`)
  }

  return {
    title,
    description,
    keywords: keywords.join(', '),
    authors: [{ name: 'Snowthere' }],
    alternates: {
      canonical: canonicalUrl,
      types: {
        'text/plain': `${canonicalUrl}/llms.txt`,
      },
    },
    openGraph: {
      type: 'article',
      title: `${resort.name} Family Ski Guide | Snowthere`,
      description,
      url: canonicalUrl,
      siteName: 'Snowthere',
      locale: 'en_US',
      images: [
        {
          url: `${BASE_URL}/og/resort-${resort.slug}.png`,
          width: 1200,
          height: 630,
          alt: `${resort.name} Family Ski Guide`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${resort.name} Family Ski Guide`,
      description,
      images: [`${BASE_URL}/og/resort-${resort.slug}.png`],
    },
    other: {
      'article:published_time': resort.created_at,
      'article:modified_time': resort.last_refreshed || resort.updated_at,
      'geo.region': resort.country,
      'geo.placename': resort.name,
    },
  }
}

export async function generateStaticParams() {
  const { data: resorts } = await supabase
    .from('resorts')
    .select('country, slug')
    .eq('status', 'published')

  return ((resorts || []) as { country: string; slug: string }[]).map((resort) => ({
    country: resort.country.toLowerCase().replace(/\s+/g, '-'),
    slug: resort.slug,
  }))
}

export const revalidate = 3600 // Revalidate every hour

export default async function ResortPage({ params }: Props) {
  const resort = await getResort(params.country, params.slug)

  if (!resort) {
    notFound()
  }

  // Fetch similar resorts
  const similarResorts = await getSimilarResorts(resort.id, 6)

  const content = resort.content
  const metrics = resort.family_metrics
  const costs = resort.costs
  const faqs = content?.faqs as { question: string; answer: string }[] | null

  return (
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <Navbar />

      {/* Breadcrumb */}
      <nav className="bg-dark-50 py-4 border-b border-dark-100">
        <div className="container-page">
          <ol className="breadcrumb">
            <li>
              <Link href="/" className="hover:text-coral-500 transition-colors">
                Home
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <Link href="/resorts" className="hover:text-coral-500 transition-colors">
                Resorts
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <Link
                href={`/resorts/${params.country}`}
                className="hover:text-coral-500 transition-colors capitalize"
              >
                {decodeURIComponent(params.country).replace(/-/g, ' ')}
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li className="text-dark-800 font-medium">{resort.name}</li>
          </ol>
        </div>
      </nav>

      {/* Hero Header - Design-5 Warm Gradient */}
      <header className="relative py-20 sm:py-28 overflow-hidden">
        {/* Design-5: "Sunset on snow" warm gradient background */}
        <div className="absolute inset-0 hero-gradient" />

        {/* Decorative gradient orbs */}
        <div className="absolute top-10 right-10 w-64 h-64 bg-coral-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-10 w-48 h-48 bg-teal-200/30 rounded-full blur-3xl" />

        <div className="container-page relative z-10">
          <div className="animate-in animate-in-1">
            <div className="flex items-center gap-2 text-dark-500 mb-4">
              <MapPin className="w-4 h-4" />
              <span className="text-sm font-medium">
                {resort.region}, {resort.country}
              </span>
            </div>

            <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-black text-dark-800 tracking-tight leading-[0.95]">
              {resort.name}
            </h1>

            {metrics && (
              <div className="mt-8 flex flex-wrap items-center gap-4">
                {/* Design-5: Score badge with coral gradient */}
                <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-br from-coral-500 to-coral-600 text-white rounded-full shadow-coral font-semibold">
                  <Star className="w-5 h-5 text-white" />
                  <span className="text-lg">
                    Family Score: <strong>{metrics.family_overall_score}/10</strong>
                  </span>
                </div>

                {metrics.best_age_min && metrics.best_age_max && (
                  <div className="flex items-center gap-2 px-4 py-2 bg-teal-100 text-teal-700 rounded-full font-medium">
                    <Users className="w-4 h-4" />
                    <span>
                      Best for ages {metrics.best_age_min} to {metrics.best_age_max}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Handwritten tagline - Design-5 */}
            <p className="mt-8 font-accent text-2xl sm:text-3xl text-teal-600 max-w-xl">
              Everything you need to plan your family ski trip
            </p>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container-page py-12 lg:py-16">
        <div className="grid gap-12 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-16">
            {/* Quick Take */}
            {content?.quick_take && (
              <div className="animate-in animate-in-2">
                <QuickTake
                  content={content.quick_take}
                  perfectIf={metrics?.perfect_if || []}
                  skipIf={metrics?.skip_if || []}
                />
              </div>
            )}

            {/* The Numbers Table */}
            {metrics && (
              <div className="animate-in animate-in-3">
                <FamilyMetricsTable metrics={metrics} />
              </div>
            )}

            {/* Getting There */}
            {content?.getting_there && (
              <section id="getting-there">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-gold-100 to-gold-50 shadow-gold">
                    <Plane className="w-6 h-6 text-gold-600" />
                  </div>
                  <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
                    <span>✈️</span>
                    <span>Getting There</span>
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={createSanitizedHTML(content.getting_there)}
                />
              </section>
            )}

            {/* Where to Stay */}
            {content?.where_to_stay && (
              <section id="where-to-stay">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 shadow-teal">
                    <Home className="w-6 h-6 text-teal-600" />
                  </div>
                  <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
                    <span>🏠</span>
                    <span>Where to Stay</span>
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={createSanitizedHTML(content.where_to_stay)}
                />
              </section>
            )}

            {/* Lift Tickets & Passes */}
            {content?.lift_tickets && (
              <section id="lift-tickets">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-coral-50 shadow-coral">
                    <Ticket className="w-6 h-6 text-coral-600" />
                  </div>
                  <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
                    <span>🎟️</span>
                    <span>Lift Tickets & Passes</span>
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={createSanitizedHTML(content.lift_tickets)}
                />
                {resort.passes.length > 0 && (
                  <div className="mt-8">
                    <h3 className="font-display font-semibold text-dark-800 mb-4">
                      Available Passes
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {resort.passes.map((pass) => (
                        <a
                          key={pass.id}
                          href={pass.purchase_url || pass.website_url || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="badge badge-pass hover:bg-dark-200 transition-colors"
                        >
                          {pass.name}
                          {pass.access_type && (
                            <span className="text-dark-500 ml-1">({pass.access_type})</span>
                          )}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}

            {/* On the Mountain */}
            {content?.on_mountain && (
              <section id="on-mountain">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 shadow-teal">
                    <Mountain className="w-6 h-6 text-teal-600" />
                  </div>
                  <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
                    <span>⛷️</span>
                    <span>On the Mountain</span>
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={createSanitizedHTML(content.on_mountain)}
                />
              </section>
            )}

            {/* Trail Map */}
            <TrailMap
              resortName={resort.name}
              country={resort.country}
              data={resort.trail_map_data as any}
              latitude={resort.latitude ?? undefined}
              longitude={resort.longitude ?? undefined}
            />

            {/* Off the Mountain */}
            {content?.off_mountain && (
              <section id="off-mountain">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-gold-100 to-gold-50 shadow-gold">
                    <Coffee className="w-6 h-6 text-gold-600" />
                  </div>
                  <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
                    <span>☕</span>
                    <span>Off the Mountain</span>
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={createSanitizedHTML(content.off_mountain)}
                />
              </section>
            )}

            {/* Ski Quality Calendar */}
            {resort.calendar.length > 0 && (
              <SkiCalendar calendar={resort.calendar} />
            )}

            {/* Parent Reviews */}
            {content?.parent_reviews_summary && (
              <section id="reviews">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-coral-50 shadow-coral">
                    <MessageSquare className="w-6 h-6 text-coral-600" />
                  </div>
                  <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
                    <span>💬</span>
                    <span>What Parents Say</span>
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={createSanitizedHTML(content.parent_reviews_summary)}
                />
              </section>
            )}

            {/* FAQ */}
            {faqs && faqs.length > 0 && <FAQSection faqs={faqs} />}

            {/* AI Disclosure */}
            <AIDisclosure className="mt-16" />
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Cost Summary Card */}
              {costs && <CostTable costs={costs} />}

              {/* Quick Links - Design-5 Card */}
              <div className="bg-white rounded-3xl shadow-card border border-dark-100 p-6">
                <h3 className="font-display text-lg font-bold text-dark-800 mb-5">
                  Jump to Section
                </h3>
                <nav className="space-y-1">
                  {content?.quick_take && (
                    <a
                      href="#quick-take"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Sparkles className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Quick Take
                    </a>
                  )}
                  {content?.getting_there && (
                    <a
                      href="#getting-there"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Plane className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Getting There
                    </a>
                  )}
                  {content?.where_to_stay && (
                    <a
                      href="#where-to-stay"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Home className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Where to Stay
                    </a>
                  )}
                  {content?.lift_tickets && (
                    <a
                      href="#lift-tickets"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Ticket className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Lift Tickets
                    </a>
                  )}
                  {content?.on_mountain && (
                    <a
                      href="#on-mountain"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Mountain className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      On the Mountain
                    </a>
                  )}
                  <a
                    href="#trail-map"
                    className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                  >
                    <Map className="w-4 h-4 group-hover:scale-110 transition-transform" />
                    Trail Map
                  </a>
                  {faqs && faqs.length > 0 && (
                    <a
                      href="#faq"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <MessageSquare className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      FAQ
                    </a>
                  )}
                  {similarResorts.length > 0 && (
                    <a
                      href="#similar-resorts"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Mountain className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Similar Resorts
                    </a>
                  )}
                </nav>
              </div>

              {/* Newsletter CTA - Design-5 Playful Card */}
              <div className="relative overflow-hidden p-8" style={{ borderRadius: '32px', background: 'linear-gradient(145deg, rgba(149, 225, 211, 0.15) 0%, rgba(255, 107, 107, 0.08) 100%)', border: '2px solid rgba(149, 225, 211, 0.3)' }}>
                {/* Decorative elements */}
                <div className="absolute top-3 right-3 w-12 h-12 bg-coral-100 rounded-full opacity-50 blur-2xl" />
                <div className="absolute bottom-3 left-3 w-10 h-10 bg-teal-100 rounded-full opacity-50 blur-2xl" />

                <div className="relative z-10 text-center">
                  <span className="font-accent text-2xl text-teal-600">
                    Planning a trip?
                  </span>
                  <p className="mt-3 text-sm text-dark-600">
                    Get our free family ski trip checklist and monthly deal alerts.
                  </p>
                  <button className="w-full mt-5 px-6 py-3.5 bg-gradient-to-r from-coral-500 to-coral-600 text-white font-semibold rounded-full shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all duration-300 flex items-center justify-center gap-2">
                    Get the Checklist
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Similar Resorts - Design-5 Warm Gradient Background */}
      {similarResorts.length > 0 && (
        <section className="relative py-20 border-t border-dark-100 overflow-hidden">
          {/* Design-5: Warm gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-mint-50/50 via-white to-coral-50/30" />
          <div className="container-page relative z-10">
            <SimilarResorts
              resorts={similarResorts}
              currentResortName={resort.name}
              currentCountry={resort.country}
            />
          </div>
        </section>
      )}

      {/* Footer */}
      <Footer />
    </main>
  )
}
