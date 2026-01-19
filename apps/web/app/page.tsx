import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import { Button, Badge, ScoreBadge } from '@/components/ui'
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
  Coffee,
  Snowflake,
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
    <main className="min-h-screen bg-ivory-50">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-ivory-50/95 backdrop-blur-sm border-b border-ivory-200">
        <div className="container-page">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2">
              <span className="font-display text-2xl font-bold text-espresso-900">
                Snowthere
              </span>
            </Link>

            <div className="hidden sm:flex items-center gap-8">
              <Link href="/resorts" className="nav-link text-sm">
                Resorts
              </Link>
              <Link href="/guides" className="nav-link text-sm">
                Guides
              </Link>
              <Link href="/about" className="nav-link text-sm">
                About
              </Link>
            </div>

            <Button size="sm" asChild>
              <Link href="/resorts">Explore</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section - CHALET Editorial Magazine Style */}
      <section className="relative overflow-hidden py-20 sm:py-28 lg:py-36">
        {/* Soft gradient background - ivory with subtle warmth */}
        <div className="absolute inset-0 bg-gradient-to-b from-camel-100/30 via-ivory-50 to-ivory-100" />

        {/* Decorative snowflakes - subtle, muted */}
        <div className="absolute top-16 left-[15%] opacity-[0.06]">
          <Snowflake className="w-24 h-24 text-slate-400 animate-float" style={{ animationDelay: '0s' }} />
        </div>
        <div className="absolute bottom-24 right-[10%] opacity-[0.06]">
          <Snowflake className="w-16 h-16 text-camel-400 animate-float" style={{ animationDelay: '2s' }} />
        </div>
        <div className="absolute top-1/2 left-[5%] opacity-[0.04]">
          <Snowflake className="w-12 h-12 text-slate-300 animate-float" style={{ animationDelay: '1s' }} />
        </div>

        <div className="container-page relative z-10">
          <div className="mx-auto max-w-3xl text-center">
            {/* Editorial accent - Swiss precision with warm camel tones */}
            <div className="inline-flex items-center gap-3 mb-6 animate-in animate-in-1">
              <span className="h-px w-10 bg-crimson-400" />
              <span className="font-accent text-xl text-camel-600">
                For ski families, by ski families
              </span>
              <span className="h-px w-10 bg-crimson-400" />
            </div>

            {/* Fraunces display heading */}
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-espresso-800 leading-[1.1] animate-in animate-in-2">
              The Family Ski Guide
              <span className="block text-crimson-500 mt-2">You&apos;ll Actually Use</span>
            </h1>

            <p className="mt-8 text-lg sm:text-xl leading-relaxed text-espresso-600 max-w-2xl mx-auto animate-in animate-in-3">
              Complete trip guides with childcare details, real costs, and
              age-by-age terrain breakdowns. Because planning a ski trip with
              kids shouldn&apos;t require a PhD.
            </p>

            {/* CHALET Button components */}
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4 animate-in animate-in-4">
              <Button size="lg" asChild>
                <Link href="/resorts" className="inline-flex items-center gap-2">
                  Browse Resorts
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </Button>
              <Button variant="ghost" size="lg" asChild>
                <Link href="/guides">
                  Trip Planning Guides
                </Link>
              </Button>
            </div>

            {/* Trust indicators - camel warm tones */}
            <div className="mt-14 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-espresso-600 animate-in animate-in-5">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-camel-500" />
                <span>3,000+ resorts</span>
              </div>
              <div className="flex items-center gap-2">
                <Heart className="w-4 h-4 text-crimson-400" />
                <span>Family-focused guides</span>
              </div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-pine-500" />
                <span>100% free</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Value Story - Editorial Style */}
      <section className="py-20 sm:py-28 bg-white border-y border-ivory-200">
        <div className="container-page">
          <div className="mx-auto max-w-4xl">
            {/* Editorial opener */}
            <div className="text-center mb-16">
              <span className="font-accent text-2xl text-camel-500 block mb-4">
                The open secret
              </span>
              <h2 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight text-espresso-800 leading-tight">
                A week in the Alps often costs less than
                <span className="relative inline-block mx-2">
                  <span className="relative z-10">a weekend at Vail</span>
                  <span className="absolute bottom-1 left-0 right-0 h-3 bg-crimson-100 -z-10" />
                </span>
              </h2>
            </div>

            {/* Side-by-side comparison */}
            <div className="grid md:grid-cols-2 gap-6 mb-12">
              <div className="card bg-camel-50/50 border-camel-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-camel-100">
                    <MapPin className="w-5 h-5 text-camel-600" />
                  </div>
                  <span className="font-display font-semibold text-espresso-800">
                    Colorado Weekend
                  </span>
                </div>
                <div className="space-y-2 text-espresso-600">
                  <div className="flex justify-between">
                    <span>Lift tickets (2 days)</span>
                    <span className="font-medium">$1,000</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Lodging (2 nights)</span>
                    <span className="font-medium">$800</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Meals</span>
                    <span className="font-medium">$400</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-camel-200 font-semibold text-espresso-800">
                    <span>Family of 4 total</span>
                    <span>$2,200+</span>
                  </div>
                </div>
              </div>

              <div className="card bg-pine-50/50 border-pine-100">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-pine-100">
                    <Globe className="w-5 h-5 text-pine-600" />
                  </div>
                  <span className="font-display font-semibold text-espresso-800">
                    Austrian Alps Week
                  </span>
                </div>
                <div className="space-y-2 text-espresso-600">
                  <div className="flex justify-between">
                    <span>Lift tickets (6 days)</span>
                    <span className="font-medium">$450</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Lodging (6 nights)</span>
                    <span className="font-medium">$900</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Meals</span>
                    <span className="font-medium">$600</span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-pine-200 font-semibold text-pine-700">
                    <span>Family of 4 total</span>
                    <span>$1,950</span>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-center text-espresso-600 max-w-2xl mx-auto leading-relaxed">
              The tricky part? Knowing which European resorts actually work for families.
              That&apos;s what we spent hundreds of hours researching.
            </p>
          </div>
        </div>
      </section>

      {/* What Makes Us Different - Card Grid */}
      <section className="py-20 sm:py-28">
        <div className="container-page">
          <div className="text-center mb-14">
            <span className="font-accent text-xl text-camel-500">
              What makes us different
            </span>
            <h2 className="mt-2 font-display text-3xl sm:text-4xl font-semibold tracking-tight text-espresso-800">
              Trip Guides That Feel Like a Friend&apos;s Advice
            </h2>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto">
            <div className="card group hover:shadow-soft transition-all duration-300">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-camel-50 group-hover:bg-camel-100 transition-colors">
                <Coffee className="w-6 h-6 text-camel-600" />
              </div>
              <h3 className="font-display text-lg font-semibold text-espresso-800 mb-2">
                Print &amp; Go Ready
              </h3>
              <p className="text-espresso-600 leading-relaxed text-sm">
                Everything in one place: ski school ages, lunch spots with high chairs,
                where to grab groceries. Print it and you&apos;re set.
              </p>
            </div>

            <div className="card group hover:shadow-soft transition-all duration-300">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 group-hover:bg-slate-200 transition-colors">
                <Ticket className="w-6 h-6 text-slate-600" />
              </div>
              <h3 className="font-display text-lg font-semibold text-espresso-800 mb-2">
                Honest Cost Breakdowns
              </h3>
              <p className="text-espresso-600 leading-relaxed text-sm">
                Real lift ticket prices, lodging ranges by budget, and a family-of-four
                daily estimate. No surprises.
              </p>
            </div>

            <div className="card group hover:shadow-soft transition-all duration-300">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-pine-50 group-hover:bg-pine-100 transition-colors">
                <Users className="w-6 h-6 text-pine-600" />
              </div>
              <h3 className="font-display text-lg font-semibold text-espresso-800 mb-2">
                Age-Specific Details
              </h3>
              <p className="text-espresso-600 leading-relaxed text-sm">
                Ski school from age 3, childcare from 18 months, magic carpets,
                &quot;kids ski free&quot; policies. The details that matter.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Resorts - Magazine Grid */}
      <section className="py-20 sm:py-28 bg-ivory-100">
        <div className="container-page">
          <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4 mb-12">
            <div>
              <span className="font-accent text-xl text-camel-500">
                Start exploring
              </span>
              <h2 className="mt-2 font-display text-3xl sm:text-4xl font-semibold tracking-tight text-espresso-900">
                Featured Family Resorts
              </h2>
            </div>
            <Link
              href="/resorts"
              className="group flex items-center gap-2 text-sm font-medium text-crimson-500 hover:text-crimson-600"
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
                  className="group"
                >
                  <div className="card bg-white hover:shadow-lifted transition-all duration-300">
                    {/* Image placeholder */}
                    <div className="aspect-[4/3] rounded-xl bg-gradient-to-br from-slate-100 via-slate-50 to-camel-50 mb-5 overflow-hidden relative">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Mountain className="w-12 h-12 text-slate-200 group-hover:scale-110 transition-transform duration-500" />
                      </div>
                      {/* Country badge */}
                      <div className="absolute top-3 left-3">
                        <span className="badge badge-category bg-white/90 backdrop-blur-sm">
                          {resort.country}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h3 className="font-display text-lg font-semibold text-espresso-900 group-hover:text-crimson-500 transition-colors">
                          {resort.name}
                        </h3>
                        <p className="mt-1 text-sm text-espresso-500">
                          {resort.region}
                        </p>
                      </div>

                      {resort.family_metrics?.family_overall_score && (
                        <div className="flex items-center gap-1.5 bg-pine-50 text-pine-700 px-2.5 py-1.5 rounded-full text-sm font-semibold">
                          <Star className="w-3.5 h-3.5 fill-current" />
                          {resort.family_metrics.family_overall_score}
                        </div>
                      )}
                    </div>

                    {resort.family_metrics?.best_age_min && resort.family_metrics?.best_age_max && (
                      <p className="mt-3 text-sm text-espresso-500 flex items-center gap-1.5">
                        <Heart className="w-3.5 h-3.5 text-crimson-400" />
                        Best for ages {resort.family_metrics.best_age_min}–{resort.family_metrics.best_age_max}
                      </p>
                    )}
                  </div>
                </Link>
              ))
            ) : (
              // Placeholder cards
              ['Park City, USA', 'St. Anton, Austria', 'Zermatt, Switzerland'].map((resort) => (
                <div key={resort} className="card bg-white">
                  <div className="aspect-[4/3] rounded-xl bg-gradient-to-br from-slate-100 via-slate-50 to-camel-50 mb-5 overflow-hidden flex items-center justify-center">
                    <Mountain className="w-12 h-12 text-slate-200" />
                  </div>
                  <h3 className="font-display text-lg font-semibold text-espresso-900">
                    {resort.split(',')[0]}
                  </h3>
                  <p className="mt-1 text-sm text-espresso-400">
                    Coming soon...
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* What Every Guide Includes */}
      <section className="py-20 sm:py-28 bg-espresso-800 text-ivory-50 relative overflow-hidden">
        {/* Subtle texture */}
        <div className="absolute inset-0 opacity-5 texture-knit" />

        <div className="container-page relative z-10">
          <div className="text-center mb-14">
            <span className="font-accent text-2xl text-camel-300">
              Every guide includes
            </span>
            <h2 className="mt-3 font-display text-3xl sm:text-4xl font-semibold tracking-tight">
              The Details That Matter
            </h2>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4 max-w-5xl mx-auto">
            {[
              {
                icon: Heart,
                title: 'Age-by-Age',
                desc: 'Ski school minimums, childcare ages, teen terrain parks',
              },
              {
                icon: Ticket,
                title: 'Real Costs',
                desc: 'Lift tickets, lodging tiers, family daily totals',
              },
              {
                icon: CheckCircle,
                title: 'Perfect If / Skip If',
                desc: 'Quick verdict on who this resort is for',
              },
              {
                icon: MapPin,
                title: 'Getting There',
                desc: 'Nearest airports, transfers, car vs shuttle',
              },
            ].map((item) => (
              <div key={item.title} className="text-center">
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-espresso-700/50">
                  <item.icon className="w-7 h-7 text-camel-300" />
                </div>
                <h3 className="font-display font-semibold text-lg text-ivory-50">{item.title}</h3>
                <p className="mt-2 text-ivory-200/80 text-sm leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter Signup */}
      <section className="py-20 sm:py-28">
        <div className="container-page">
          <div className="max-w-2xl mx-auto text-center">
            <div className="card card-warm p-10 sm:p-12">
              <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-crimson-100">
                <Send className="w-7 h-7 text-crimson-500" />
              </div>

              <span className="font-accent text-2xl text-camel-500">
                Planning ahead?
              </span>
              <h2 className="mt-2 font-display text-2xl sm:text-3xl font-semibold tracking-tight text-espresso-900">
                Get the Family Ski Newsletter
              </h2>
              <p className="mt-4 text-espresso-600 max-w-md mx-auto">
                Monthly destination spotlights, deal alerts, and trip tips.
                Designed for families, never spammy.
              </p>

              <form className="mt-8 flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="Your email"
                  className="input flex-1"
                />
                <Button type="submit" className="whitespace-nowrap">
                  Subscribe
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </form>

              <p className="mt-4 text-xs text-espresso-400">
                Join 5,000+ ski families. Unsubscribe anytime.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-ivory-200 bg-ivory-100 py-12">
        <div className="container-page">
          <div className="flex flex-col items-center justify-between gap-8 sm:flex-row">
            <div className="text-center sm:text-left">
              <Link href="/" className="font-display text-xl font-bold text-espresso-800">
                Snowthere
              </Link>
              <p className="mt-2 text-sm text-espresso-500">
                Family ski guides made with care.
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-6">
              <Link href="/resorts" className="text-sm text-espresso-600 hover:text-crimson-500 transition-colors">
                Resorts
              </Link>
              <Link href="/guides" className="text-sm text-espresso-600 hover:text-crimson-500 transition-colors">
                Guides
              </Link>
              <Link href="/about" className="text-sm text-espresso-600 hover:text-crimson-500 transition-colors">
                About
              </Link>
              <Link href="/contact" className="text-sm text-espresso-600 hover:text-crimson-500 transition-colors">
                Contact
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
