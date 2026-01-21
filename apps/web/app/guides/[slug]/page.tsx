import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, BookOpen, Map, CheckSquare, CreditCard, Snowflake, Calendar, Clock, User } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import { createSanitizedHTML } from '@/lib/sanitize'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'

// Guide type configuration
const GUIDE_TYPE_CONFIG: Record<
  string,
  { icon: React.ElementType; color: string; label: string }
> = {
  comparison: { icon: Map, color: 'coral', label: 'Resort Comparison' },
  'how-to': { icon: CheckSquare, color: 'teal', label: 'How-To Guide' },
  regional: { icon: Map, color: 'mint', label: 'Regional Guide' },
  pass: { icon: CreditCard, color: 'gold', label: 'Pass Guide' },
  seasonal: { icon: Calendar, color: 'coral', label: 'Seasonal Guide' },
  gear: { icon: Snowflake, color: 'teal', label: 'Gear Guide' },
}

interface GuideContent {
  sections: Array<{
    type: string
    title?: string
    content?: string
    items?: Array<{
      name?: string
      description?: string
      resort_slug?: string
      question?: string
      answer?: string
    } | string>
    columns?: string[]
    rows?: string[][]
  }>
}

interface Guide {
  id: string
  slug: string
  title: string
  guide_type: string
  category: string | null
  excerpt: string | null
  content: GuideContent
  featured_image_url: string | null
  seo_meta: { title?: string; description?: string } | null
  author: string | null
  published_at: string | null
}

async function getGuide(slug: string): Promise<Guide | null> {
  const { data, error } = await supabase
    .from('guides')
    .select('*')
    .eq('slug', slug)
    .eq('status', 'published')
    .single()

  if (error || !data) {
    return null
  }

  return data as Guide
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const guide = await getGuide(slug)

  if (!guide) {
    return {
      title: 'Guide Not Found | Snowthere',
    }
  }

  return {
    title: guide.seo_meta?.title || `${guide.title} | Snowthere`,
    description: guide.seo_meta?.description || guide.excerpt || `Read our guide: ${guide.title}`,
  }
}

// Render different section types
function GuideSection({ section }: { section: GuideContent['sections'][0] }) {
  switch (section.type) {
    case 'intro':
    case 'text':
      return (
        <div className="prose prose-lg max-w-none">
          {section.title && (
            <h2 className="font-display text-2xl font-bold text-gray-900 mb-4">
              {section.title}
            </h2>
          )}
          <div
            className="text-gray-600 leading-relaxed"
            dangerouslySetInnerHTML={createSanitizedHTML(section.content || '')}
          />
        </div>
      )

    case 'list':
      return (
        <div>
          {section.title && (
            <h2 className="font-display text-2xl font-bold text-gray-900 mb-6">
              {section.title}
            </h2>
          )}
          <div className="space-y-4">
            {section.items?.map((item, index) => {
              if (typeof item === 'string') {
                return (
                  <div key={index} className="flex items-start gap-3">
                    <span className="text-coral-500 font-bold">{index + 1}.</span>
                    <span className="text-gray-700">{item}</span>
                  </div>
                )
              }
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl p-4 shadow-sm border border-gray-100"
                >
                  <div className="flex items-start gap-4">
                    <span className="flex-shrink-0 w-8 h-8 bg-coral-100 text-coral-600 rounded-full flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </span>
                    <div>
                      {item.resort_slug ? (
                        <Link
                          href={`/resorts/${item.resort_slug}`}
                          className="font-semibold text-gray-900 hover:text-coral-500 transition-colors"
                        >
                          {item.name}
                        </Link>
                      ) : (
                        <span className="font-semibold text-gray-900">{item.name}</span>
                      )}
                      {item.description && (
                        <p className="text-gray-600 mt-1">{item.description}</p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )

    case 'checklist':
      return (
        <div>
          {section.title && (
            <h2 className="font-display text-2xl font-bold text-gray-900 mb-6">
              {section.title}
            </h2>
          )}
          <div className="bg-white rounded-2xl p-6 shadow-sm">
            <ul className="space-y-3">
              {section.items?.map((item, index) => (
                <li key={index} className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded border-2 border-gray-300 flex-shrink-0" />
                  <span className="text-gray-700">
                    {typeof item === 'string' ? item : item.name}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )

    case 'comparison_table':
      return (
        <div>
          {section.title && (
            <h2 className="font-display text-2xl font-bold text-gray-900 mb-6">
              {section.title}
            </h2>
          )}
          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-2xl shadow-sm overflow-hidden">
              <thead>
                <tr className="bg-gray-900 text-white">
                  {section.columns?.map((col, index) => (
                    <th key={index} className="px-4 py-3 text-left font-semibold">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {section.rows?.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className={rowIndex % 2 === 0 ? 'bg-gray-50' : 'bg-white'}
                  >
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex} className="px-4 py-3 text-gray-700">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )

    case 'faq':
      return (
        <div>
          {section.title && (
            <h2 className="font-display text-2xl font-bold text-gray-900 mb-6">
              {section.title}
            </h2>
          )}
          <div className="space-y-4">
            {section.items?.map((item, index) => {
              if (typeof item === 'string') return null
              return (
                <div
                  key={index}
                  className="bg-white rounded-xl p-5 shadow-sm border border-gray-100"
                >
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {item.question}
                  </h3>
                  <p className="text-gray-600">{item.answer}</p>
                </div>
              )
            })}
          </div>
        </div>
      )

    default:
      return null
  }
}

export default async function GuidePage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const guide = await getGuide(slug)

  if (!guide) {
    notFound()
  }

  const config = GUIDE_TYPE_CONFIG[guide.guide_type] || GUIDE_TYPE_CONFIG.comparison
  const Icon = config.icon

  const publishedDate = guide.published_at
    ? new Date(guide.published_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]">
        {/* Back link header */}
        <header className="bg-white/80 backdrop-blur-sm border-b border-gray-100">
        <div className="container mx-auto px-4 py-4">
          <Link
            href="/guides"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Guides</span>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12 md:py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            {/* Type badge */}
            <span className={`inline-flex items-center gap-2 text-sm font-medium text-${config.color}-600 bg-${config.color}-50 px-4 py-2 rounded-full mb-6`}>
              <Icon className="w-4 h-4" />
              {config.label}
            </span>

            {/* Title */}
            <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
              {guide.title}
            </h1>

            {/* Excerpt */}
            {guide.excerpt && (
              <p className="text-lg md:text-xl text-gray-600 mb-6">
                {guide.excerpt}
              </p>
            )}

            {/* Meta */}
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
          <div className="max-w-3xl mx-auto space-y-12">
            {guide.content?.sections?.map((section, index) => (
              <GuideSection key={index} section={section} />
            ))}
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
              Explore our resort guides for detailed information on family-friendly ski destinations.
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
      </div>
      <Footer />
    </>
  )
}
