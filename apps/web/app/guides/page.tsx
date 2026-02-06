import { Metadata } from 'next'
import Link from 'next/link'
import { BookOpen, Map, CheckSquare, CreditCard, Snowflake, Calendar } from 'lucide-react'
import { SITE_URL } from '@/lib/constants'
import { sanitizeJSON } from '@/lib/sanitize'
import { supabase } from '@/lib/supabase'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'

export const metadata: Metadata = {
  title: 'Family Ski Guides',
  description:
    'Comprehensive guides for family ski trips - from packing lists to resort comparisons. Everything you need to plan the perfect family ski vacation.',
  alternates: {
    canonical: `${SITE_URL}/guides`,
  },
  openGraph: {
    url: `${SITE_URL}/guides`,
  },
}

// Guide type emojis for placeholder cards
const GUIDE_TYPE_EMOJI: Record<string, string> = {
  comparison: '⛷️',
  'how-to': '✅',
  regional: '🗺️',
  pass: '🎟️',
  seasonal: '📅',
  gear: '🎿',
}

// Guide type icons and colors
const GUIDE_TYPE_CONFIG: Record<
  string,
  { icon: React.ElementType; color: string; label: string }
> = {
  comparison: { icon: Map, color: 'coral', label: 'Resort Comparisons' },
  'how-to': { icon: CheckSquare, color: 'teal', label: 'How-To Guides' },
  regional: { icon: Map, color: 'mint', label: 'Regional Guides' },
  pass: { icon: CreditCard, color: 'gold', label: 'Pass Guides' },
  seasonal: { icon: Calendar, color: 'coral', label: 'Seasonal Guides' },
  gear: { icon: Snowflake, color: 'teal', label: 'Gear & Packing' },
}

interface Guide {
  id: string
  slug: string
  title: string
  guide_type: string
  category: string | null
  excerpt: string | null
  featured_image_url: string | null
  published_at: string | null
}

async function getPublishedGuides(): Promise<Guide[]> {
  const { data, error } = await supabase
    .from('guides')
    .select('id, slug, title, guide_type, category, excerpt, featured_image_url, published_at')
    .eq('status', 'published')
    .order('published_at', { ascending: false })

  if (error) {
    console.error('Error fetching guides:', error)
    return []
  }

  return data || []
}

function GuideCard({ guide }: { guide: Guide }) {
  const config = GUIDE_TYPE_CONFIG[guide.guide_type] || GUIDE_TYPE_CONFIG.comparison
  const Icon = config.icon
  const emoji = GUIDE_TYPE_EMOJI[guide.guide_type] || '📖'

  return (
    <Link href={`/guides/${guide.slug}`}>
      <article className="group bg-white rounded-3xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden h-full flex flex-col">
        {/* Image or placeholder */}
        <div className={`h-40 bg-gradient-to-br from-${config.color}-100 to-${config.color}-200 flex items-center justify-center relative overflow-hidden`}>
          {guide.featured_image_url ? (
            <img
              src={guide.featured_image_url}
              alt={guide.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <span className="text-5xl group-hover:scale-110 transition-transform duration-300" aria-hidden="true">
              {emoji}
            </span>
          )}
          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>

        {/* Content */}
        <div className="p-5 flex-1 flex flex-col">
          {/* Type badge */}
          <span className={`inline-flex items-center gap-1.5 text-xs font-medium text-${config.color}-600 bg-${config.color}-50 px-2.5 py-1 rounded-full w-fit mb-3`}>
            <Icon className="w-3 h-3" />
            {config.label}
          </span>

          {/* Title */}
          <h2 className="font-display text-lg font-bold text-gray-900 group-hover:text-coral-500 transition-colors mb-2 line-clamp-2">
            {guide.title}
          </h2>

          {/* Excerpt */}
          {guide.excerpt && (
            <p className="text-sm text-gray-600 line-clamp-3 flex-1">
              {guide.excerpt}
            </p>
          )}

          {/* Category tag */}
          {guide.category && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-400">
                {guide.category}
              </span>
            </div>
          )}
        </div>
      </article>
    </Link>
  )
}

// ISR: Revalidate every hour
export const revalidate = 3600

export default async function GuidesPage() {
  const guides = await getPublishedGuides()

  // Group guides by type
  const guidesByType = guides.reduce((acc, guide) => {
    const type = guide.guide_type
    if (!acc[type]) acc[type] = []
    acc[type].push(guide)
    return acc
  }, {} as Record<string, Guide[]>)

  // Build ItemList JSON-LD from published guides
  const itemListJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Family Ski Guides',
    description: 'Trip planning guides for family ski vacations.',
    numberOfItems: guides.length,
    itemListElement: guides.map((guide, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: guide.title,
      url: `${SITE_URL}/guides/${guide.slug}`,
      ...(guide.excerpt ? { description: guide.excerpt } : {}),
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: sanitizeJSON(itemListJsonLd) }}
      />
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]">
        {/* Hero Section */}
      <section className="relative py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-gray-600 mb-6">
              <BookOpen className="w-4 h-4 text-coral-500" />
              <span>Family Ski Resources</span>
            </div>

            <h1 className="font-display text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Guides for{' '}
              <span className="text-coral-500">Family</span>{' '}
              Ski Adventures
            </h1>

            <p className="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to plan the perfect family ski trip - from resort comparisons to packing lists, we&apos;ve got you covered.
            </p>
          </div>
        </div>
      </section>

      {/* Guides Content */}
      <section className="pb-20">
        <div className="container mx-auto px-4">
          {guides.length === 0 ? (
            /* Empty state */
            <div className="bg-white rounded-3xl shadow-xl p-12 text-center max-w-2xl mx-auto">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-coral-100 rounded-full mb-6">
                <BookOpen className="w-10 h-10 text-coral-500" />
              </div>
              <h2 className="font-display text-2xl font-bold text-gray-900 mb-4">
                Guides Coming Soon!
              </h2>
              <p className="text-gray-600 mb-6">
                We&apos;re working on comprehensive guides to help you plan the perfect family ski vacation. Check back soon!
              </p>
              <Link
                href="/resorts"
                className="inline-flex items-center gap-2 bg-coral-500 text-white px-6 py-3 rounded-full font-semibold hover:bg-coral-600 transition-colors"
              >
                Browse Resorts
              </Link>
            </div>
          ) : (
            /* Guides by type */
            <div className="space-y-16">
              {Object.entries(guidesByType).map(([type, typeGuides]) => {
                const config = GUIDE_TYPE_CONFIG[type] || GUIDE_TYPE_CONFIG.comparison
                return (
                  <div key={type}>
                    <h2 className="font-display text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                      <config.icon className={`w-6 h-6 text-${config.color}-500`} />
                      {config.label}
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {typeGuides.map((guide) => (
                        <GuideCard key={guide.id} guide={guide} />
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="pb-20">
        <div className="container mx-auto px-4">
          <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12 text-center max-w-3xl mx-auto">
            <h2 className="font-display text-2xl md:text-3xl font-bold text-gray-900 mb-4">
              Not Sure Where to Start?
            </h2>
            <p className="text-gray-600 mb-6">
              Take our quick quiz to find your family&apos;s perfect ski resort match based on your preferences.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/quiz"
                className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-coral-500 to-coral-600 text-white px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:shadow-coral-500/25 transition-all duration-200"
              >
                Take the Quiz
              </Link>
              <Link
                href="/resorts"
                className="inline-flex items-center justify-center gap-2 bg-gray-100 text-gray-700 px-8 py-4 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
              >
                Browse All Resorts
              </Link>
            </div>
          </div>
        </div>
      </section>
      </div>
      <Footer />
    </>
  )
}
