import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import {
  Mountain,
  MapPin,
  Star,
  Users,
  Ticket,
  Sparkles,
  ArrowRight,
  CheckCircle,
  Globe,
  Heart,
  Send,
} from 'lucide-react'

async function getFeaturedResorts() {
  const { data: resorts } = await supabase
    .from('resorts')
    .select(`
      id,
      name,
      slug,
      country,
      region,
      family_metrics:resort_family_metrics(family_overall_score, best_age_min, best_age_max)
    `)
    .eq('status', 'published')
    .limit(6)

  return resorts || []
}

export default async function HomePage() {
  const featuredResorts = await getFeaturedResorts()

  return (
    <main className="min-h-screen bg-cream-50">
      {/* Hero Section */}
      <section className="hero relative overflow-hidden py-20 sm:py-28 lg:py-36">
        {/* Decorative elements */}
        <div className="absolute top-20 left-10 opacity-20">
          <Mountain className="w-32 h-32 text-forest-200" />
        </div>
        <div className="absolute bottom-20 right-10 opacity-20">
          <Sparkles className="w-24 h-24 text-glow-300" />
        </div>

        <div className="container-page relative z-10">
          <div className="mx-auto max-w-3xl text-center animate-in animate-in-1">
            {/* Handwritten intro */}
            <span className="font-accent text-2xl sm:text-3xl text-glow-300 block mb-4">
              Your ski-obsessed friend who&apos;s done the research
            </span>

            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-cream-50">
              Family Ski Adventures
              <span className="block mt-2 text-glow-400">Made Simple</span>
            </h1>

            <p className="mt-8 text-lg sm:text-xl leading-relaxed text-forest-200 max-w-2xl mx-auto">
              Real talk from parents who&apos;ve been there. Find the perfect ski resort
              for your family with honest guides, cost comparisons, and everything
              you need to plan an amazing trip.
            </p>

            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/resorts" className="btn btn-primary px-8 py-4 text-lg">
                Browse Resorts
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
              <Link
                href="/guides"
                className="btn btn-secondary px-8 py-4 text-lg"
              >
                Trip Planning Guides
              </Link>
            </div>

            {/* Trust badges */}
            <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-forest-300 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-glow-400" />
                <span>3000+ resorts worldwide</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-glow-400" />
                <span>Family-tested advice</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-glow-400" />
                <span>100% free guides</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Value Proposition - The Big Insight */}
      <section className="py-16 sm:py-24 bg-cream-100 border-y border-cream-200">
        <div className="container-page">
          <div className="mx-auto max-w-3xl text-center animate-in animate-in-2">
            <span className="font-accent text-2xl text-glow-600">
              Here&apos;s the thing...
            </span>
            <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold tracking-tight text-slate-900">
              International skiing is often <span className="highlight">cheaper</span> than US resorts
            </h2>
            <p className="mt-6 text-lg leading-relaxed text-slate-600">
              Fly to Austria, get lodging, and buy lift tickets for less than a weekend at Vail.
              But families feel overwhelmed: <em>&quot;How do we do this? Which ones?&quot;</em>
            </p>
            <p className="mt-4 text-lg font-medium text-forest-700">
              We answer that.
            </p>
          </div>

          {/* Value cards */}
          <div className="mx-auto mt-16 max-w-5xl">
            <div className="grid gap-6 sm:grid-cols-3">
              <div className="card text-center group hover:shadow-lifted transition-all duration-300">
                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-glow-100 group-hover:bg-glow-200 transition-colors">
                  <MapPin className="w-7 h-7 text-glow-600" />
                </div>
                <h3 className="font-display text-xl font-semibold text-slate-900">
                  Complete Trip Guides
                </h3>
                <p className="mt-3 text-slate-600 leading-relaxed">
                  Everything you need in one place. Print it, use it, enjoy your trip without endless googling.
                </p>
              </div>

              <div className="card text-center group hover:shadow-lifted transition-all duration-300">
                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-forest-100 group-hover:bg-forest-200 transition-colors">
                  <Ticket className="w-7 h-7 text-forest-600" />
                </div>
                <h3 className="font-display text-xl font-semibold text-slate-900">
                  Real Cost Comparisons
                </h3>
                <p className="mt-3 text-slate-600 leading-relaxed">
                  Side-by-side costs so you can find value skiing that fits your budget. No surprises.
                </p>
              </div>

              <div className="card text-center group hover:shadow-lifted transition-all duration-300">
                <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gold-100 group-hover:bg-gold-200 transition-colors">
                  <Users className="w-7 h-7 text-gold-600" />
                </div>
                <h3 className="font-display text-xl font-semibold text-slate-900">
                  Parent-Tested Advice
                </h3>
                <p className="mt-3 text-slate-600 leading-relaxed">
                  Honest recommendations based on real family experiences, not marketing fluff.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Resorts */}
      <section className="py-16 sm:py-24">
        <div className="container-page">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-10">
            <div>
              <span className="font-accent text-xl text-glow-600">
                Start exploring
              </span>
              <h2 className="mt-2 font-display text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
                Featured Family Resorts
              </h2>
            </div>
            <Link
              href="/resorts"
              className="text-sm font-semibold text-glow-600 hover:text-glow-700 flex items-center gap-1 group"
            >
              View all resorts
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {featuredResorts.length > 0 ? (
              featuredResorts.map((resort: any) => (
                <Link
                  key={resort.id}
                  href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
                  className="card group cursor-pointer hover:shadow-lifted transition-all duration-300"
                >
                  {/* Placeholder image */}
                  <div className="aspect-[16/10] rounded-2xl bg-gradient-to-br from-forest-100 to-forest-200 mb-5 overflow-hidden">
                    <div className="w-full h-full flex items-center justify-center">
                      <Mountain className="w-16 h-16 text-forest-300 group-hover:scale-110 transition-transform duration-300" />
                    </div>
                  </div>

                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-display text-lg font-semibold text-slate-900 group-hover:text-glow-600 transition-colors">
                        {resort.name}
                      </h3>
                      <p className="mt-1 text-sm text-slate-500 flex items-center gap-1">
                        <Globe className="w-3.5 h-3.5" />
                        {resort.region}, {resort.country}
                      </p>
                    </div>

                    {resort.family_metrics?.family_overall_score && (
                      <div className="flex items-center gap-1 bg-glow-100 text-glow-700 px-2.5 py-1 rounded-full text-sm font-medium">
                        <Star className="w-3.5 h-3.5" />
                        {resort.family_metrics.family_overall_score}/10
                      </div>
                    )}
                  </div>

                  {resort.family_metrics?.best_age_min && resort.family_metrics?.best_age_max && (
                    <p className="mt-3 text-sm text-slate-600">
                      Best for ages {resort.family_metrics.best_age_min}–{resort.family_metrics.best_age_max}
                    </p>
                  )}
                </Link>
              ))
            ) : (
              // Placeholder cards when no resorts
              ['Park City', 'St. Anton', 'Zermatt'].map((resort) => (
                <div key={resort} className="card group">
                  <div className="aspect-[16/10] rounded-2xl bg-gradient-to-br from-forest-100 to-forest-200 mb-5 overflow-hidden">
                    <div className="w-full h-full flex items-center justify-center">
                      <Mountain className="w-16 h-16 text-forest-300" />
                    </div>
                  </div>
                  <h3 className="font-display text-lg font-semibold text-slate-900">
                    {resort}
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Coming soon...
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* Why Families Trust Us */}
      <section className="py-16 sm:py-24 bg-forest-900 text-cream-50">
        <div className="container-page">
          <div className="text-center mb-12">
            <span className="font-accent text-2xl text-glow-400">
              Made for families like yours
            </span>
            <h2 className="mt-4 font-display text-3xl sm:text-4xl font-bold tracking-tight">
              Why Parents Trust Our Guides
            </h2>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4 max-w-5xl mx-auto">
            {[
              {
                icon: Heart,
                title: 'Kid-Focused',
                desc: 'Age-specific recommendations from toddlers to teens',
              },
              {
                icon: Ticket,
                title: 'Budget-Friendly',
                desc: 'Find value skiing that fits real family budgets',
              },
              {
                icon: CheckCircle,
                title: 'Honest Reviews',
                desc: 'Real parent experiences, not resort PR fluff',
              },
              {
                icon: Globe,
                title: 'Worldwide',
                desc: 'From Colorado to the Alps to Japan',
              },
            ].map((item) => (
              <div key={item.title} className="text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-forest-800">
                  <item.icon className="w-6 h-6 text-glow-400" />
                </div>
                <h3 className="font-display font-semibold text-lg">{item.title}</h3>
                <p className="mt-2 text-forest-300 text-sm leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="py-16 sm:py-24">
        <div className="container-page">
          <div className="card card-warm max-w-2xl mx-auto text-center">
            <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-glow-100">
              <Send className="w-8 h-8 text-glow-600" />
            </div>

            <span className="font-accent text-2xl text-glow-600">
              Planning a trip?
            </span>
            <h2 className="mt-2 font-display text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
              Get Our Family Ski Newsletter
            </h2>
            <p className="mt-4 text-slate-600 max-w-md mx-auto">
              Monthly tips, deals, and destination spotlights. No spam, just helpful stuff for ski families.
            </p>

            <form className="mt-8 flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 rounded-full border border-cream-300 bg-white px-5 py-3 text-slate-900 placeholder-slate-400 focus:border-glow-500 focus:outline-none focus:ring-2 focus:ring-glow-200 transition-all"
              />
              <button type="submit" className="btn btn-primary px-6 py-3 whitespace-nowrap">
                Subscribe
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </form>

            <p className="mt-4 text-xs text-slate-500">
              Join 5,000+ ski families. Unsubscribe anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-cream-200 bg-cream-100 py-12">
        <div className="container-page">
          <div className="flex flex-col items-center justify-between gap-8 sm:flex-row">
            <div className="text-center sm:text-left">
              <Link href="/" className="font-display text-xl font-bold text-forest-800">
                Snowthere
              </Link>
              <p className="mt-2 text-sm text-slate-500">
                Family ski guides made with <Heart className="w-3.5 h-3.5 inline text-glow-500" /> for ski families.
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-6">
              <Link href="/resorts" className="text-sm text-slate-600 hover:text-glow-600 transition-colors">
                Resorts
              </Link>
              <Link href="/guides" className="text-sm text-slate-600 hover:text-glow-600 transition-colors">
                Guides
              </Link>
              <Link href="/about" className="text-sm text-slate-600 hover:text-glow-600 transition-colors">
                About
              </Link>
              <Link href="/contact" className="text-sm text-slate-600 hover:text-glow-600 transition-colors">
                Contact
              </Link>
              <Link href="/privacy" className="text-sm text-slate-600 hover:text-glow-600 transition-colors">
                Privacy
              </Link>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-cream-200 text-center">
            <p className="text-xs text-slate-400">
              © {new Date().getFullYear()} Snowthere. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}
