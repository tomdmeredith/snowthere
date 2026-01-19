import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import { ResortWithDetails } from '@/lib/database.types'
import { QuickTake } from '@/components/resort/QuickTake'
import { FamilyMetricsTable } from '@/components/resort/FamilyMetricsTable'
import { CostTable } from '@/components/resort/CostTable'
import { SkiCalendar } from '@/components/resort/SkiCalendar'
import { FAQSection } from '@/components/resort/FAQSection'
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
    <main className="min-h-screen bg-ivory-50">
      {/* Breadcrumb */}
      <nav className="bg-ivory-100 py-4 border-b border-ivory-200">
        <div className="container-page">
          <ol className="breadcrumb">
            <li>
              <Link href="/" className="hover:text-cashmere-600 transition-colors">
                Home
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <Link href="/resorts" className="hover:text-cashmere-600 transition-colors">
                Resorts
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <Link
                href={`/resorts/${params.country}`}
                className="hover:text-cashmere-600 transition-colors capitalize"
              >
                {decodeURIComponent(params.country).replace(/-/g, ' ')}
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li className="text-espresso-900 font-medium">{resort.name}</li>
          </ol>
        </div>
      </nav>

      {/* Hero Header */}
      <header className="hero py-16 sm:py-20">
        <div className="container-page relative z-10">
          <div className="animate-in animate-in-1">
            <div className="flex items-center gap-2 text-powder-300 mb-3">
              <MapPin className="w-4 h-4" />
              <span className="text-sm font-medium">
                {resort.region}, {resort.country}
              </span>
            </div>

            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-ivory-50 tracking-tight">
              {resort.name}
            </h1>

            {metrics && (
              <div className="mt-6 flex flex-wrap items-center gap-4">
                <div className="quick-take-score">
                  <Star className="w-5 h-5 text-cashmere-400" />
                  <span className="text-lg">
                    Family Score: <strong>{metrics.family_overall_score}/10</strong>
                  </span>
                </div>

                {metrics.best_age_min && metrics.best_age_max && (
                  <div className="flex items-center gap-2 text-powder-200">
                    <Users className="w-4 h-4" />
                    <span>
                      Best for ages {metrics.best_age_min}–{metrics.best_age_max}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Handwritten tagline */}
            <p className="mt-6 font-accent text-2xl text-cashmere-300 max-w-xl">
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
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-cashmere-100">
                    <Plane className="w-5 h-5 text-cashmere-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-900">
                    Getting There
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.getting_there }}
                />
              </section>
            )}

            {/* Where to Stay */}
            {content?.where_to_stay && (
              <section id="where-to-stay">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-powder-100">
                    <Home className="w-5 h-5 text-powder-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-900">
                    Where to Stay
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.where_to_stay }}
                />
              </section>
            )}

            {/* Lift Tickets & Passes */}
            {content?.lift_tickets && (
              <section id="lift-tickets">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-lodge-100">
                    <Ticket className="w-5 h-5 text-lodge-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-900">
                    Lift Tickets & Passes
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.lift_tickets }}
                />
                {resort.passes.length > 0 && (
                  <div className="mt-8">
                    <h3 className="font-display font-semibold text-espresso-900 mb-4">
                      Available Passes
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {resort.passes.map((pass) => (
                        <a
                          key={pass.id}
                          href={pass.purchase_url || pass.website_url || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="badge badge-pass hover:bg-espresso-200 transition-colors"
                        >
                          {pass.name}
                          {pass.access_type && (
                            <span className="text-espresso-500 ml-1">({pass.access_type})</span>
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
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-sage-100">
                    <Mountain className="w-5 h-5 text-sage-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-900">
                    On the Mountain
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.on_mountain }}
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
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-cashmere-100">
                    <Coffee className="w-5 h-5 text-cashmere-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-900">
                    Off the Mountain
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.off_mountain }}
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
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-lodge-100">
                    <MessageSquare className="w-5 h-5 text-lodge-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-espresso-900">
                    What Parents Say
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{
                    __html: content.parent_reviews_summary,
                  }}
                />
              </section>
            )}

            {/* FAQ */}
            {faqs && faqs.length > 0 && <FAQSection faqs={faqs} />}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-8 space-y-6">
              {/* Cost Summary Card */}
              {costs && <CostTable costs={costs} />}

              {/* Quick Links */}
              <div className="card">
                <h3 className="font-display font-semibold text-espresso-900 mb-4">
                  Jump to Section
                </h3>
                <nav className="space-y-2">
                  {content?.quick_take && (
                    <a
                      href="#quick-take"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <Sparkles className="w-4 h-4" />
                      Quick Take
                    </a>
                  )}
                  {content?.getting_there && (
                    <a
                      href="#getting-there"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <Plane className="w-4 h-4" />
                      Getting There
                    </a>
                  )}
                  {content?.where_to_stay && (
                    <a
                      href="#where-to-stay"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <Home className="w-4 h-4" />
                      Where to Stay
                    </a>
                  )}
                  {content?.lift_tickets && (
                    <a
                      href="#lift-tickets"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <Ticket className="w-4 h-4" />
                      Lift Tickets
                    </a>
                  )}
                  {content?.on_mountain && (
                    <a
                      href="#on-mountain"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <Mountain className="w-4 h-4" />
                      On the Mountain
                    </a>
                  )}
                  <a
                    href="#trail-map"
                    className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                  >
                    <Map className="w-4 h-4" />
                    Trail Map
                  </a>
                  {faqs && faqs.length > 0 && (
                    <a
                      href="#faq"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <MessageSquare className="w-4 h-4" />
                      FAQ
                    </a>
                  )}
                  {similarResorts.length > 0 && (
                    <a
                      href="#similar-resorts"
                      className="flex items-center gap-2 text-sm text-espresso-600 hover:text-cashmere-600 transition-colors py-1"
                    >
                      <Mountain className="w-4 h-4" />
                      Similar Resorts
                    </a>
                  )}
                </nav>
              </div>

              {/* Newsletter CTA */}
              <div className="card card-warm">
                <div className="text-center">
                  <span className="font-accent text-2xl text-cashmere-600">
                    Planning a trip?
                  </span>
                  <p className="mt-2 text-sm text-espresso-600">
                    Get our free family ski trip checklist and monthly deal alerts.
                  </p>
                  <button className="btn btn-primary w-full mt-4">
                    Get the Checklist
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Similar Resorts */}
      {similarResorts.length > 0 && (
        <section className="bg-ivory-100 py-16 border-t border-ivory-200">
          <div className="container-page">
            <SimilarResorts
              resorts={similarResorts}
              currentResortName={resort.name}
              currentCountry={resort.country}
            />
          </div>
        </section>
      )}
    </main>
  )
}
