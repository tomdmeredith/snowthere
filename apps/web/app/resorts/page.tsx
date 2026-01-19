import { Metadata } from 'next'
import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import {
  ChevronRight,
  Mountain,
  Star,
  Users,
  Globe,
  MapPin,
  Search,
  Filter,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Browse Family Ski Resorts | Snowthere',
  description:
    'Find the perfect family ski resort worldwide. Browse by country, family score, and more. Complete trip guides with honest parent reviews.',
}

interface ResortWithMetrics {
  id: string
  slug: string
  name: string
  country: string
  region: string
  family_metrics: {
    family_overall_score: number | null
    best_age_min: number | null
    best_age_max: number | null
  } | null
}

async function getResorts(): Promise<ResortWithMetrics[]> {
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
        best_age_max
      )
    `)
    .eq('status', 'published')
    .order('name')

  if (error) {
    console.error('Error fetching resorts:', error)
    return []
  }

  return data as ResortWithMetrics[]
}

function groupByCountry(resorts: ResortWithMetrics[]) {
  return resorts.reduce(
    (acc, resort) => {
      if (!acc[resort.country]) {
        acc[resort.country] = []
      }
      acc[resort.country].push(resort)
      return acc
    },
    {} as Record<string, ResortWithMetrics[]>
  )
}

export const revalidate = 3600 // Revalidate every hour

export default async function ResortsPage() {
  const resorts = await getResorts()
  const grouped = groupByCountry(resorts)
  const countries = Object.keys(grouped).sort()

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
            <li className="text-espresso-900 font-medium">Resorts</li>
          </ol>
        </div>
      </nav>

      {/* Hero Header */}
      <header className="hero py-16 sm:py-20">
        <div className="container-page relative z-10">
          <div className="animate-in animate-in-1 max-w-2xl">
            <span className="font-accent text-2xl text-cashmere-300 block mb-3">
              Find your perfect family resort
            </span>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-ivory-50 tracking-tight">
              Browse Family Ski Resorts
            </h1>
            <p className="mt-6 text-lg text-powder-200 leading-relaxed">
              {resorts.length > 0 ? (
                <>
                  <strong className="text-ivory-50">{resorts.length}</strong> family-friendly resorts worldwide with complete trip guides, cost breakdowns, and detailed family information.
                </>
              ) : (
                'Explore our growing collection of family-friendly ski resorts from around the world.'
              )}
            </p>
          </div>

          {/* Search/Filter placeholder */}
          <div className="mt-8 flex flex-col sm:flex-row gap-4 max-w-xl animate-in animate-in-2">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-espresso-400" />
              <input
                type="text"
                placeholder="Search resorts..."
                className="w-full pl-12 pr-4 py-3 rounded-full bg-white/10 border border-powder-600 text-ivory-50 placeholder-powder-300 focus:outline-none focus:ring-2 focus:ring-cashmere-400 focus:border-transparent transition-all"
              />
            </div>
            <button className="btn btn-secondary px-6 py-3 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </button>
          </div>
        </div>
      </header>

      {/* Resort Listings */}
      <div className="container-page py-12 lg:py-16">
        {countries.length === 0 ? (
          <div className="text-center py-16">
            <div className="mx-auto w-16 h-16 rounded-2xl bg-ivory-100 flex items-center justify-center mb-6">
              <Mountain className="w-8 h-8 text-espresso-400" />
            </div>
            <h2 className="font-display text-xl font-semibold text-espresso-900 mb-2">
              No resorts published yet
            </h2>
            <p className="text-espresso-600">
              We&apos;re working on adding family ski resort guides. Check back soon!
            </p>
          </div>
        ) : (
          <div className="space-y-16">
            {countries.map((country) => (
              <section key={country} className="animate-in animate-in-3">
                {/* Country header */}
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-xl bg-powder-100">
                    <Globe className="w-6 h-6 text-powder-600" />
                  </div>
                  <div>
                    <h2 className="font-display text-2xl font-bold text-espresso-900">
                      {country}
                    </h2>
                    <p className="text-sm text-espresso-500">
                      {grouped[country].length} {grouped[country].length === 1 ? 'resort' : 'resorts'}
                    </p>
                  </div>
                </div>

                {/* Resort grid */}
                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                  {grouped[country].map((resort) => (
                    <Link
                      key={resort.id}
                      href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
                      className="card group hover:shadow-lifted transition-all duration-300"
                    >
                      {/* Placeholder image */}
                      <div className="aspect-[16/9] rounded-xl bg-gradient-to-br from-powder-100 to-powder-200 mb-4 overflow-hidden">
                        <div className="w-full h-full flex items-center justify-center">
                          <Mountain className="w-12 h-12 text-powder-300 group-hover:scale-110 transition-transform duration-300" />
                        </div>
                      </div>

                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="font-display text-lg font-semibold text-espresso-900 group-hover:text-cashmere-600 transition-colors">
                            {resort.name}
                          </h3>
                          <p className="mt-1 text-sm text-espresso-500 flex items-center gap-1">
                            <MapPin className="w-3.5 h-3.5" />
                            {resort.region}
                          </p>
                        </div>

                        {resort.family_metrics?.family_overall_score && (
                          <div className="flex items-center gap-1 bg-cashmere-100 text-cashmere-700 px-2.5 py-1 rounded-full text-sm font-semibold shrink-0">
                            <Star className="w-3.5 h-3.5" />
                            {resort.family_metrics.family_overall_score}/10
                          </div>
                        )}
                      </div>

                      {resort.family_metrics?.best_age_min && resort.family_metrics?.best_age_max && (
                        <p className="mt-3 text-sm text-espresso-600 flex items-center gap-1">
                          <Users className="w-3.5 h-3.5 text-espresso-400" />
                          Best for ages {resort.family_metrics.best_age_min}–{resort.family_metrics.best_age_max}
                        </p>
                      )}
                    </Link>
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>

      {/* Newsletter CTA */}
      <section className="bg-ivory-100 border-t border-ivory-200 py-16">
        <div className="container-page">
          <div className="card card-warm max-w-2xl mx-auto text-center">
            <span className="font-accent text-xl text-cashmere-600">
              Don&apos;t see your favorite resort?
            </span>
            <h2 className="mt-2 font-display text-xl font-semibold text-espresso-900">
              We&apos;re adding new resorts every week
            </h2>
            <p className="mt-3 text-espresso-600">
              Sign up to get notified when we add resorts you care about.
            </p>
            <Link href="/" className="btn btn-primary mt-6 inline-flex">
              Join the Newsletter
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-ivory-200 bg-ivory-100 py-12">
        <div className="container-page">
          <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
            <div className="text-center sm:text-left">
              <Link href="/" className="font-display text-xl font-bold text-espresso-800">
                Snowthere
              </Link>
              <p className="mt-2 text-sm text-espresso-500">
                Family ski guides made with love for ski families.
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-6">
              <Link href="/" className="text-sm text-espresso-600 hover:text-cashmere-600 transition-colors">
                Home
              </Link>
              <Link href="/resorts" className="text-sm text-espresso-600 hover:text-cashmere-600 transition-colors">
                Resorts
              </Link>
              <Link href="/about" className="text-sm text-espresso-600 hover:text-cashmere-600 transition-colors">
                About
              </Link>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-ivory-200 text-center">
            <p className="text-xs text-espresso-400">
              © {new Date().getFullYear()} Snowthere. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}
