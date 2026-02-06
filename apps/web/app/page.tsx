import { Metadata } from 'next'
import { SITE_URL } from '@/lib/constants'
import { sanitizeJSON } from '@/lib/sanitize'
import { supabase } from '@/lib/supabase'
import { Navbar } from '@/components/layout/Navbar'
import { FloatingShapes } from '@/components/home/FloatingShapes'
import { HeroSpielplatz } from '@/components/home/HeroSpielplatz'
import { TradingCardGrid } from '@/components/home/TradingCardGrid'
import { HowItWorks } from '@/components/home/HowItWorks'
import { QuoteHighlight } from '@/components/home/QuoteHighlight'
import { Newsletter } from '@/components/home/Newsletter'
import { Footer } from '@/components/home/Footer'
import { ValueStory } from '@/components/home/ValueStory'
import { WhatMakesUsDifferent } from '@/components/home/WhatMakesUsDifferent'
import { EveryGuideIncludes } from '@/components/home/EveryGuideIncludes'

interface FamilyMetrics {
  family_overall_score: number | null
  best_age_min: number | null
  best_age_max: number | null
}

interface FeaturedResort {
  id: string
  name: string
  slug: string
  country: string
  region: string | null
  // Supabase returns object for 1:1, array for 1:many - handle both
  family_metrics: FamilyMetrics | FamilyMetrics[] | null
  images: { image_url: string; image_type: string }[] | null
}

async function getFeaturedResorts(): Promise<FeaturedResort[]> {
  const { data: resorts } = await supabase
    .from('resorts')
    .select(`
      id,
      name,
      slug,
      country,
      region,
      family_metrics:resort_family_metrics(family_overall_score, best_age_min, best_age_max),
      images:resort_images(image_url, image_type)
    `)
    .eq('status', 'published')
    .not('resort_family_metrics.family_overall_score', 'is', null)
    .limit(20)

  if (!resorts || resorts.length === 0) return []

  // Helper to extract score from family_metrics (handles both object and array)
  const getScore = (metrics: FamilyMetrics | FamilyMetrics[] | null): number => {
    if (!metrics) return 0
    if (Array.isArray(metrics)) {
      return metrics[0]?.family_overall_score ?? 0
    }
    return metrics.family_overall_score ?? 0
  }

  // Sort by family score in JS (Supabase foreignTable ordering is unreliable)
  const sorted = (resorts as FeaturedResort[]).sort((a, b) => {
    const scoreA = getScore(a.family_metrics)
    const scoreB = getScore(b.family_metrics)
    return scoreB - scoreA
  })

  return sorted.slice(0, 4)
}

export const metadata: Metadata = {
  alternates: {
    canonical: `${SITE_URL}/`,
  },
  openGraph: {
    url: `${SITE_URL}/`,
  },
}

// ISR: Revalidate every hour to show updated featured resorts
export const revalidate = 3600

export default async function HomePage() {
  const featuredResorts = await getFeaturedResorts()

  return (
    <main id="main-content" className="min-h-screen bg-white relative">
      {/* Schema.org JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: sanitizeJSON({
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            name: 'Snowthere',
            alternateName: 'Snowthere Family Ski Guides',
            url: 'https://www.snowthere.com',
            description: 'Family ski resort guides with honest reviews, cost breakdowns, and trip planning for parents.',
            potentialAction: {
              '@type': 'SearchAction',
              target: {
                '@type': 'EntryPoint',
                urlTemplate: 'https://www.snowthere.com/resorts?q={search_term_string}',
              },
              'query-input': 'required name=search_term_string',
            },
          }),
        }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: sanitizeJSON({
            '@context': 'https://schema.org',
            '@type': 'Organization',
            name: 'Snowthere',
            url: 'https://www.snowthere.com',
            logo: 'https://www.snowthere.com/logo.png',
            description: 'Family ski resort guides with honest reviews, cost breakdowns, and detailed trip planning.',
            foundingDate: '2026',
            sameAs: [],
          }),
        }}
      />

      {/* Floating geometric shapes with parallax */}
      <FloatingShapes />

      {/* Navigation */}
      <Navbar />

      {/* Hero Section - Server wrapper provides H1, client component adds animation */}
      <HeroSpielplatz />

      {/* Value Story - Alps vs Colorado comparison */}
      <ValueStory />

      {/* How It Works - Easy as 1 2 3 */}
      <HowItWorks />

      {/* Featured Resorts - Trading Cards */}
      <TradingCardGrid resorts={featuredResorts} />

      {/* What Makes Us Different */}
      <WhatMakesUsDifferent />

      {/* Quote Highlight */}
      <QuoteHighlight />

      {/* Every Guide Includes */}
      <EveryGuideIncludes />

      {/* Newsletter */}
      <Newsletter />

      {/* Footer */}
      <Footer />
    </main>
  )
}
