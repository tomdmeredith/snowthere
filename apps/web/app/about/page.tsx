import { Metadata } from 'next'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight, Mountain, Heart, Sparkles, Search, Users } from 'lucide-react'

export const metadata: Metadata = {
  title: 'About Snowthere | Family Ski Trip Guides',
  description: 'Learn about Snowthere - helping families plan unforgettable ski vacations with honest, detailed resort guides. Our mission is to make family ski trips accessible to everyone.',
}

export default function AboutPage() {
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
            <li className="text-dark-800 font-medium">About</li>
          </ol>
        </div>
      </nav>

      {/* Header */}
      <header className="py-16 bg-gradient-to-br from-coral-50 to-white">
        <div className="container-page">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-peach-100 shadow-coral">
              <Mountain className="w-6 h-6 text-coral-600" />
            </div>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-dark-800">
              About Snowthere
            </h1>
          </div>
          <p className="text-xl text-dark-600 mt-4 max-w-2xl">
            Helping families find their perfect ski adventure, anywhere in the world.
          </p>
        </div>
      </header>

      {/* Content */}
      <div className="container-page py-12">
        <div className="max-w-3xl mx-auto">

          {/* Mission */}
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <Heart className="w-5 h-5 text-coral-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Our Mission</h2>
            </div>
            <p className="text-lg text-dark-600 leading-relaxed mb-4">
              Family ski trips shouldn&apos;t be overwhelming. We believe every family deserves
              access to the kind of insider knowledge that makes the difference between a
              stressful vacation and an unforgettable adventure.
            </p>
            <p className="text-lg text-dark-600 leading-relaxed">
              Here&apos;s a secret most families don&apos;t know: a week skiing in the Austrian Alps
              often costs less than a weekend at a major US resort. Our job is to help you
              discover opportunities like this and give you everything you need to book with
              confidence.
            </p>
          </section>

          {/* What We Do */}
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <Search className="w-5 h-5 text-teal-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">What We Do</h2>
            </div>
            <p className="text-dark-600 mb-6">
              We create complete, print-ready trip guides for family ski resorts around the world.
              Each guide includes:
            </p>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="bg-dark-50 rounded-2xl p-5">
                <h3 className="font-semibold text-dark-800 mb-2">Real Cost Breakdowns</h3>
                <p className="text-dark-600 text-sm">
                  Lift tickets, lodging by budget tier, and estimated daily costs for a family of four.
                  No surprises.
                </p>
              </div>
              <div className="bg-dark-50 rounded-2xl p-5">
                <h3 className="font-semibold text-dark-800 mb-2">Age-Specific Details</h3>
                <p className="text-dark-600 text-sm">
                  Ski school ages, childcare minimums, kids-ski-free policies, and which terrain
                  works for your crew.
                </p>
              </div>
              <div className="bg-dark-50 rounded-2xl p-5">
                <h3 className="font-semibold text-dark-800 mb-2">Honest Verdicts</h3>
                <p className="text-dark-600 text-sm">
                  &quot;Perfect if&quot; and &quot;Skip if&quot; sections that tell you straight up whether a
                  resort fits your family.
                </p>
              </div>
              <div className="bg-dark-50 rounded-2xl p-5">
                <h3 className="font-semibold text-dark-800 mb-2">Practical Tips</h3>
                <p className="text-dark-600 text-sm">
                  Where to eat, where to grocery shop, how to get there, and the local knowledge
                  that makes everything easier.
                </p>
              </div>
            </div>
          </section>

          {/* How We Research */}
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <Sparkles className="w-5 h-5 text-coral-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">How We Research</h2>
            </div>
            <p className="text-dark-600 mb-4">
              We use AI-assisted research to gather and synthesize information from across the web,
              combined with human review to ensure accuracy and add the nuances that matter to
              real families.
            </p>
            <div className="bg-gradient-to-br from-teal-50 to-mint-50 rounded-2xl p-6 border border-teal-200">
              <h3 className="font-semibold text-dark-800 mb-3">Our Process</h3>
              <ol className="space-y-2 text-dark-600">
                <li><strong>1. Research</strong> - We gather information from resort websites, travel publications, and parent communities</li>
                <li><strong>2. Synthesize</strong> - AI helps us organize and structure the information consistently</li>
                <li><strong>3. Verify</strong> - We fact-check prices, ages, and policies against official sources</li>
                <li><strong>4. Review</strong> - Human editors ensure the voice feels authentic and the advice is practical</li>
              </ol>
            </div>
            <p className="text-dark-500 text-sm mt-4">
              We&apos;re transparent about our use of AI. Every guide includes a disclosure, and we
              continuously improve our process based on reader feedback.
            </p>
          </section>

          {/* Why Trust Us */}
          <section className="mb-16">
            <div className="flex items-center gap-3 mb-6">
              <Users className="w-5 h-5 text-teal-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Why Trust Snowthere</h2>
            </div>
            <ul className="space-y-4 text-dark-600">
              <li className="flex items-start gap-3">
                <span className="text-coral-500 font-bold">1.</span>
                <span><strong>We tell you when to skip it.</strong> Every resort has downsides. We&apos;ll tell you what they are so you can make the right choice for your family.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-coral-500 font-bold">2.</span>
                <span><strong>Real numbers, not marketing.</strong> We research actual prices and update them regularly. No &quot;contact for pricing&quot; nonsense.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-coral-500 font-bold">3.</span>
                <span><strong>Global perspective.</strong> We cover resorts worldwide because some of the best family skiing isn&apos;t where you&apos;d expect.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-coral-500 font-bold">4.</span>
                <span><strong>Parent-focused.</strong> We care about ski school ages, highchairs at lunch spots, and grocery store locations - the details that matter when you have kids.</span>
              </li>
            </ul>
          </section>

          {/* Contact CTA */}
          <section className="bg-gradient-to-br from-coral-50 to-peach-50 rounded-3xl p-8 text-center">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">
              Questions or Feedback?
            </h2>
            <p className="text-dark-600 mb-6">
              We&apos;d love to hear from you. Whether you have a question about a resort,
              want to suggest one we should cover, or just want to say hi.
            </p>
            <Link
              href="/contact"
              className="inline-flex items-center gap-2 px-6 py-3 bg-coral-500 text-white font-semibold rounded-xl hover:bg-coral-600 transition-colors"
            >
              Get in Touch
              <ChevronRight className="w-4 h-4" />
            </Link>
          </section>

        </div>
      </div>

      <Footer />
    </main>
  )
}
