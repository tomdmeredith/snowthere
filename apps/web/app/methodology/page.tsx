import { Metadata } from 'next'
import Link from 'next/link'
import { SITE_URL } from '@/lib/constants'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import {
  ChevronRight,
  Calculator,
  Baby,
  GraduationCap,
  Mountain,
  Ticket,
  MapPin,
  RefreshCw,
  Star,
  CheckCircle,
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Family Score Methodology | How We Rate Ski Resorts',
  description:
    'Learn how Snowthere calculates Family Scores for ski resorts. Our transparent, deterministic methodology considers childcare, ski school, terrain, value, and convenience.',
  alternates: {
    canonical: `${SITE_URL}/methodology`,
  },
  openGraph: {
    title: 'Family Score Methodology | Snowthere',
    description: 'How we calculate Family Scores for ski resorts - transparent and deterministic.',
    url: `${SITE_URL}/methodology`,
  },
}

interface FactorCardProps {
  icon: React.ReactNode
  title: string
  maxPoints: string
  children: React.ReactNode
  color: 'teal' | 'coral' | 'gold'
}

function FactorCard({ icon, title, maxPoints, children, color }: FactorCardProps) {
  const colorClasses = {
    teal: 'from-teal-100 to-mint-100 border-teal-200 shadow-teal',
    coral: 'from-coral-100 to-coral-50 border-coral-200 shadow-coral',
    gold: 'from-gold-100 to-gold-50 border-gold-200 shadow-gold',
  }

  const iconClasses = {
    teal: 'text-teal-600',
    coral: 'text-coral-600',
    gold: 'text-gold-600',
  }

  return (
    <div className={`rounded-3xl p-6 bg-gradient-to-br ${colorClasses[color]} border`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={iconClasses[color]}>{icon}</div>
          <h3 className="font-display text-xl font-bold text-dark-800">{title}</h3>
        </div>
        <span className="text-sm font-semibold text-dark-500 bg-white/60 px-3 py-1 rounded-full">
          {maxPoints}
        </span>
      </div>
      <div className="text-dark-600 space-y-2">{children}</div>
    </div>
  )
}

export default function MethodologyPage() {
  const lastUpdated = 'January 2026'

  return (
    <main className="min-h-screen bg-white">
      <Navbar />

      {/* Breadcrumb */}
      <nav className="bg-dark-50 py-4 border-b border-dark-100">
        <div className="container-page">
          <ol className="breadcrumb">
            <li>
              <Link href="/" className="hover:text-coral-500 transition-colors">
                Home
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li className="text-dark-800 font-medium">Methodology</li>
          </ol>
        </div>
      </nav>

      {/* Header */}
      <header className="py-16 bg-gradient-to-br from-coral-50 to-white">
        <div className="container-page">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-coral-50 shadow-coral">
              <Calculator className="w-6 h-6 text-coral-600" />
            </div>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-dark-800">
              How We Score Resorts
            </h1>
          </div>
          <p className="text-lg text-dark-500 mt-4 max-w-2xl">
            Our Family Score is a transparent, deterministic rating that helps families find the
            right ski resort for their needs. Here&apos;s exactly how we calculate it.
          </p>
          <p className="text-dark-400 mt-4">Last updated: {lastUpdated}</p>
        </div>
      </header>

      {/* Content */}
      <div className="container-page py-12">
        <div className="max-w-4xl mx-auto">
          {/* Overview */}
          <section className="mb-16">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-6">
              The Family Score at a Glance
            </h2>

            <div className="bg-gradient-to-br from-dark-700 to-dark-900 rounded-3xl p-8 text-white mb-8">
              <div className="flex flex-col sm:flex-row items-center gap-6">
                <div className="flex items-center justify-center w-24 h-24 rounded-full bg-gradient-to-br from-coral-500 to-coral-600 shadow-coral">
                  <Star className="w-10 h-10 text-white fill-white/30" />
                </div>
                <div>
                  <p className="text-2xl font-display font-bold mb-2">
                    Score Range: 5.0 - 10.0
                  </p>
                  <p className="text-white/80 leading-relaxed">
                    Every resort starts with a base score of 5.0. Points are added based on
                    family-friendly features. The maximum possible score is 10.0.
                  </p>
                </div>
              </div>
            </div>

            <div className="prose-family">
              <p className="text-dark-600 leading-relaxed">
                Unlike subjective ratings, our Family Score is <strong>deterministic</strong> — the
                same resort features will always produce the same score. This means you can trust
                that two resorts with similar scores have genuinely similar family-friendliness.
              </p>
            </div>
          </section>

          {/* Score Breakdown */}
          <section className="mb-16">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-6">
              What We Measure
            </h2>

            <p className="text-dark-600 mb-8">
              We evaluate five key areas that matter most to families with children:
            </p>

            <div className="grid gap-6">
              {/* Childcare */}
              <FactorCard
                icon={<Baby className="w-6 h-6" />}
                title="Childcare Quality"
                maxPoints="up to +1.5"
                color="teal"
              >
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-teal-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.8</strong> — Resort offers childcare services
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-teal-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.4</strong> — Childcare accepts children 6 months or younger
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-teal-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — Infant care available (3 months or younger)
                    </span>
                  </li>
                </ul>
              </FactorCard>

              {/* Ski School */}
              <FactorCard
                icon={<GraduationCap className="w-6 h-6" />}
                title="Ski School Quality"
                maxPoints="up to +1.0"
                color="coral"
              >
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-coral-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.2</strong> — Resort has a ski school
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-coral-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.5</strong> — Ski school accepts children from age 3
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-coral-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — Ski school accepts children from age 4
                    </span>
                  </li>
                </ul>
                <p className="text-sm text-dark-500 mt-2 italic">
                  Note: Age 3 and age 4 bonuses are mutually exclusive
                </p>
              </FactorCard>

              {/* Terrain */}
              <FactorCard
                icon={<Mountain className="w-6 h-6" />}
                title="Family-Friendly Terrain"
                maxPoints="up to +1.2"
                color="gold"
              >
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-gold-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — 30%+ of terrain is beginner/intermediate
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-gold-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — 40%+ of terrain is beginner/intermediate
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-gold-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — Has magic carpet lifts for beginners
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-gold-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — Has dedicated kids&apos; terrain park
                    </span>
                  </li>
                </ul>
              </FactorCard>

              {/* Value */}
              <FactorCard
                icon={<Ticket className="w-6 h-6" />}
                title="Value for Families"
                maxPoints="up to +0.8"
                color="teal"
              >
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-teal-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.4</strong> — Kids 5 and under ski free
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-teal-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.4</strong> — Kids 10 and under ski free (exceptional policy)
                    </span>
                  </li>
                </ul>
              </FactorCard>

              {/* Convenience */}
              <FactorCard
                icon={<MapPin className="w-6 h-6" />}
                title="Village Convenience"
                maxPoints="up to +0.5"
                color="coral"
              >
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-coral-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.3</strong> — Ski-in/ski-out lodging available
                    </span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-coral-500 mt-1 flex-shrink-0" />
                    <span>
                      <strong>+0.2</strong> — English-friendly resort
                    </span>
                  </li>
                </ul>
              </FactorCard>
            </div>
          </section>

          {/* Example Calculation */}
          <section className="mb-16">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-6">
              Example Calculation
            </h2>

            <div className="bg-dark-50 rounded-3xl p-6 sm:p-8">
              <p className="text-dark-600 mb-6">
                Here&apos;s how we might calculate a score for a family-friendly resort:
              </p>

              <div className="bg-white rounded-2xl p-6 border border-dark-100">
                <table className="w-full text-sm">
                  <tbody className="divide-y divide-dark-100">
                    <tr>
                      <td className="py-3 text-dark-600">Base score</td>
                      <td className="py-3 text-right font-mono font-semibold text-dark-800">5.0</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">Has childcare</td>
                      <td className="py-3 text-right font-mono font-semibold text-teal-600">+0.8</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">Childcare from 6 months</td>
                      <td className="py-3 text-right font-mono font-semibold text-teal-600">+0.4</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">Ski school from age 3</td>
                      <td className="py-3 text-right font-mono font-semibold text-coral-600">+0.7</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">35% beginner terrain</td>
                      <td className="py-3 text-right font-mono font-semibold text-gold-600">+0.3</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">Magic carpet</td>
                      <td className="py-3 text-right font-mono font-semibold text-gold-600">+0.3</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">Kids 5 & under free</td>
                      <td className="py-3 text-right font-mono font-semibold text-teal-600">+0.4</td>
                    </tr>
                    <tr>
                      <td className="py-3 text-dark-600">English friendly</td>
                      <td className="py-3 text-right font-mono font-semibold text-coral-600">+0.2</td>
                    </tr>
                    <tr className="bg-gradient-to-r from-coral-50 to-coral-50/50">
                      <td className="py-4 font-display font-bold text-dark-800">Total Score</td>
                      <td className="py-4 text-right font-mono font-bold text-coral-600 text-lg">8.1</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* Data Sources */}
          <section className="mb-16">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-6">
              Our Data Sources
            </h2>

            <div className="prose-family">
              <p className="text-dark-600 leading-relaxed mb-4">
                We gather information from multiple authoritative sources to ensure accuracy:
              </p>

              <ul className="space-y-3 text-dark-600">
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-coral-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Official resort websites</strong> — Primary source for childcare,
                    ski school, and policy information
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-coral-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Ski pass networks</strong> — Epic Pass, Ikon Pass, and regional pass
                    partner information
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-coral-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Tourism boards</strong> — Regional and national tourism authority data
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-coral-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Family travel reviews</strong> — Aggregated feedback from family
                    skiing communities
                  </span>
                </li>
              </ul>
            </div>
          </section>

          {/* Updates */}
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <RefreshCw className="w-5 h-5 text-teal-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">
                Keeping Scores Current
              </h2>
            </div>

            <div className="prose-family">
              <p className="text-dark-600 leading-relaxed mb-4">
                Resort amenities and policies change. We refresh our data regularly:
              </p>

              <ul className="space-y-3 text-dark-600">
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-teal-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Continuous monitoring</strong> — Our system automatically checks for
                    policy changes
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-teal-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Seasonal updates</strong> — Full refresh before each ski season
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="w-2 h-2 rounded-full bg-teal-400 mt-2 flex-shrink-0" />
                  <span>
                    <strong>Community feedback</strong> — We investigate and correct reported
                    inaccuracies
                  </span>
                </li>
              </ul>

              <p className="text-dark-600 leading-relaxed mt-6">
                Each resort page shows when it was last refreshed, so you always know how current
                the information is.
              </p>
            </div>
          </section>

          {/* Limitations */}
          <section className="mb-16">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-6">
              What the Score Doesn&apos;t Measure
            </h2>

            <div className="bg-gradient-to-br from-gold-50 to-gold-100/50 rounded-3xl p-6 sm:p-8 border border-gold-200">
              <p className="text-dark-600 mb-4">
                The Family Score is specifically about <strong>family amenities</strong>. It
                doesn&apos;t account for:
              </p>

              <ul className="space-y-2 text-dark-600">
                <li className="flex items-start gap-2">
                  <span className="text-gold-500">•</span>
                  <span>Snow conditions or reliability</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-gold-500">•</span>
                  <span>Overall resort size or terrain variety</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-gold-500">•</span>
                  <span>Affordability or cost</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-gold-500">•</span>
                  <span>Travel accessibility</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-gold-500">•</span>
                  <span>Nightlife or adult amenities</span>
                </li>
              </ul>

              <p className="text-dark-600 mt-4">
                That&apos;s why we include detailed guides on each resort page — the Family Score
                is a starting point, not the whole picture.
              </p>
            </div>
          </section>

          {/* CTA */}
          <section>
            <div className="bg-gradient-to-br from-dark-700 to-dark-900 rounded-3xl p-8 text-center">
              <h2 className="font-display text-2xl font-bold text-white mb-4">
                Find Your Family&apos;s Perfect Resort
              </h2>
              <p className="text-white/80 mb-6 max-w-md mx-auto">
                Take our quick quiz to get personalized resort recommendations based on your
                family&apos;s specific needs.
              </p>
              <Link
                href="/quiz"
                className="inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold text-dark-800 bg-gradient-to-r from-gold-300 to-gold-400 hover:from-gold-400 hover:to-gold-500 shadow-gold hover:shadow-gold-lg transition-all duration-300 hover:scale-105"
              >
                Take the Quiz
                <ChevronRight className="w-5 h-5" />
              </Link>
            </div>
          </section>
        </div>
      </div>

      <Footer />
    </main>
  )
}
