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

interface FeaturedResort {
  id: string
  name: string
  slug: string
  country: string
  region: string | null
  family_metrics: { family_overall_score: number | null; best_age_min: number | null; best_age_max: number | null }[] | null
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

  // Sort by family score in JS (Supabase foreignTable ordering is unreliable)
  const sorted = (resorts as FeaturedResort[]).sort((a, b) => {
    const scoreA = a.family_metrics?.[0]?.family_overall_score ?? 0
    const scoreB = b.family_metrics?.[0]?.family_overall_score ?? 0
    return scoreB - scoreA
  })

  return sorted.slice(0, 4)
}

// Force dynamic rendering to ensure fresh data and correct sorting
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  const featuredResorts = await getFeaturedResorts()

  return (
    <main className="min-h-screen bg-white relative">
      {/* Floating geometric shapes with parallax */}
      <FloatingShapes />

      {/* Navigation */}
      <Navbar />

      {/* Hero Section - Tilted image + stacked headline */}
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
