import Link from 'next/link'
import { supabase } from '@/lib/supabase'
import { Button, Badge, ScoreBadge } from '@/components/ui'
import { AgeSelector } from '@/components/home/AgeSelector'
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
    <main className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-dark-100">
        <div className="container-page">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2">
              <span className="font-display text-2xl font-bold text-dark-800">
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

      {/* Hero Section - SPIELPLATZ Design-5 Playful Style */}
      <section className="relative overflow-hidden py-24 sm:py-32 lg:py-40">
        {/* Design-5: "Sunset on snow" warm gradient background */}
        <div className="absolute inset-0 hero-gradient" />

        {/* Decorative snowflakes - subtle, playful */}
        <div className="absolute top-16 left-[15%] opacity-[0.08]">
          <Snowflake className="w-24 h-24 text-teal-400 animate-float" style={{ animationDelay: '0s' }} />
        </div>
        <div className="absolute bottom-24 right-[10%] opacity-[0.08]">
          <Snowflake className="w-16 h-16 text-coral-400 animate-float" style={{ animationDelay: '2s' }} />
        </div>
        <div className="absolute top-1/2 left-[5%] opacity-[0.06]">
          <Snowflake className="w-12 h-12 text-gold-400 animate-float" style={{ animationDelay: '1s' }} />
        </div>

        <div className="container-page relative z-10">
          <div className="mx-auto max-w-3xl text-center">
            {/* Editorial accent - playful tones */}
            <div className="inline-flex items-center gap-3 mb-6 animate-in animate-in-1">
              <span className="h-px w-10 bg-coral-400" />
              <span className="font-accent text-xl text-teal-600">
                For ski families, by ski families
              </span>
              <span className="h-px w-10 bg-coral-400" />
            </div>

            {/* Design-5: Giant Fraunces display heading */}
            <h1 className="title-giant text-dark-800 animate-in animate-in-2">
              The Family Ski Guide
              <span className="block text-coral-500 mt-1">You&apos;ll Actually Use</span>
            </h1>

            <p className="mt-8 text-lg sm:text-xl leading-relaxed text-dark-600 max-w-2xl mx-auto animate-in animate-in-3">
              Complete trip guides with childcare details, real costs, and
              age-by-age terrain breakdowns. Because planning a ski trip with
              kids shouldn&apos;t require a PhD.
            </p>

            {/* Age Selector - Primary CTA */}
            <div className="mt-10 animate-in animate-in-4">
              <AgeSelector />
            </div>

            {/* Secondary CTA */}
            <div className="mt-6 flex items-center justify-center gap-4 animate-in animate-in-5">
              <Button variant="ghost" size="lg" asChild>
                <Link href="/resorts" className="inline-flex items-center gap-2">
                  Browse All Resorts
                </Link>
              </Button>
              <span className="text-dark-300">or</span>
              <Button variant="ghost" size="lg" asChild>
                <Link href="/guides">
                  Trip Planning Guides
                </Link>
              </Button>
            </div>

            {/* Trust indicators - playful tones */}
            <div className="mt-14 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-dark-600 animate-in animate-in-5">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-teal-500" />
                <span>3,000+ resorts</span>
              </div>
              <div className="flex items-center gap-2">
                <Heart className="w-4 h-4 text-coral-400" />
                <span>Family-focused guides</span>
              </div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-gold-500" />
                <span>100% free</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* The Value Story - Design-5 Editorial Style */}
      <section className="py-24 sm:py-32 bg-white border-y border-dark-100">
        <div className="container-page">
          <div className="mx-auto max-w-4xl">
            {/* Editorial opener */}
            <div className="text-center mb-16">
              <span className="font-accent text-2xl text-teal-500 block mb-4">
                The open secret
              </span>
              <h2 className="font-display text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-dark-800 leading-tight">
                A week in the Alps often costs less than
                <span className="relative inline-block mx-2">
                  <span className="relative z-10">a weekend at Vail</span>
                  <span className="absolute bottom-1 left-0 right-0 h-4 bg-coral-200/60 -z-10 rounded" />
                </span>
              </h2>
            </div>

            {/* Design-5: Side-by-side comparison cards with playful hover */}
            <div className="grid md:grid-cols-2 gap-8 mb-14">
              {/* Colorado card - gold accent */}
              <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-gold-50 to-gold-100/50 border-2 border-gold-200 p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-gold">
                <div className="flex items-center gap-4 mb-6">
                  <div className="p-3 rounded-2xl bg-gold-200">
                    <MapPin className="w-6 h-6 text-gold-700" />
                  </div>
                  <span className="font-display text-xl font-bold text-dark-800">
                    Colorado Weekend
                  </span>
                </div>
                <div className="space-y-3 text-dark-600">
                  <div className="flex justify-between items-center">
                    <span>Lift tickets (2 days)</span>
                    <span className="font-semibold text-dark-700">$1,000</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Lodging (2 nights)</span>
                    <span className="font-semibold text-dark-700">$800</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Meals</span>
                    <span className="font-semibold text-dark-700">$400</span>
                  </div>
                  <div className="flex justify-between items-center pt-4 mt-4 border-t-2 border-gold-300">
                    <span className="font-semibold text-dark-800">Family of 4 total</span>
                    <span className="font-bold text-xl text-dark-800">$2,200+</span>
                  </div>
                </div>
              </div>

              {/* Alps card - teal accent with "better value" feel */}
              <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-50 to-mint-100/50 border-2 border-teal-200 p-8 transition-all duration-300 hover:-translate-y-1 hover:shadow-teal">
                {/* "Better value" ribbon */}
                <div className="absolute top-4 right-4">
                  <Badge variant="perfect" size="sm">Better value</Badge>
                </div>
                <div className="flex items-center gap-4 mb-6">
                  <div className="p-3 rounded-2xl bg-teal-200">
                    <Globe className="w-6 h-6 text-teal-700" />
                  </div>
                  <span className="font-display text-xl font-bold text-dark-800">
                    Austrian Alps Week
                  </span>
                </div>
                <div className="space-y-3 text-dark-600">
                  <div className="flex justify-between items-center">
                    <span>Lift tickets (6 days)</span>
                    <span className="font-semibold text-teal-700">$450</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Lodging (6 nights)</span>
                    <span className="font-semibold text-teal-700">$900</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Meals</span>
                    <span className="font-semibold text-teal-700">$600</span>
                  </div>
                  <div className="flex justify-between items-center pt-4 mt-4 border-t-2 border-teal-300">
                    <span className="font-semibold text-dark-800">Family of 4 total</span>
                    <span className="font-bold text-xl text-teal-600">$1,950</span>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-center text-lg text-dark-600 max-w-2xl mx-auto leading-relaxed">
              The tricky part? Knowing which European resorts actually work for families.
              That&apos;s what we spent hundreds of hours researching.
            </p>
          </div>
        </div>
      </section>

      {/* What Makes Us Different - Design-5 Card Grid */}
      <section className="py-24 sm:py-32">
        <div className="container-page">
          <div className="text-center mb-16">
            <span className="font-accent text-2xl text-teal-500">
              What makes us different
            </span>
            <h2 className="mt-3 font-display text-4xl sm:text-5xl font-bold tracking-tight text-dark-800">
              Trip Guides That Feel Like a Friend&apos;s Advice
            </h2>
          </div>

          {/* Design-5: Cards with scale hover + shadow escalation */}
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto">
            <div className="card card-lift group p-8">
              <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gold-100 group-hover:bg-gold-200 group-hover:scale-110 transition-all duration-300">
                <Coffee className="w-7 h-7 text-gold-600" />
              </div>
              <h3 className="font-display text-xl font-semibold text-dark-800 mb-3">
                Print &amp; Go Ready
              </h3>
              <p className="text-dark-600 leading-relaxed">
                Everything in one place: ski school ages, lunch spots with high chairs,
                where to grab groceries. Print it and you&apos;re set.
              </p>
            </div>

            <div className="card card-lift group p-8">
              <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-dark-100 group-hover:bg-dark-200 group-hover:scale-110 transition-all duration-300">
                <Ticket className="w-7 h-7 text-dark-600" />
              </div>
              <h3 className="font-display text-xl font-semibold text-dark-800 mb-3">
                Honest Cost Breakdowns
              </h3>
              <p className="text-dark-600 leading-relaxed">
                Real lift ticket prices, lodging ranges by budget, and a family-of-four
                daily estimate. No surprises.
              </p>
            </div>

            <div className="card card-lift group p-8">
              <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-teal-100 group-hover:bg-teal-200 group-hover:scale-110 transition-all duration-300">
                <Users className="w-7 h-7 text-teal-600" />
              </div>
              <h3 className="font-display text-xl font-semibold text-dark-800 mb-3">
                Age-Specific Details
              </h3>
              <p className="text-dark-600 leading-relaxed">
                Ski school from age 3, childcare from 18 months, magic carpets,
                &quot;kids ski free&quot; policies. The details that matter.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Resorts - Design-5 Magazine Grid */}
      <section className="py-24 sm:py-32 bg-gradient-to-br from-mint-50/80 via-white to-coral-50/30">
        <div className="container-page">
          <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between gap-4 mb-14">
            <div>
              <span className="font-accent text-2xl text-teal-500">
                Start exploring
              </span>
              <h2 className="mt-2 font-display text-4xl sm:text-5xl font-bold tracking-tight text-dark-800">
                Featured Family Resorts
              </h2>
            </div>
            <Link
              href="/resorts"
              className="group flex items-center gap-2 font-semibold text-coral-500 hover:text-coral-600 transition-colors"
            >
              View all resorts
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {/* Design-5: Resort cards with scale + shadow escalation */}
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {featuredResorts.length > 0 ? (
              featuredResorts.map((resort: any) => (
                <Link
                  key={resort.id}
                  href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
                  className="group"
                >
                  <div className="resort-card">
                    {/* Image placeholder with scale on hover */}
                    <div className="resort-card-image aspect-[4/3] bg-gradient-to-br from-dark-100 via-dark-50 to-mint-50 relative">
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Mountain className="w-14 h-14 text-dark-200 transition-transform duration-500" />
                      </div>
                      {/* Country badge - pill shape */}
                      <div className="absolute top-4 left-4">
                        <Badge variant="highlight" size="sm">
                          {resort.country}
                        </Badge>
                      </div>
                    </div>

                    <div className="p-6">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="font-display text-xl font-semibold text-dark-800 group-hover:text-coral-500 transition-colors">
                            {resort.name}
                          </h3>
                          <p className="mt-1 text-dark-500">
                            {resort.region}
                          </p>
                        </div>

                        {resort.family_metrics?.family_overall_score && (
                          <ScoreBadge
                            score={resort.family_metrics.family_overall_score}
                            badgeSize="sm"
                            showMax={false}
                          />
                        )}
                      </div>

                      {resort.family_metrics?.best_age_min && resort.family_metrics?.best_age_max && (
                        <p className="mt-4 text-sm text-dark-500 flex items-center gap-2">
                          <Heart className="w-4 h-4 text-coral-400" />
                          Best for ages {resort.family_metrics.best_age_min}–{resort.family_metrics.best_age_max}
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              // Placeholder cards with Design-5 styling
              ['Park City, USA', 'St. Anton, Austria', 'Zermatt, Switzerland'].map((resort) => (
                <div key={resort} className="resort-card">
                  <div className="resort-card-image aspect-[4/3] bg-gradient-to-br from-dark-100 via-dark-50 to-mint-50 flex items-center justify-center">
                    <Mountain className="w-14 h-14 text-dark-200" />
                  </div>
                  <div className="p-6">
                    <h3 className="font-display text-xl font-semibold text-dark-800">
                      {resort.split(',')[0]}
                    </h3>
                    <p className="mt-1 text-dark-400">
                      Coming soon...
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* What Every Guide Includes - Design-5 Dark Section */}
      <section className="py-24 sm:py-32 bg-dark-800 text-white relative overflow-hidden">
        {/* Subtle texture */}
        <div className="absolute inset-0 opacity-5 texture-knit" />
        {/* Decorative gradient orbs */}
        <div className="absolute top-20 left-10 w-64 h-64 bg-coral-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl" />

        <div className="container-page relative z-10">
          <div className="text-center mb-16">
            <span className="font-accent text-2xl text-gold-300">
              Every guide includes
            </span>
            <h2 className="mt-3 font-display text-4xl sm:text-5xl font-bold tracking-tight">
              The Details That Matter
            </h2>
          </div>

          {/* Design-5: Larger icons with hover effects */}
          <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4 max-w-5xl mx-auto">
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
              <div key={item.title} className="text-center group">
                <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-dark-700/80 border border-dark-600 group-hover:bg-dark-700 group-hover:border-gold-400/50 group-hover:scale-110 transition-all duration-300">
                  <item.icon className="w-8 h-8 text-gold-300" />
                </div>
                <h3 className="font-display font-semibold text-xl text-white">{item.title}</h3>
                <p className="mt-3 text-dark-300 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter Signup - Design-5 Playful Card */}
      <section className="py-24 sm:py-32">
        <div className="container-page">
          <div className="max-w-2xl mx-auto text-center">
            {/* Design-5: Extra rounded corners (40px), playful gradient */}
            <div className="relative overflow-hidden p-10 sm:p-14" style={{ borderRadius: '40px', background: 'linear-gradient(145deg, rgba(149, 225, 211, 0.15) 0%, rgba(255, 107, 107, 0.08) 100%)', border: '2px solid rgba(149, 225, 211, 0.3)' }}>
              {/* Decorative elements */}
              <div className="absolute top-4 right-4 w-20 h-20 bg-coral-100 rounded-full opacity-50 blur-2xl" />
              <div className="absolute bottom-4 left-4 w-16 h-16 bg-teal-100 rounded-full opacity-50 blur-2xl" />

              <div className="relative z-10">
                <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-coral-100 shadow-coral">
                  <Send className="w-8 h-8 text-coral-500" />
                </div>

                <span className="font-accent text-2xl text-teal-600">
                  Planning ahead?
                </span>
                <h2 className="mt-2 font-display text-3xl sm:text-4xl font-bold tracking-tight text-dark-800">
                  Get the Family Ski Newsletter
                </h2>
                <p className="mt-5 text-lg text-dark-600 max-w-md mx-auto">
                  Monthly destination spotlights, deal alerts, and trip tips.
                  Designed for families, never spammy.
                </p>

                {/* Design-5: Pill-shaped input and button */}
                <form className="mt-10 flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                  <input
                    type="email"
                    placeholder="Your email"
                    className="flex-1 px-6 py-4 rounded-full border border-dark-200 bg-white focus:outline-none focus:ring-2 focus:ring-coral-400 focus:border-transparent transition-all text-dark-700 placeholder:text-dark-400"
                  />
                  <Button type="submit" size="lg" className="whitespace-nowrap">
                    Subscribe
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </form>

                <p className="mt-5 text-sm text-dark-500">
                  Join 5,000+ ski families. Unsubscribe anytime.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-dark-100 bg-dark-50 py-12">
        <div className="container-page">
          <div className="flex flex-col items-center justify-between gap-8 sm:flex-row">
            <div className="text-center sm:text-left">
              <Link href="/" className="font-display text-xl font-bold text-dark-800">
                Snowthere
              </Link>
              <p className="mt-2 text-sm text-dark-500">
                Family ski guides made with care.
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-6">
              <Link href="/resorts" className="text-sm text-dark-600 hover:text-coral-500 transition-colors">
                Resorts
              </Link>
              <Link href="/guides" className="text-sm text-dark-600 hover:text-coral-500 transition-colors">
                Guides
              </Link>
              <Link href="/about" className="text-sm text-dark-600 hover:text-coral-500 transition-colors">
                About
              </Link>
              <Link href="/contact" className="text-sm text-dark-600 hover:text-coral-500 transition-colors">
                Contact
              </Link>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-dark-100 text-center">
            <p className="text-xs text-dark-400">
              © {new Date().getFullYear()} Snowthere. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </main>
  )
}
