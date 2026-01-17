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

  // Transform the passes relation
  const transformedResort = {
    ...resort,
    family_metrics: resort.family_metrics,
    content: resort.content,
    costs: resort.costs,
    calendar: resort.calendar || [],
    passes: (resort.passes || []).map((p: any) => ({
      ...p.pass,
      access_type: p.access_type,
    })),
  }

  return transformedResort as ResortWithDetails
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const resort = await getResort(params.country, params.slug)
  if (!resort) return { title: 'Resort Not Found' }

  const seoMeta = resort.content?.seo_meta as { title?: string; description?: string } | null

  return {
    title: seoMeta?.title || `${resort.name} Family Ski Guide`,
    description:
      seoMeta?.description ||
      `Complete family guide to skiing at ${resort.name}. Kid-friendly terrain, costs, best times to visit, and honest parent reviews.`,
    openGraph: {
      title: `${resort.name} Family Ski Guide`,
      description: `Everything families need to know about skiing at ${resort.name}`,
    },
  }
}

export async function generateStaticParams() {
  const { data: resorts } = await supabase
    .from('resorts')
    .select('country, slug')
    .eq('status', 'published')

  return (resorts || []).map((resort) => ({
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

  const content = resort.content
  const metrics = resort.family_metrics
  const costs = resort.costs
  const faqs = content?.faqs as { question: string; answer: string }[] | null

  return (
    <main className="min-h-screen bg-cream-50">
      {/* Breadcrumb */}
      <nav className="bg-cream-100 py-4 border-b border-cream-200">
        <div className="container-page">
          <ol className="breadcrumb">
            <li>
              <Link href="/" className="hover:text-glow-600 transition-colors">
                Home
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <Link href="/resorts" className="hover:text-glow-600 transition-colors">
                Resorts
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li>
              <Link
                href={`/resorts/${params.country}`}
                className="hover:text-glow-600 transition-colors capitalize"
              >
                {decodeURIComponent(params.country).replace(/-/g, ' ')}
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li className="text-slate-900 font-medium">{resort.name}</li>
          </ol>
        </div>
      </nav>

      {/* Hero Header */}
      <header className="hero py-16 sm:py-20">
        <div className="container-page relative z-10">
          <div className="animate-in animate-in-1">
            <div className="flex items-center gap-2 text-forest-300 mb-3">
              <MapPin className="w-4 h-4" />
              <span className="text-sm font-medium">
                {resort.region}, {resort.country}
              </span>
            </div>

            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold text-cream-50 tracking-tight">
              {resort.name}
            </h1>

            {metrics && (
              <div className="mt-6 flex flex-wrap items-center gap-4">
                <div className="quick-take-score">
                  <Star className="w-5 h-5 text-glow-400" />
                  <span className="text-lg">
                    Family Score: <strong>{metrics.family_overall_score}/10</strong>
                  </span>
                </div>

                {metrics.best_age_min && metrics.best_age_max && (
                  <div className="flex items-center gap-2 text-forest-200">
                    <Users className="w-4 h-4" />
                    <span>
                      Best for ages {metrics.best_age_min}–{metrics.best_age_max}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Handwritten tagline */}
            <p className="mt-6 font-accent text-2xl text-glow-300 max-w-xl">
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
                  <div className="p-2 rounded-xl bg-glow-100">
                    <Plane className="w-5 h-5 text-glow-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-slate-900">
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
                  <div className="p-2 rounded-xl bg-forest-100">
                    <Home className="w-5 h-5 text-forest-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-slate-900">
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
                  <div className="p-2 rounded-xl bg-gold-100">
                    <Ticket className="w-5 h-5 text-gold-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-slate-900">
                    Lift Tickets & Passes
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.lift_tickets }}
                />
                {resort.passes.length > 0 && (
                  <div className="mt-8">
                    <h3 className="font-display font-semibold text-slate-900 mb-4">
                      Available Passes
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {resort.passes.map((pass) => (
                        <a
                          key={pass.id}
                          href={pass.purchase_url || pass.website_url || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="badge badge-pass hover:bg-slate-200 transition-colors"
                        >
                          {pass.name}
                          {pass.access_type && (
                            <span className="text-slate-500 ml-1">({pass.access_type})</span>
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
                  <div className="p-2 rounded-xl bg-forest-100">
                    <Mountain className="w-5 h-5 text-forest-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-slate-900">
                    On the Mountain
                  </h2>
                </div>
                <div
                  className="prose-family"
                  dangerouslySetInnerHTML={{ __html: content.on_mountain }}
                />
              </section>
            )}

            {/* Off the Mountain */}
            {content?.off_mountain && (
              <section id="off-mountain">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 rounded-xl bg-glow-100">
                    <Coffee className="w-5 h-5 text-glow-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-slate-900">
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
                  <div className="p-2 rounded-xl bg-gold-100">
                    <MessageSquare className="w-5 h-5 text-gold-600" />
                  </div>
                  <h2 className="font-display text-2xl font-semibold text-slate-900">
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
                <h3 className="font-display font-semibold text-slate-900 mb-4">
                  Jump to Section
                </h3>
                <nav className="space-y-2">
                  {content?.quick_take && (
                    <a
                      href="#quick-take"
                      className="flex items-center gap-2 text-sm text-slate-600 hover:text-glow-600 transition-colors py-1"
                    >
                      <Sparkles className="w-4 h-4" />
                      Quick Take
                    </a>
                  )}
                  {content?.getting_there && (
                    <a
                      href="#getting-there"
                      className="flex items-center gap-2 text-sm text-slate-600 hover:text-glow-600 transition-colors py-1"
                    >
                      <Plane className="w-4 h-4" />
                      Getting There
                    </a>
                  )}
                  {content?.where_to_stay && (
                    <a
                      href="#where-to-stay"
                      className="flex items-center gap-2 text-sm text-slate-600 hover:text-glow-600 transition-colors py-1"
                    >
                      <Home className="w-4 h-4" />
                      Where to Stay
                    </a>
                  )}
                  {content?.lift_tickets && (
                    <a
                      href="#lift-tickets"
                      className="flex items-center gap-2 text-sm text-slate-600 hover:text-glow-600 transition-colors py-1"
                    >
                      <Ticket className="w-4 h-4" />
                      Lift Tickets
                    </a>
                  )}
                  {content?.on_mountain && (
                    <a
                      href="#on-mountain"
                      className="flex items-center gap-2 text-sm text-slate-600 hover:text-glow-600 transition-colors py-1"
                    >
                      <Mountain className="w-4 h-4" />
                      On the Mountain
                    </a>
                  )}
                  {faqs && faqs.length > 0 && (
                    <a
                      href="#faq"
                      className="flex items-center gap-2 text-sm text-slate-600 hover:text-glow-600 transition-colors py-1"
                    >
                      <MessageSquare className="w-4 h-4" />
                      FAQ
                    </a>
                  )}
                </nav>
              </div>

              {/* Newsletter CTA */}
              <div className="card card-warm">
                <div className="text-center">
                  <span className="font-accent text-2xl text-glow-600">
                    Planning a trip?
                  </span>
                  <p className="mt-2 text-sm text-slate-600">
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
      <section className="bg-cream-100 py-16 border-t border-cream-200">
        <div className="container-page">
          <div className="text-center mb-10">
            <h2 className="font-display text-2xl font-semibold text-slate-900">
              Similar Resorts
            </h2>
            <p className="mt-2 text-slate-600">
              More family-friendly resorts in {resort.region}
            </p>
          </div>

          {/* Placeholder for similar resorts */}
          <div className="text-center py-12">
            <p className="text-slate-500 font-accent text-xl">
              Coming soon...
            </p>
          </div>
        </div>
      </section>
    </main>
  )
}
