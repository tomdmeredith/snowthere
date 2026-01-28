import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import {
  BookOpen,
  Map,
  CheckSquare,
  CreditCard,
  Snowflake,
  Calendar,
  Clock,
  User,
  ChevronRight,
} from 'lucide-react'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { GuideContent } from '@/components/guides/GuideContent'
import {
  getGuideBySlug,
  getRelatedGuides,
  getAllGuideSlugs,
  GUIDE_TYPE_CONFIG,
  type GuideWithResorts,
  type GuideType,
  type GuideFAQItem,
} from '@/lib/guides'

// Icons for guide type badges (React components can't live in lib/guides.ts)
const GUIDE_TYPE_ICONS: Record<string, React.ElementType> = {
  comparison: Map,
  'how-to': CheckSquare,
  regional: Map,
  pass: CreditCard,
  seasonal: Calendar,
  gear: Snowflake,
}

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://snowthere.com'

// A7: Static generation for all published guides
export async function generateStaticParams() {
  const slugs = await getAllGuideSlugs()
  return slugs.map((slug) => ({ slug }))
}

// A7: ISR revalidation (matches resort pages)
export const revalidate = 43200

// A3: Full metadata with OpenGraph, Twitter, canonical, keywords
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const guide = await getGuideBySlug(slug)

  if (!guide) {
    return { title: 'Guide Not Found | Snowthere' }
  }

  const title = guide.seo_meta?.title || `${guide.title} | Snowthere`
  const description =
    guide.seo_meta?.description ||
    guide.excerpt ||
    `Family ski guide: ${guide.title}`
  const canonicalUrl = `${BASE_URL}/guides/${guide.slug}`
  const keywords = [
    guide.title,
    'family skiing',
    'ski with kids',
    ...(guide.seo_meta?.keywords || []),
  ].filter(Boolean)

  return {
    title,
    description,
    keywords: keywords.join(', '),
    authors: [{ name: guide.author || 'Snowthere' }],
    alternates: {
      canonical: canonicalUrl,
      types: {
        'text/plain': `${canonicalUrl}/llms.txt`,
      },
    },
    openGraph: {
      type: 'article',
      title,
      description,
      url: canonicalUrl,
      siteName: 'Snowthere',
      locale: 'en_US',
      ...(guide.featured_image_url && {
        images: [
          {
            url: guide.featured_image_url,
            width: 1200,
            height: 630,
            alt: guide.title,
          },
        ],
      }),
      ...(guide.published_at && { publishedTime: guide.published_at }),
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      ...(guide.featured_image_url && {
        images: [guide.featured_image_url],
      }),
    },
    other: {
      ...(guide.published_at && {
        'article:published_time': guide.published_at,
      }),
      'article:modified_time': guide.updated_at,
    },
  }
}

// A2: Build Schema.org JSON-LD schemas
function buildSchemas(guide: GuideWithResorts) {
  const schemas: Record<string, unknown>[] = []
  const canonicalUrl = `${BASE_URL}/guides/${guide.slug}`

  // Article schema (all guides)
  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: guide.title,
    description: guide.seo_meta?.description || guide.excerpt || undefined,
    url: canonicalUrl,
    author: { '@type': 'Organization', name: 'Snowthere', url: BASE_URL },
    publisher: { '@type': 'Organization', name: 'Snowthere', url: BASE_URL },
    ...(guide.published_at && { datePublished: guide.published_at }),
    dateModified: guide.updated_at,
    ...(guide.featured_image_url && { image: guide.featured_image_url }),
  })

  // BreadcrumbList schema
  schemas.push({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: BASE_URL },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Guides',
        item: `${BASE_URL}/guides`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: guide.title,
        item: canonicalUrl,
      },
    ],
  })

  // FAQPage schema for guides with FAQ sections
  const faqItems = (guide.content?.sections || [])
    .filter((s) => s.type === 'faq')
    .flatMap((s) => (s.items || []) as GuideFAQItem[])
    .filter((item) => item.question && item.answer)

  if (faqItems.length > 0) {
    schemas.push({
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqItems.map((item) => ({
        '@type': 'Question',
        name: item.question,
        acceptedAnswer: { '@type': 'Answer', text: item.answer },
      })),
    })
  }

  return schemas
}

export default async function GuidePage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const guide = await getGuideBySlug(slug)

  if (!guide) {
    notFound()
  }

  // C2: Fetch related guides by same type
  const relatedGuides = await getRelatedGuides(slug, guide.guide_type, 3)

  // C1: Build resort slug -> country slug map for correct URLs
  const resortCountryMap: Record<string, string> = {}
  if (guide.guide_resorts) {
    for (const gr of guide.guide_resorts) {
      const resort = gr.resort
      if (resort?.slug && resort?.country) {
        resortCountryMap[resort.slug] = resort.country
          .toLowerCase()
          .replace(/\s+/g, '-')
      }
    }
  }

  const typeConfig = GUIDE_TYPE_CONFIG[guide.guide_type as GuideType]
  const Icon = GUIDE_TYPE_ICONS[guide.guide_type] || BookOpen

  const publishedDate = guide.published_at
    ? new Date(guide.published_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  const schemas = buildSchemas(guide)

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]">
        {/* A2: Schema.org JSON-LD */}
        {schemas.map((schema, i) => (
          <script
            key={i}
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
          />
        ))}

        {/* C3: Breadcrumb navigation */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-gray-100">
          <div className="container mx-auto px-4 py-4">
            <nav
              aria-label="Breadcrumb"
              className="flex items-center gap-2 text-sm text-gray-500"
            >
              <Link href="/" className="hover:text-gray-900 transition-colors">
                Home
              </Link>
              <ChevronRight className="w-3 h-3" />
              <Link
                href="/guides"
                className="hover:text-gray-900 transition-colors"
              >
                Guides
              </Link>
              <ChevronRight className="w-3 h-3" />
              <span className="text-gray-900 font-medium truncate max-w-[200px] md:max-w-none">
                {guide.title}
              </span>
            </nav>
          </div>
        </header>

        {/* Hero Section */}
        <section className="py-12 md:py-16">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center">
              <span
                className={`inline-flex items-center gap-2 text-sm font-medium text-${typeConfig?.color || 'coral'}-600 bg-${typeConfig?.color || 'coral'}-50 px-4 py-2 rounded-full mb-6`}
              >
                <Icon className="w-4 h-4" />
                {typeConfig?.label || 'Guide'}
              </span>

              <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
                {guide.title}
              </h1>

              {guide.excerpt && (
                <p className="text-lg md:text-xl text-gray-600 mb-6">
                  {guide.excerpt}
                </p>
              )}

              <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
                {guide.author && (
                  <div className="flex items-center gap-1.5">
                    <User className="w-4 h-4" />
                    <span>{guide.author}</span>
                  </div>
                )}
                {publishedDate && (
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4" />
                    <span>{publishedDate}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Featured Image */}
        {guide.featured_image_url && (
          <section className="pb-12">
            <div className="container mx-auto px-4">
              <div className="max-w-4xl mx-auto">
                <img
                  src={guide.featured_image_url}
                  alt={guide.title}
                  className="w-full rounded-2xl shadow-xl"
                />
              </div>
            </div>
          </section>
        )}

        {/* Content Sections */}
        <section className="pb-20">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto">
              <GuideContent
                sections={guide.content?.sections || []}
                resortCountryMap={resortCountryMap}
              />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="pb-20">
          <div className="container mx-auto px-4">
            <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12 text-center max-w-2xl mx-auto">
              <h2 className="font-display text-2xl font-bold text-gray-900 mb-4">
                Ready to Plan Your Trip?
              </h2>
              <p className="text-gray-600 mb-6">
                Explore our resort guides for detailed information on
                family-friendly ski destinations.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  href="/resorts"
                  className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-coral-500 to-coral-600 text-white px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:shadow-coral-500/25 transition-all duration-200"
                >
                  Browse Resorts
                </Link>
                <Link
                  href="/quiz"
                  className="inline-flex items-center justify-center gap-2 bg-gray-100 text-gray-700 px-8 py-4 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
                >
                  Take the Quiz
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* C2: Related Guides */}
        {relatedGuides.length > 0 && (
          <section className="pb-20">
            <div className="container mx-auto px-4">
              <div className="max-w-3xl mx-auto">
                <h2 className="font-display text-2xl font-bold text-gray-900 mb-6">
                  More {typeConfig?.label || 'Guides'}
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {relatedGuides.map((related) => {
                    const relatedConfig =
                      GUIDE_TYPE_CONFIG[related.guide_type as GuideType]
                    return (
                      <Link
                        key={related.slug}
                        href={`/guides/${related.slug}`}
                        className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow group"
                      >
                        <span
                          className={`text-xs font-medium text-${relatedConfig?.color || 'coral'}-600`}
                        >
                          {relatedConfig?.label || 'Guide'}
                        </span>
                        <h3 className="font-semibold text-gray-900 mt-1 group-hover:text-coral-500 transition-colors">
                          {related.title}
                        </h3>
                        {related.excerpt && (
                          <p className="text-gray-500 text-sm mt-2 line-clamp-2">
                            {related.excerpt}
                          </p>
                        )}
                      </Link>
                    )
                  })}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
      <Footer />
    </>
  )
}
