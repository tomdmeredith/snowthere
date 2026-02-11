import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { supabase } from '@/lib/supabase'
import { ResortWithDetails, SkiPass } from '@/lib/database.types'
import { SITE_URL } from '@/lib/constants'
import { sanitizeHTML, sanitizeJSON } from '@/lib/sanitize'
import { injectResortLinks } from '@/lib/resort-linker'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { QuickTake } from '@/components/resort/QuickTake'
import { FamilyMetricsTable } from '@/components/resort/FamilyMetricsTable'
import { CostTable } from '@/components/resort/CostTable'
import { SkiCalendar } from '@/components/resort/SkiCalendar'
import { FAQSection } from '@/components/resort/FAQSection'
import { TrailMap, type TrailMapData } from '@/components/resort/TrailMap'
import { HeroImage } from '@/components/resort/HeroImage'
import { TerrainBreakdown } from '@/components/resort/TerrainBreakdown'
import { ContentRenderer } from '@/components/resort/ContentRenderer'
import { QuickScoreSummary } from '@/components/resort/QuickScoreSummary'
import { SimilarResorts } from '@/components/resort/SimilarResorts'
import { UsefulLinks } from '@/components/resort/UsefulLinks'
import { PassCard } from '@/components/resort/PassCard'
import {
  ChevronRight,
  MapPin,
  Star,
  Users,
  Plane,
  Home,
  Ticket,
  Mountain,
  ArrowRight,
  Sparkles,
  Map,
  MessageSquare,
} from 'lucide-react'

interface Props {
  params: { country: string; slug: string }
}

// Supabase .select() with joins returns passes as nested objects before transformation
type SupabaseResortRow = Omit<ResortWithDetails, 'passes'> & {
  passes: { access_type: string | null; pass: SkiPass }[]
}

// Supabase similarity join row shape
interface SimilarityRow {
  similarity_score: number
  resort_a?: { id: string; name: string; country: string; slug: string; status: string }
  resort_b?: { id: string; name: string; country: string; slug: string; status: string }
}

async function getResort(country: string, slug: string): Promise<ResortWithDetails | null> {
  // Convert URL slug back to country name (e.g., "united-states" -> "United States")
  const countryName = decodeURIComponent(country)
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())

  // Normalize slug: decode URI encoding and normalize Unicode (NFC)
  // This fixes mismatches between browser NFD encoding (e.g. macOS) and database NFC storage
  const normalizedSlug = decodeURIComponent(slug).normalize('NFC')

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
      ),
      images:resort_images(*),
      links:resort_links(*)
    `)
    .eq('slug', normalizedSlug)
    .eq('country', countryName)
    .eq('status', 'published')
    .single()

  if (error || !resort) return null

  // Cast Supabase complex join return type to our known shape
  const resortData = resort as unknown as SupabaseResortRow

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
    calendar: Array.isArray(resortData.calendar) ? resortData.calendar : [],
    passes: (Array.isArray(resortData.passes) ? resortData.passes : []).map((p) => ({
      ...p.pass,
      access_type: p.access_type,
    })),
    images: Array.isArray(resortData.images) ? resortData.images : [],
    links: Array.isArray(resortData.links) ? resortData.links : [],
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
    for (const row of similarA as unknown as SimilarityRow[]) {
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
    for (const row of similarB as unknown as SimilarityRow[]) {
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
  const title = seoMeta?.title || `Family Ski Guide: ${resort.name} with Kids${scoreLabel} | Snowthere`

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

  // Find best available OG image from resort images
  const ogImage = resort.images?.find((img) => img.image_type === 'hero')?.image_url
    || resort.images?.find((img) => img.image_type === 'atmosphere')?.image_url
    || null

  // Build canonical URL
  const countrySlug = resort.country.toLowerCase().replace(/\s+/g, '-')
  const canonicalUrl = `${SITE_URL}/resorts/${countrySlug}/${resort.slug}`

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
      title: `Family Ski Guide: ${resort.name} with Kids | Snowthere`,
      description,
      url: canonicalUrl,
      siteName: 'Snowthere',
      locale: 'en_US',
      ...(ogImage && {
        images: [{
          url: ogImage,
          width: 1200,
          height: 630,
          alt: `${resort.name} Family Ski Guide`,
        }],
      }),
    },
    twitter: {
      card: ogImage ? 'summary_large_image' : 'summary',
      title: `${resort.name} Family Ski Guide`,
      description,
      ...(ogImage && { images: [ogImage] }),
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

export const revalidate = 21600 // Revalidate every 6 hours (ISR) - pipeline triggers on-demand when content changes

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
  const rawFaqs = content?.faqs
  const faqs = Array.isArray(rawFaqs) ? rawFaqs as { question: string; answer: string }[] : null

  // Pre-process content sections with resort links (auto-link mentions of other resorts)
  // SEO best practice: Each resort is linked only once per page (first mention wins)
  // We share linkedSlugs across all sections to avoid duplicate links
  const linkedSlugs = new Set<string>()
  const linkedContent = {
    getting_there: content?.getting_there ? sanitizeHTML(await injectResortLinks(content.getting_there as string, resort.name, linkedSlugs)) : null,
    where_to_stay: content?.where_to_stay ? sanitizeHTML(await injectResortLinks(content.where_to_stay as string, resort.name, linkedSlugs)) : null,
    lift_tickets: content?.lift_tickets ? sanitizeHTML(await injectResortLinks(content.lift_tickets as string, resort.name, linkedSlugs)) : null,
    on_mountain: content?.on_mountain ? sanitizeHTML(await injectResortLinks(content.on_mountain as string, resort.name, linkedSlugs)) : null,
    off_mountain: content?.off_mountain ? sanitizeHTML(await injectResortLinks(content.off_mountain as string, resort.name, linkedSlugs)) : null,
    parent_reviews_summary: content?.parent_reviews_summary ? sanitizeHTML(await injectResortLinks(content.parent_reviews_summary as string, resort.name, linkedSlugs)) : null,
  }

  // Find hero and atmosphere images
  const images = resort.images || []
  const heroImage = images.find((img) => img.image_type === 'hero')
  const atmosphereImage = images.find((img) => img.image_type === 'atmosphere')

  // Get links for sidebar
  const links = resort.links || []

  // Build SkiResort schema for SEO/GEO
  const countrySlug = resort.country.toLowerCase().replace(/\s+/g, '-')
  const skiResortSchema = {
    '@context': 'https://schema.org',
    '@type': 'SkiResort',
    name: resort.name,
    description: content?.quick_take
      ? String(content.quick_take).replace(/<[^>]+>/g, '').slice(0, 200)
      : `Family ski resort in ${resort.country}`,
    url: `${SITE_URL}/resorts/${countrySlug}/${resort.slug}`,
    address: {
      '@type': 'PostalAddress',
      addressRegion: resort.region || undefined,
      addressCountry: resort.country,
    },
    geo: resort.latitude && resort.longitude ? {
      '@type': 'GeoCoordinates',
      latitude: resort.latitude,
      longitude: resort.longitude,
    } : undefined,
    priceRange: costs?.estimated_family_daily
      ? costs.estimated_family_daily < 400 ? '$'
        : costs.estimated_family_daily < 600 ? '$$'
        : costs.estimated_family_daily < 900 ? '$$$'
        : '$$$$'
      : undefined,
    amenityFeature: [
      metrics?.has_childcare ? { '@type': 'LocationFeatureSpecification', name: 'Childcare', value: true } : null,
      metrics?.ski_school_min_age != null ? { '@type': 'LocationFeatureSpecification', name: 'Ski School', value: true } : null,
      metrics?.has_magic_carpet ? { '@type': 'LocationFeatureSpecification', name: 'Magic Carpet', value: true } : null,
    ].filter(Boolean),
  }

  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL },
      { '@type': 'ListItem', position: 2, name: 'Resorts', item: `${SITE_URL}/resorts` },
      { '@type': 'ListItem', position: 3, name: resort.country, item: `${SITE_URL}/resorts/${countrySlug}` },
      { '@type': 'ListItem', position: 4, name: resort.name, item: `${SITE_URL}/resorts/${countrySlug}/${resort.slug}` },
    ],
  }

  return (
    <main id="main-content" className="min-h-screen bg-white">
      {/* SkiResort Schema for SEO/GEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: sanitizeJSON(skiResortSchema) }}
      />

      {/* BreadcrumbList Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: sanitizeJSON(breadcrumbSchema) }}
      />

      {/* FAQ Schema - server-rendered for Googlebot */}
      {faqs && faqs.length > 0 && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: sanitizeJSON({
              '@context': 'https://schema.org',
              '@type': 'FAQPage',
              mainEntity: faqs.map((faq) => ({
                '@type': 'Question',
                name: faq.question,
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: faq.answer.replace(/<[^>]+>/g, ''),
                },
              })),
            }),
          }}
        />
      )}

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

      {/* Hero Header - Design-5 Spielplatz Style */}
      <header className="relative py-16 sm:py-24 overflow-hidden">
        {/* Design-5: Warm gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]" />

        {/* Floating Geometric Shapes - Design-5 */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute text-8xl text-[#FF6B6B]/20 top-[10%] left-[5%]">
            ○
          </div>
          <div className="absolute text-9xl text-[#4ECDC4]/20 top-[60%] right-[10%]">
            △
          </div>
          <div className="absolute text-7xl text-[#FFE066]/30 bottom-[20%] left-[15%] rotate-45">
            □
          </div>
          <div className="absolute text-6xl text-[#95E1D3]/20 top-[30%] right-[20%]">
            ◇
          </div>
        </div>

        {/* Decorative gradient orbs */}
        <div className="absolute top-10 right-10 w-64 h-64 bg-coral-200/30 rounded-full blur-3xl" />
        <div className="absolute bottom-10 left-10 w-48 h-48 bg-teal-200/30 rounded-full blur-3xl" />

        <div className="container-page relative z-10">
          <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            {/* Left Column - Text Content */}
            <div className="animate-in animate-in-1">
              <div className="flex items-center gap-2 text-dark-500 mb-4">
                <MapPin className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {resort.region ? `${resort.region}, ${resort.country}` : resort.country}
                </span>
              </div>

              <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-black text-dark-800 tracking-tight leading-[0.95]">
                {resort.name}
              </h1>

              {/* Handwritten tagline - Design-5 */}
              <p className="mt-6 font-accent text-2xl sm:text-3xl text-teal-600 max-w-xl">
                {(content?.tagline as string) || 'Everything you need to plan your family ski trip'}
              </p>

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
                        Ages {metrics.best_age_min}-{metrics.best_age_max}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Right Column - Image with Design-5 Treatment */}
            <div className="animate-in animate-in-2 relative">
              {heroImage ? (
                <div className="relative transform rotate-2 hover:rotate-0 transition-transform duration-500">
                  {/* Colored border frame - Design-5 */}
                  <div className="absolute -inset-3 bg-gradient-to-br from-[#FF6B6B] via-[#FFE066] to-[#4ECDC4] rounded-3xl" />
                  <div className="relative aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl">
                    <Image
                      src={heroImage.image_url}
                      alt={heroImage.alt_text || `${resort.name} ski resort`}
                      fill
                      priority
                      className="object-cover"
                      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 600px"
                    />
                  </div>
                  {/* Fun fact bubble */}
                  {metrics?.family_overall_score && (
                    <div className="absolute -bottom-4 -right-4 bg-white px-4 py-2 rounded-full shadow-lg transform rotate-3 border-2 border-[#4ECDC4]">
                      <span className="text-sm font-bold text-dark-800">
                        ★ {metrics.family_overall_score}/10 Family Score
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                /* Fallback gradient pattern when no image */
                <div className="relative transform rotate-2">
                  <div className="absolute -inset-3 bg-gradient-to-br from-[#FF6B6B] via-[#FFE066] to-[#4ECDC4] rounded-3xl" />
                  <div className="relative aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl bg-gradient-to-br from-dark-100 to-dark-200 flex items-center justify-center">
                    <div className="text-center p-8">
                      <Mountain className="w-16 h-16 text-dark-300 mx-auto mb-4" />
                      <p className="text-dark-400 font-medium">
                        {resort.name}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="container-page py-12 lg:py-16">
        <div className="grid gap-12 lg:grid-cols-3 items-start">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-16">
            {/* Quick Take */}
            {content?.quick_take && (
              <div className="animate-in animate-in-2">
                <QuickTake
                  content={content.quick_take}
                  perfectIf={Array.isArray(metrics?.perfect_if) ? metrics.perfect_if : []}
                  skipIf={Array.isArray(metrics?.skip_if) ? metrics.skip_if : []}
                />
              </div>
            )}

            {/* The Numbers Table — shown when data completeness >= 0.3 */}
            {metrics && metrics.data_completeness != null && metrics.data_completeness >= 0.3 && (
              <div className="animate-in animate-in-3">
                {metrics.data_completeness < 0.6 && (
                  <p className="text-sm text-dark-400 mb-2 italic">
                    Some data is pending verification. We update as we confirm details.
                  </p>
                )}
                <FamilyMetricsTable metrics={metrics} />
              </div>
            )}

            {/* Terrain Breakdown Visual */}
            {metrics?.terrain_beginner_pct != null &&
              metrics?.terrain_intermediate_pct != null &&
              metrics?.terrain_advanced_pct != null && (
                <TerrainBreakdown
                  beginner={metrics.terrain_beginner_pct}
                  intermediate={metrics.terrain_intermediate_pct}
                  advanced={metrics.terrain_advanced_pct}
                />
              )}

            {/* Getting There */}
            {linkedContent.getting_there && (
              <section id="getting-there">
                <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3 mb-8">
                  <span>✈️</span>
                  <span>How Do You Get to {resort.name}?</span>
                </h2>
                <ContentRenderer html={linkedContent.getting_there} />
              </section>
            )}

            {/* Where to Stay */}
            {linkedContent.where_to_stay && (
              <section id="where-to-stay">
                <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3 mb-8">
                  <span>🏠</span>
                  <span>Where Should Your Family Stay?</span>
                </h2>
                <ContentRenderer html={linkedContent.where_to_stay} />
              </section>
            )}

            {/* Lift Tickets & Passes */}
            {linkedContent.lift_tickets && (
              <section id="lift-tickets">
                <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3 mb-8">
                  <span>🎟️</span>
                  <span>How Much Do Lift Tickets Cost at {resort.name}?</span>
                </h2>
                <ContentRenderer html={linkedContent.lift_tickets} />
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
            {linkedContent.on_mountain && (
              <section id="on-mountain">
                <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3 mb-8">
                  <span>⛷️</span>
                  <span>What&apos;s the Skiing Like for Families?</span>
                </h2>
                <ContentRenderer html={linkedContent.on_mountain} />
              </section>
            )}

            {/* Trail Map */}
            <TrailMap
              resortName={resort.name}
              country={resort.country}
              data={resort.trail_map_data as TrailMapData | null}
              latitude={resort.latitude ?? undefined}
              longitude={resort.longitude ?? undefined}
            />

            {/* Off the Mountain */}
            {linkedContent.off_mountain && (
              <section id="off-mountain">
                <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3 mb-8">
                  <span>☕</span>
                  <span>What Can You Do Off the Slopes?</span>
                </h2>
                <ContentRenderer html={linkedContent.off_mountain} />
              </section>
            )}

            {/* Ski Quality Calendar */}
            {resort.calendar.length > 0 && (
              <SkiCalendar calendar={resort.calendar} />
            )}

            {/* Parent Reviews */}
            {linkedContent.parent_reviews_summary && (
              <section id="reviews">
                <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3 mb-8">
                  <span>💬</span>
                  <span>What Do Other Parents Think?</span>
                </h2>
                <ContentRenderer html={linkedContent.parent_reviews_summary} />
              </section>
            )}

            {/* FAQ */}
            {faqs && faqs.length > 0 && <FAQSection faqs={faqs} />}
          </div>

          {/* Sidebar */}
          <aside className="lg:col-span-1 max-w-full overflow-hidden">
            <div className="lg:sticky lg:top-24 space-y-6">
              {/* Family Score Card - Top of sidebar */}
              {metrics && (
                <QuickScoreSummary
                  familyScore={metrics.family_overall_score}
                  bestAgeMin={metrics.best_age_min}
                  bestAgeMax={metrics.best_age_max}
                  perfectIf={metrics.perfect_if || []}
                  skipIf={metrics.skip_if || []}
                  lastUpdated={resort.last_refreshed || resort.updated_at}
                  scoreConfidence={metrics.score_confidence ?? null}
                />
              )}

              {/* Cost Summary Card — shown when metrics completeness >= 0.3 and at least one price exists */}
              {costs && metrics && metrics.data_completeness != null && metrics.data_completeness >= 0.3 &&
                (costs.lift_adult_daily != null || costs.lodging_mid_nightly != null ||
                 costs.meal_family_avg != null || costs.estimated_family_daily != null) && (
                <CostTable costs={costs} />
              )}

              {/* Ski Passes Section */}
              {resort.passes.length > 0 && (
                <div className="bg-white rounded-3xl shadow-card border border-dark-100 p-6">
                  <h3 className="font-display text-lg font-bold text-dark-800 mb-4 flex items-center gap-2">
                    <span>🎟️</span> Ski Passes
                  </h3>
                  <div className="space-y-3">
                    {resort.passes.map((pass, i) => (
                      <PassCard
                        key={pass.id}
                        name={pass.name}
                        accessType={pass.access_type ?? undefined}
                        purchaseUrl={(pass.purchase_url || pass.website_url) ?? undefined}
                        color={(['coral', 'teal', 'gold', 'mint'] as const)[i % 4]}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Jump to Section - Design-5 Card */}
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
                      Getting There?
                    </a>
                  )}
                  {content?.where_to_stay && (
                    <a
                      href="#where-to-stay"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Home className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Where to Stay?
                    </a>
                  )}
                  {content?.lift_tickets && (
                    <a
                      href="#lift-tickets"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Ticket className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Lift Ticket Costs?
                    </a>
                  )}
                  {content?.on_mountain && (
                    <a
                      href="#on-mountain"
                      className="flex items-center gap-3 text-sm text-dark-600 hover:text-coral-500 hover:bg-coral-50 transition-all duration-300 py-2.5 px-3 rounded-xl group"
                    >
                      <Mountain className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Skiing for Families?
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

              {/* Useful Links Section */}
              {links && links.length > 0 && (
                <div className="bg-white rounded-3xl shadow-card border border-dark-100 p-6">
                  <UsefulLinks links={links} resortSlug={resort.slug} />
                </div>
              )}

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
          </aside>
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
