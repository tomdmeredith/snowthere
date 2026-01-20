'use client'

import Image from 'next/image'
import Link from 'next/link'

// Sample data
const featuredStory = {
  title: 'The Complete Guide to Family Skiing in the Alps',
  subtitle: 'We visited 47 resorts across 12 countries to find the perfect destinations for your next family adventure',
  author: 'Sarah Mitchell',
  date: 'Winter 2026',
  readTime: '12 min read',
  image: '/images/generated/mother-daughter.png',
}

const editorsPicks = [
  {
    category: 'Best for Beginners',
    resort: 'Lech-Zürs',
    country: 'Austria',
    excerpt: 'Gentle slopes, impeccable ski schools, and that ineffable Austrian warmth.',
    image: '/images/generated/kids-ski-school.png',
  },
  {
    category: 'Best Value',
    resort: 'Bansko',
    country: 'Bulgaria',
    excerpt: 'World-class skiing at a fraction of the price. The secret is out.',
    image: '/images/generated/powder-sunrise.png',
  },
  {
    category: 'Best for Teens',
    resort: 'Verbier',
    country: 'Switzerland',
    excerpt: 'Challenging terrain meets après-ski cool. Teenagers approved.',
    image: '/images/generated/family-skiing.png',
  },
]

const sections = [
  { name: 'Featured', href: '#featured' },
  { name: 'Europe', href: '#europe' },
  { name: 'North America', href: '#americas' },
  { name: 'Budget Picks', href: '#budget' },
  { name: 'Luxury', href: '#luxury' },
  { name: 'Passes', href: '#passes' },
]

export default function Papier() {
  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#1A1A1A]">
      {/* Masthead */}
      <header className="border-b border-[#1A1A1A]/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          {/* Top Bar */}
          <div className="flex items-center justify-between py-4 border-b border-[#1A1A1A]/5">
            <span className="text-xs tracking-widest uppercase text-[#1A1A1A]/50">
              The Family Ski Guide
            </span>
            <span className="text-xs tracking-wide text-[#1A1A1A]/50">
              Winter 2026 · Issue No. 01
            </span>
          </div>

          {/* Logo */}
          <div className="py-8 text-center">
            <Link href="/" className="inline-block">
              <h1 className="font-[family-name:var(--font-playfair)] text-5xl md:text-6xl lg:text-7xl tracking-tight">
                Snowthere
              </h1>
            </Link>
            <p className="mt-2 text-sm tracking-[0.3em] uppercase text-[#1A1A1A]/60">
              Where Families Discover Their Next Adventure
            </p>
          </div>

          {/* Navigation */}
          <nav className="flex items-center justify-center gap-8 py-4 overflow-x-auto">
            {sections.map((section) => (
              <a
                key={section.name}
                href={section.href}
                className="text-xs tracking-[0.2em] uppercase text-[#1A1A1A]/60 hover:text-[#C65D3E] transition-colors whitespace-nowrap"
              >
                {section.name}
              </a>
            ))}
          </nav>
        </div>
      </header>

      {/* Featured Story - Magazine Layout */}
      <section className="max-w-7xl mx-auto px-6 lg:px-12 py-16">
        <div className="grid lg:grid-cols-12 gap-8 lg:gap-12">
          {/* Main Image */}
          <div className="lg:col-span-7">
            <div className="relative aspect-[4/5] overflow-hidden">
              <Image
                src={featuredStory.image}
                alt="Mother and daughter skiing"
                fill
                className="object-cover"
                priority
              />
              {/* Caption */}
              <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/60 to-transparent">
                <p className="text-xs text-white/80 italic">
                  A mother teaches her daughter the joy of skiing in the Austrian Alps
                </p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-5 flex flex-col justify-center">
            <span className="text-xs tracking-[0.3em] uppercase text-[#C65D3E] mb-4">
              Cover Story
            </span>

            {/* Drop Cap Title */}
            <h2 className="font-[family-name:var(--font-playfair)] text-4xl md:text-5xl leading-[1.1] mb-6">
              {featuredStory.title}
            </h2>

            <p className="font-[family-name:var(--font-source-serif)] text-xl text-[#1A1A1A]/80 leading-relaxed mb-8">
              {featuredStory.subtitle}
            </p>

            {/* Author Line */}
            <div className="flex items-center gap-4 mb-8">
              <div className="w-10 h-10 rounded-full bg-[#C65D3E]/20 flex items-center justify-center">
                <span className="text-sm font-medium text-[#C65D3E]">SM</span>
              </div>
              <div>
                <p className="text-sm font-medium">{featuredStory.author}</p>
                <p className="text-xs text-[#1A1A1A]/50">
                  {featuredStory.date} · {featuredStory.readTime}
                </p>
              </div>
            </div>

            <button className="self-start px-8 py-3 bg-[#1A1A1A] text-white text-xs tracking-[0.2em] uppercase hover:bg-[#C65D3E] transition-colors">
              Read the Full Story
            </button>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="border-t border-[#1A1A1A]/10" />
      </div>

      {/* Editor's Picks - Three Column Grid */}
      <section className="max-w-7xl mx-auto px-6 lg:px-12 py-16">
        <div className="flex items-baseline justify-between mb-12">
          <h2 className="font-[family-name:var(--font-playfair)] text-3xl">
            Editor&apos;s Picks
          </h2>
          <a href="#" className="text-xs tracking-[0.2em] uppercase text-[#C65D3E] hover:underline">
            View All Picks →
          </a>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {editorsPicks.map((pick, index) => (
            <article key={pick.resort} className="group cursor-pointer">
              {/* Image */}
              <div className="relative aspect-[3/4] overflow-hidden mb-6">
                <Image
                  src={pick.image}
                  alt={pick.resort}
                  fill
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                />
                {/* Number Badge */}
                <div className="absolute top-4 left-4 w-10 h-10 bg-white flex items-center justify-center">
                  <span className="font-[family-name:var(--font-playfair)] text-xl">
                    {index + 1}
                  </span>
                </div>
              </div>

              {/* Content */}
              <span className="text-xs tracking-[0.2em] uppercase text-[#C65D3E]">
                {pick.category}
              </span>
              <h3 className="font-[family-name:var(--font-playfair)] text-2xl mt-2 mb-1 group-hover:text-[#C65D3E] transition-colors">
                {pick.resort}
              </h3>
              <p className="text-sm text-[#1A1A1A]/50 mb-3">{pick.country}</p>
              <p className="font-[family-name:var(--font-source-serif)] text-[#1A1A1A]/70 leading-relaxed">
                {pick.excerpt}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* Pull Quote Section */}
      <section className="bg-[#1A1A1A] text-[#FAF8F5] py-24">
        <div className="max-w-4xl mx-auto px-6 lg:px-12 text-center">
          <blockquote>
            <p className="font-[family-name:var(--font-playfair)] text-3xl md:text-4xl lg:text-5xl leading-[1.3] italic mb-8">
              &quot;The best family ski vacations aren&apos;t about the runs you conquer—they&apos;re about the moments you share.&quot;
            </p>
            <cite className="not-italic">
              <span className="text-xs tracking-[0.3em] uppercase text-[#FAF8F5]/60">
                — The Snowthere Philosophy
              </span>
            </cite>
          </blockquote>
        </div>
      </section>

      {/* Two-Column Feature */}
      <section className="max-w-7xl mx-auto px-6 lg:px-12 py-24">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-24">
          {/* Left Column - The Guide */}
          <div>
            <span className="text-xs tracking-[0.3em] uppercase text-[#C65D3E] block mb-4">
              The Guide
            </span>
            <h2 className="font-[family-name:var(--font-playfair)] text-4xl mb-6">
              How to Plan the<br />Perfect Family Ski Trip
            </h2>
            <div className="font-[family-name:var(--font-source-serif)] text-lg text-[#1A1A1A]/70 space-y-4">
              <p className="first-letter:text-5xl first-letter:font-[family-name:var(--font-playfair)] first-letter:float-left first-letter:mr-3 first-letter:mt-1">
                Planning a ski vacation with children requires a different calculus than the trips of your youth. Gone are the days of first lifts and last runs. Instead, you&apos;re optimizing for magic carpet proximity and hot chocolate availability.
              </p>
              <p>
                But here&apos;s what we&apos;ve learned after a decade of family ski travel: the resorts that understand families aren&apos;t just tolerating your children—they&apos;re designing experiences specifically for them.
              </p>
            </div>
            <a href="#" className="inline-block mt-8 text-xs tracking-[0.2em] uppercase border-b-2 border-[#C65D3E] pb-1 hover:text-[#C65D3E] transition-colors">
              Continue Reading
            </a>
          </div>

          {/* Right Column - Image Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="relative aspect-square">
              <Image
                src="/images/generated/apres-ski-lodge.png"
                alt="Cozy lodge"
                fill
                className="object-cover"
              />
            </div>
            <div className="relative aspect-square mt-8">
              <Image
                src="/images/generated/chalet-interior.png"
                alt="Chalet interior"
                fill
                className="object-cover"
              />
            </div>
            <div className="relative aspect-square -mt-8">
              <Image
                src="/images/generated/family-sunset.png"
                alt="Family at sunset"
                fill
                className="object-cover"
              />
            </div>
            <div className="relative aspect-square">
              <Image
                src="/images/generated/kids-equipment.png"
                alt="Kids ski equipment"
                fill
                className="object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Newsletter - Editorial Style */}
      <section className="border-t border-b border-[#1A1A1A]/10 py-16">
        <div className="max-w-2xl mx-auto px-6 lg:px-12 text-center">
          <span className="text-xs tracking-[0.3em] uppercase text-[#C65D3E] block mb-4">
            From the Editor&apos;s Desk
          </span>
          <h2 className="font-[family-name:var(--font-playfair)] text-3xl mb-4">
            Join the Inner Circle
          </h2>
          <p className="font-[family-name:var(--font-source-serif)] text-[#1A1A1A]/70 mb-8">
            Receive curated recommendations, insider tips, and early access to our seasonal guides. Delivered thoughtfully, never too often.
          </p>
          <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
            <input
              type="email"
              placeholder="Your email address"
              className="flex-1 px-4 py-3 bg-white border border-[#1A1A1A]/10 text-sm focus:outline-none focus:border-[#C65D3E] transition-colors"
            />
            <button
              type="submit"
              className="px-8 py-3 bg-[#C65D3E] text-white text-xs tracking-[0.2em] uppercase hover:bg-[#1A1A1A] transition-colors"
            >
              Subscribe
            </button>
          </form>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 lg:px-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            <div className="md:col-span-2">
              <h3 className="font-[family-name:var(--font-playfair)] text-2xl mb-4">Snowthere</h3>
              <p className="font-[family-name:var(--font-source-serif)] text-sm text-[#1A1A1A]/60 max-w-xs">
                The definitive guide to family skiing. Researched with care, written with families in mind.
              </p>
            </div>
            <div>
              <h4 className="text-xs tracking-[0.2em] uppercase mb-4">Explore</h4>
              <ul className="space-y-2 text-sm text-[#1A1A1A]/60">
                <li><a href="#" className="hover:text-[#C65D3E]">All Resorts</a></li>
                <li><a href="#" className="hover:text-[#C65D3E]">By Region</a></li>
                <li><a href="#" className="hover:text-[#C65D3E]">Ski Passes</a></li>
                <li><a href="#" className="hover:text-[#C65D3E]">Planning Guides</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-xs tracking-[0.2em] uppercase mb-4">About</h4>
              <ul className="space-y-2 text-sm text-[#1A1A1A]/60">
                <li><a href="#" className="hover:text-[#C65D3E]">Our Story</a></li>
                <li><a href="#" className="hover:text-[#C65D3E]">Contact</a></li>
                <li><a href="#" className="hover:text-[#C65D3E]">Privacy</a></li>
                <li><a href="#" className="hover:text-[#C65D3E]">Terms</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-[#1A1A1A]/10 flex items-center justify-between text-xs text-[#1A1A1A]/40">
            <span>© 2026 Snowthere. All rights reserved.</span>
            <span className="italic">Made with love for families who ski.</span>
          </div>
        </div>
      </footer>

      {/* Fixed Design Label */}
      <div className="fixed bottom-6 left-6 z-50">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-2 bg-[#1A1A1A] text-white rounded-full hover:bg-[#C65D3E] transition-colors"
        >
          <span className="text-xs tracking-wide opacity-60">Design 2</span>
          <span className="w-px h-3 bg-white/20" />
          <span className="text-xs font-medium">Papier</span>
        </Link>
      </div>
    </div>
  )
}
