import { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { SITE_URL } from '@/lib/constants'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight } from 'lucide-react'
import { ResortCard } from '@/components/resort/ResortCard'
import { countryToSlug, type ResortListItem } from '@/lib/resort-filters'
import { sanitizeJSON } from '@/lib/sanitize'

// --- Collection Definitions ---

interface CollectionDef {
  title: string
  h1: string
  description: string
  intro: string
  faqs: { question: string; answer: string }[]
}

const COLLECTIONS: Record<string, CollectionDef> = {
  'best-for-toddlers': {
    title: 'Best Ski Resorts for Toddlers',
    h1: 'Best Ski Resorts for Toddlers',
    description:
      'Ski resorts rated highest for families with toddlers and kids under 3. Childcare, gentle slopes, and family-friendly lodging.',
    intro:
      "Looking for a ski resort where your toddler can play safely while you ski? These resorts scored highest for under-3s, with on-mountain childcare, gentle terrain, and activities that don't involve a chairlift. Real talk: skiing with a toddler is a different sport. These resorts actually get that.",
    faqs: [
      {
        question: 'What age can toddlers start skiing?',
        answer:
          'Most ski schools accept kids from age 3, though some resorts have snow play programs for kids as young as 18 months. For actual skiing lessons, 3-4 is the sweet spot.',
      },
      {
        question: 'Do ski resorts have daycare for toddlers?',
        answer:
          'Many family-focused resorts offer licensed childcare for kids from 2 months to 6 years. We flag resorts with on-mountain childcare in our guides.',
      },
    ],
  },
  'best-for-beginners': {
    title: 'Best Beginner Family Ski Resorts',
    h1: 'Best Beginner Family Ski Resorts',
    description:
      'Family ski resorts with the most beginner-friendly terrain. Gentle slopes, magic carpets, and excellent ski schools.',
    intro:
      "First time on skis as a family? These resorts have the highest percentage of beginner-friendly terrain — think gentle green runs, magic carpets, and ski schools that actually know how to teach kids (and nervous parents). The good news: you don't need a black diamond mountain to have an amazing family ski trip.",
    faqs: [
      {
        question: 'What is the best ski resort for a family that has never skied?',
        answer:
          'Look for resorts with at least 50% beginner terrain, dedicated learning areas separated from advanced skiers, and strong ski school programs. Our top picks all have magic carpets and progression terrain parks.',
      },
      {
        question: 'How many days does it take to learn to ski as a family?',
        answer:
          'Most adults can handle green runs after 2-3 days of lessons. Kids aged 4-7 often pick it up faster. Book at least a 3-day trip to get past the frustration phase.',
      },
    ],
  },
  'cheapest-family-resorts': {
    title: 'Cheapest Family Ski Resorts',
    h1: 'Most Affordable Family Ski Resorts',
    description:
      'Budget-friendly family ski resorts sorted by estimated daily family cost. Great skiing without breaking the bank.',
    intro:
      "Here's the thing about family skiing: it doesn't have to cost a fortune. These resorts offer the best value for families, sorted by estimated daily cost for a family of four. Pro tip: some European resorts are cheaper than Colorado once you factor in lodging and food — even with flights.",
    faqs: [
      {
        question: 'How much does a family ski vacation cost?',
        answer:
          'A family of four can spend anywhere from $200-$1,200+ per day depending on the resort. Budget resorts in Europe start around $200-350/day including lodging, while premium US resorts often exceed $800/day.',
      },
      {
        question: 'Are European ski resorts cheaper than American ones?',
        answer:
          "Often yes. Austrian and French resorts can be 40-60% cheaper than comparable US resorts for lodging and lift tickets. Even factoring in flights, a week in Austria can cost less than a week in Vail.",
      },
    ],
  },
  'epic-pass-resorts': {
    title: 'Epic Pass Family Ski Resorts',
    h1: 'Epic Pass Family Ski Resorts',
    description:
      'Family-friendly ski resorts included on the Epic Pass. Save on lift tickets and ski multiple resorts with one pass.',
    intro:
      "Got an Epic Pass? These family-friendly resorts are included in your pass, so you can skip the lift ticket window and head straight to the slopes. We've scored each one for families specifically — because a great resort for expert skiers isn't always great for kids.",
    faqs: [
      {
        question: 'Is the Epic Pass worth it for families?',
        answer:
          'If you ski 5+ days per season, the Epic Pass typically pays for itself. The Epic Day Pass option is great for families who ski less frequently — you pick your number of days upfront at a discount.',
      },
      {
        question: 'Which Epic Pass resorts are best for kids?',
        answer:
          'Our family scores consider childcare, beginner terrain, ski school quality, and overall family-friendliness. Browse our rankings below to find the best Epic Pass resorts for your family.',
      },
    ],
  },
  'ikon-pass-resorts': {
    title: 'Ikon Pass Family Ski Resorts',
    h1: 'Ikon Pass Family Ski Resorts',
    description:
      'Family-friendly ski resorts on the Ikon Pass. Family scores, best ages, and trip planning for Ikon destinations.',
    intro:
      "Ikon Pass holders, this one's for you. These are the most family-friendly resorts in the Ikon network, scored specifically for parents with kids. Whether you're doing a weekend trip or a full week, these resorts have the childcare, terrain, and vibe that makes skiing with kids actually fun.",
    faqs: [
      {
        question: 'Is the Ikon Pass good for families?',
        answer:
          'The Ikon Pass includes many excellent family resorts worldwide. The Ikon Base Pass is a budget-friendly option with some blackout dates. For families, the flexibility to try different resorts is a huge plus.',
      },
      {
        question: 'Which Ikon Pass resorts have the best childcare?',
        answer:
          'Several Ikon resorts offer excellent on-mountain childcare. Check our individual resort guides for childcare details, age ranges, and booking tips.',
      },
    ],
  },
  'with-childcare': {
    title: 'Ski Resorts with Childcare',
    h1: 'Ski Resorts with On-Mountain Childcare',
    description:
      'Ski resorts with licensed childcare and daycare facilities. Drop off the little ones and enjoy the slopes worry-free.',
    intro:
      "Real talk: sometimes the best family ski day is when the kids are happily playing in childcare while you actually get to ski. These resorts have confirmed on-mountain childcare or daycare facilities — because parallel turns are hard enough without a toddler on your back.",
    faqs: [
      {
        question: 'What age do ski resort daycares accept?',
        answer:
          'Most resort childcare programs accept children from 2 months to 6 years, though age ranges vary by resort. Some offer extended programs for kids up to 12 with a mix of ski lessons and indoor activities.',
      },
      {
        question: 'How much does ski resort childcare cost?',
        answer:
          'Resort childcare typically costs $100-200 per day per child in the US, and can be lower in European resorts. Many resorts offer multi-day discounts. Book early — spots fill up fast during peak weeks.',
      },
    ],
  },
}

const COLLECTION_SLUGS = Object.keys(COLLECTIONS)

// --- Data Fetching ---

type CollectionResort = ResortListItem & {
  family_metrics_full: {
    best_age_min: number | null
    best_age_max: number | null
    family_overall_score: number | null
    has_childcare: boolean | null
    kid_friendly_terrain_pct: number | null
  } | null
  passes: { ski_pass_id: string; ski_passes: { name: string } | null }[] | null
}

async function getCollectionResorts(collection: string): Promise<ResortListItem[]> {
  const { data, error } = await supabase
    .from('resorts')
    .select(`
      id,
      slug,
      name,
      country,
      region,
      family_metrics:resort_family_metrics(
        family_overall_score,
        best_age_min,
        best_age_max,
        has_childcare,
        kid_friendly_terrain_pct
      ),
      content:resort_content(
        tagline
      ),
      images:resort_images(
        image_url,
        image_type
      ),
      costs:resort_costs(
        estimated_family_daily,
        currency
      ),
      passes:resort_passes(
        ski_pass_id,
        ski_passes(name)
      )
    `)
    .eq('status', 'published')

  if (error || !data) return []

  const resorts = data as unknown as CollectionResort[]

  function sortByFamilyScore(list: CollectionResort[]): CollectionResort[] {
    return list.sort((a, b) => {
      const aScore = (a.family_metrics as CollectionResort['family_metrics_full'])?.family_overall_score ?? 0
      const bScore = (b.family_metrics as CollectionResort['family_metrics_full'])?.family_overall_score ?? 0
      return bScore - aScore
    })
  }

  let filtered: CollectionResort[]
  switch (collection) {
    case 'best-for-toddlers':
      filtered = sortByFamilyScore(resorts.filter((r) => {
        const m = r.family_metrics as CollectionResort['family_metrics_full']
        return m && m.best_age_min !== null && m.best_age_min <= 3
      }))
      break

    case 'best-for-beginners':
      filtered = resorts.filter((r) => {
        const m = r.family_metrics as CollectionResort['family_metrics_full']
        return m && m.kid_friendly_terrain_pct !== null && m.kid_friendly_terrain_pct >= 50
      })
      filtered.sort((a, b) => {
        const aPct = (a.family_metrics as CollectionResort['family_metrics_full'])?.kid_friendly_terrain_pct ?? 0
        const bPct = (b.family_metrics as CollectionResort['family_metrics_full'])?.kid_friendly_terrain_pct ?? 0
        return bPct - aPct
      })
      break

    case 'cheapest-family-resorts':
      filtered = resorts.filter((r) => r.costs?.estimated_family_daily != null)
      filtered.sort((a, b) => {
        const aPrice = a.costs?.estimated_family_daily ?? Infinity
        const bPrice = b.costs?.estimated_family_daily ?? Infinity
        return aPrice - bPrice
      })
      break

    case 'epic-pass-resorts':
      filtered = sortByFamilyScore(resorts.filter((r) =>
        r.passes?.some((p) => p.ski_passes?.name?.toLowerCase().includes('epic'))
      ))
      break

    case 'ikon-pass-resorts':
      filtered = sortByFamilyScore(resorts.filter((r) =>
        r.passes?.some((p) => p.ski_passes?.name?.toLowerCase().includes('ikon'))
      ))
      break

    case 'with-childcare':
      filtered = sortByFamilyScore(resorts.filter((r) => {
        const m = r.family_metrics as CollectionResort['family_metrics_full']
        return m?.has_childcare === true
      }))
      break

    default:
      return []
  }

  return filtered as unknown as ResortListItem[]
}

// --- Static Params ---

export function generateStaticParams() {
  return COLLECTION_SLUGS.map((collection) => ({ collection }))
}

// --- Metadata ---

interface PageProps {
  params: { collection: string }
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const def = COLLECTIONS[params.collection]
  if (!def) return { title: 'Collection Not Found' }

  const canonicalUrl = `${SITE_URL}/collections/${params.collection}`
  return {
    title: def.title,
    description: def.description,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      type: 'website',
      title: `${def.title} | Snowthere`,
      description: def.description,
      url: canonicalUrl,
      siteName: 'Snowthere',
      locale: 'en_US',
    },
  }
}

export const revalidate = 21600 // 6 hours

// --- Page ---

export default async function CollectionPage({ params }: PageProps) {
  const def = COLLECTIONS[params.collection]
  if (!def) notFound()

  const resorts = await getCollectionResorts(params.collection)

  const canonicalUrl = `${SITE_URL}/collections/${params.collection}`

  const breadcrumbJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL },
      { '@type': 'ListItem', position: 2, name: 'Resorts', item: `${SITE_URL}/resorts` },
      { '@type': 'ListItem', position: 3, name: def.title, item: canonicalUrl },
    ],
  }

  const itemListJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: def.title,
    description: def.description,
    numberOfItems: resorts.length,
    itemListElement: resorts.map((resort, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: resort.name,
      url: `${SITE_URL}/resorts/${countryToSlug(resort.country)}/${resort.slug}`,
    })),
  }

  const faqJsonLd = def.faqs.length > 0
    ? {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: def.faqs.map((faq) => ({
          '@type': 'Question',
          name: faq.question,
          acceptedAnswer: {
            '@type': 'Answer',
            text: faq.answer,
          },
        })),
      }
    : null

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: sanitizeJSON(breadcrumbJsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: sanitizeJSON(itemListJsonLd) }}
      />
      {faqJsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: sanitizeJSON(faqJsonLd) }}
        />
      )}

      <Navbar />
      <main id="main-content" className="min-h-screen bg-white">
        {/* Breadcrumb */}
        <nav className="bg-dark-50 py-4 border-b border-dark-100">
          <div className="container-page">
            <ol className="breadcrumb">
              <li>
                <Link href="/" className="hover:text-gold-600 transition-colors">
                  Home
                </Link>
              </li>
              <li className="breadcrumb-separator">
                <ChevronRight className="w-4 h-4" />
              </li>
              <li>
                <Link href="/resorts" className="hover:text-gold-600 transition-colors">
                  Resorts
                </Link>
              </li>
              <li className="breadcrumb-separator">
                <ChevronRight className="w-4 h-4" />
              </li>
              <li className="text-dark-900 font-medium">{def.title}</li>
            </ol>
          </div>
        </nav>

        {/* Hero */}
        <header className="relative py-20 sm:py-28 overflow-hidden">
          <div className="absolute inset-0 hero-gradient" />
          <div className="container-page relative z-10">
            <div className="animate-in animate-in-1 max-w-3xl">
              <h1 className="title-giant text-dark-800">{def.h1}</h1>
              <p className="mt-8 text-xl text-dark-600 leading-relaxed max-w-2xl">
                {def.intro}
              </p>
            </div>
          </div>
        </header>

        {/* Comparison Table (GEO-optimized) */}
        {resorts.length > 0 && (
          <section className="container-page py-12">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b-2 border-dark-200">
                    <th className="py-3 px-4 font-display font-bold text-dark-800">Resort</th>
                    <th className="py-3 px-4 font-display font-bold text-dark-800">Country</th>
                    <th className="py-3 px-4 font-display font-bold text-dark-800 text-center">Family Score</th>
                    <th className="py-3 px-4 font-display font-bold text-dark-800 text-right">Est. Daily Cost</th>
                    <th className="py-3 px-4 font-display font-bold text-dark-800 text-center">Best Ages</th>
                  </tr>
                </thead>
                <tbody>
                  {resorts.map((resort) => {
                    const score = resort.family_metrics?.family_overall_score
                    const cost = resort.costs?.estimated_family_daily
                    const ageMin = resort.family_metrics?.best_age_min
                    const ageMax = resort.family_metrics?.best_age_max
                    const cSlug = countryToSlug(resort.country)
                    return (
                      <tr key={resort.id} className="border-b border-dark-100 hover:bg-dark-50 transition-colors">
                        <td className="py-3 px-4">
                          <Link
                            href={`/resorts/${cSlug}/${resort.slug}`}
                            className="font-semibold text-coral-600 hover:text-coral-700 transition-colors"
                          >
                            {resort.name}
                          </Link>
                        </td>
                        <td className="py-3 px-4 text-dark-600">{resort.country}</td>
                        <td className="py-3 px-4 text-center">
                          {score != null ? (
                            <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-teal-50 text-teal-700 font-bold text-sm">
                              {score.toFixed(1)}
                            </span>
                          ) : (
                            <span className="text-dark-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right text-dark-700">
                          {cost != null ? (
                            <>${Math.round(cost)}<span className="text-dark-400 text-sm">/day</span></>
                          ) : (
                            <span className="text-dark-400">-</span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-center text-dark-600">
                          {ageMin != null && ageMax != null ? `${ageMin}-${ageMax}` : '-'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Resort Cards Grid */}
        <div className="container-page py-16 lg:py-20">
          {resorts.length > 0 ? (
            <>
              <h2 className="font-display text-2xl font-bold text-dark-800 mb-8">
                All {resorts.length} Resorts
              </h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {resorts.map((resort) => (
                  <ResortCard key={resort.id} resort={resort} />
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-20">
              <p className="text-xl text-dark-600">
                No resorts match this collection yet. We&apos;re adding new resorts every day!
              </p>
              <Link href="/resorts" className="mt-6 inline-block text-coral-600 hover:text-coral-700 font-semibold">
                Browse all resorts
              </Link>
            </div>
          )}
        </div>

        {/* FAQ Section */}
        {def.faqs.length > 0 && (
          <section className="bg-dark-50 py-16">
            <div className="container-page max-w-3xl">
              <h2 className="font-display text-2xl font-bold text-dark-800 mb-8">
                Frequently Asked Questions
              </h2>
              <div className="space-y-6">
                {def.faqs.map((faq) => (
                  <div key={faq.question}>
                    <h3 className="font-display text-lg font-bold text-dark-800 mb-2">
                      {faq.question}
                    </h3>
                    <p className="text-dark-600 leading-relaxed">{faq.answer}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
      <Footer />
    </>
  )
}
