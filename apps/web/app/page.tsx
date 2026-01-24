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

async function getFeaturedResorts() {
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
    .order('family_overall_score', { ascending: false, nullsFirst: false, foreignTable: 'resort_family_metrics' })
    .limit(4)

  return resorts || []
}

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
