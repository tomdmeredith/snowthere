'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'

// Sample resort data
const featuredResorts = [
  { name: 'St. Moritz', country: 'Switzerland', familyScore: 9.2, image: '/images/generated/chalet-interior.png' },
  { name: 'Courchevel', country: 'France', familyScore: 9.5, image: '/images/generated/apres-ski-lodge.png' },
  { name: 'Lech', country: 'Austria', familyScore: 9.1, image: '/images/generated/powder-sunrise.png' },
  { name: 'Aspen', country: 'USA', familyScore: 8.8, image: '/images/generated/family-sunset.png' },
]

export default function ObsidianLuxe() {
  const [activeResort, setActiveResort] = useState(0)

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-[#F5F0E8]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/30">
        <div className="max-w-[1800px] mx-auto px-8 lg:px-16">
          <div className="flex items-center justify-between h-20 border-b border-white/5">
            <Link href="/" className="text-xs tracking-[0.5em] uppercase font-light">
              Snowthere
            </Link>

            <div className="hidden md:flex items-center gap-12">
              <a href="#" className="text-xs tracking-[0.2em] uppercase text-white/50 hover:text-white transition-colors">
                Destinations
              </a>
              <a href="#" className="text-xs tracking-[0.2em] uppercase text-white/50 hover:text-white transition-colors">
                Curated
              </a>
              <a href="#" className="text-xs tracking-[0.2em] uppercase text-white/50 hover:text-white transition-colors">
                Planning
              </a>
              <a href="#" className="text-xs tracking-[0.2em] uppercase text-white/50 hover:text-white transition-colors">
                Journal
              </a>
            </div>

            <button className="px-6 py-2.5 text-xs tracking-[0.15em] uppercase border border-[#B4846C]/50 text-[#B4846C] hover:bg-[#B4846C] hover:text-black transition-all duration-500">
              Begin
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Full Screen Cinematic */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0">
          <Image
            src="/images/generated/family-sunset.png"
            alt="Family skiing at sunset"
            fill
            className="object-cover opacity-60"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black" />
          <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-transparent to-black/40" />
        </div>

        {/* Letterbox Bars */}
        <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-[#0A0A0A] to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0A0A0A] to-transparent" />

        {/* Content */}
        <div className="relative z-10 text-center max-w-4xl px-8">
          <div className="mb-8">
            <span className="text-xs tracking-[0.5em] uppercase text-[#B4846C]">
              The Art of Family Skiing
            </span>
          </div>

          <h1 className="font-[family-name:var(--font-cormorant)] text-6xl md:text-8xl lg:text-9xl font-light tracking-tight leading-[0.9] mb-8">
            Where Families<br />
            <span className="italic">Discover</span><br />
            Extraordinary
          </h1>

          <p className="text-lg md:text-xl text-white/60 max-w-xl mx-auto mb-12 leading-relaxed">
            A curated collection of the world&apos;s most exceptional ski destinations for discerning families.
          </p>

          <div className="flex items-center justify-center gap-8">
            <button className="group px-10 py-4 bg-[#B4846C] text-black text-xs tracking-[0.2em] uppercase font-medium hover:bg-[#D4A48C] transition-all duration-500">
              <span className="flex items-center gap-3">
                Explore Collection
                <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </span>
            </button>

            <button className="px-10 py-4 border border-white/20 text-xs tracking-[0.2em] uppercase hover:border-white/40 transition-all duration-500">
              Watch Film
            </button>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2 animate-bounce">
          <div className="w-px h-16 bg-gradient-to-b from-[#B4846C] to-transparent" />
        </div>
      </section>

      {/* Featured Destinations - Horizontal Scroll */}
      <section className="py-32 px-8 lg:px-16">
        <div className="max-w-[1800px] mx-auto">
          {/* Section Header */}
          <div className="flex items-end justify-between mb-16">
            <div>
              <span className="text-xs tracking-[0.3em] uppercase text-[#B4846C] block mb-4">
                Featured Destinations
              </span>
              <h2 className="font-[family-name:var(--font-cormorant)] text-5xl md:text-6xl font-light">
                Curated Excellence
              </h2>
            </div>
            <a href="#" className="hidden md:flex items-center gap-2 text-xs tracking-[0.2em] uppercase text-white/50 hover:text-white transition-colors">
              View All
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </a>
          </div>

          {/* Horizontal Scroll Cards */}
          <div className="flex gap-6 overflow-x-auto pb-8 -mx-8 px-8 snap-x snap-mandatory scrollbar-hide">
            {featuredResorts.map((resort, index) => (
              <div
                key={resort.name}
                className="group relative flex-shrink-0 w-[400px] snap-start cursor-pointer"
                onMouseEnter={() => setActiveResort(index)}
              >
                {/* Card */}
                <div className="relative aspect-[3/4] overflow-hidden rounded-sm">
                  <Image
                    src={resort.image}
                    alt={resort.name}
                    fill
                    className="object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent opacity-80" />

                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-[#B4846C]/0 group-hover:bg-[#B4846C]/10 transition-colors duration-500" />

                  {/* Content */}
                  <div className="absolute bottom-0 left-0 right-0 p-8">
                    <span className="text-xs tracking-[0.3em] uppercase text-white/50 block mb-2">
                      {resort.country}
                    </span>
                    <h3 className="font-[family-name:var(--font-cormorant)] text-3xl font-light mb-4">
                      {resort.name}
                    </h3>

                    {/* Family Score */}
                    <div className="flex items-center gap-3">
                      <span className="text-xs tracking-wide text-white/40">Family Score</span>
                      <span className="text-[#B4846C] font-light text-lg">{resort.familyScore}</span>
                    </div>
                  </div>

                  {/* Index Number */}
                  <div className="absolute top-6 right-6 font-[family-name:var(--font-cormorant)] text-6xl font-light text-white/10">
                    {String(index + 1).padStart(2, '0')}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Value Proposition */}
      <section className="py-32 px-8 lg:px-16 border-t border-white/5">
        <div className="max-w-[1800px] mx-auto">
          <div className="grid lg:grid-cols-2 gap-24 items-center">
            {/* Image */}
            <div className="relative aspect-[4/5] overflow-hidden rounded-sm">
              <Image
                src="/images/generated/mother-daughter.png"
                alt="Mother and daughter"
                fill
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-black/30 to-transparent" />
            </div>

            {/* Content */}
            <div className="lg:pl-12">
              <span className="text-xs tracking-[0.3em] uppercase text-[#B4846C] block mb-6">
                Our Philosophy
              </span>
              <h2 className="font-[family-name:var(--font-cormorant)] text-5xl md:text-6xl font-light mb-8 leading-[1.1]">
                Extraordinary<br />
                Experiences,<br />
                <span className="italic">Thoughtfully</span> Curated
              </h2>
              <p className="text-lg text-white/60 leading-relaxed mb-8 max-w-lg">
                We believe family skiing should be transformative, not transactional.
                Each destination in our collection has been personally vetted for
                exceptional family experiences.
              </p>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-8 pt-8 border-t border-white/10">
                <div>
                  <span className="font-[family-name:var(--font-cormorant)] text-4xl font-light text-[#B4846C]">47</span>
                  <p className="text-xs tracking-wide text-white/40 mt-2 uppercase">Countries</p>
                </div>
                <div>
                  <span className="font-[family-name:var(--font-cormorant)] text-4xl font-light text-[#B4846C]">3,000+</span>
                  <p className="text-xs tracking-wide text-white/40 mt-2 uppercase">Resorts</p>
                </div>
                <div>
                  <span className="font-[family-name:var(--font-cormorant)] text-4xl font-light text-[#B4846C]">∞</span>
                  <p className="text-xs tracking-wide text-white/40 mt-2 uppercase">Memories</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-32 px-8 lg:px-16 relative overflow-hidden">
        <div className="absolute inset-0">
          <Image
            src="/images/generated/family-skiing.png"
            alt="Family skiing"
            fill
            className="object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0A0A0A] via-[#0A0A0A]/90 to-[#0A0A0A]" />
        </div>

        <div className="relative z-10 max-w-[1800px] mx-auto text-center">
          <h2 className="font-[family-name:var(--font-cormorant)] text-5xl md:text-7xl font-light mb-8">
            Begin Your Journey
          </h2>
          <p className="text-xl text-white/50 max-w-2xl mx-auto mb-12">
            Join families who have discovered the art of exceptional ski vacations.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <input
              type="email"
              placeholder="Your email"
              className="w-full sm:w-80 px-6 py-4 bg-white/5 border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-[#B4846C]/50 transition-colors"
            />
            <button className="w-full sm:w-auto px-10 py-4 bg-[#B4846C] text-black text-xs tracking-[0.2em] uppercase font-medium hover:bg-[#D4A48C] transition-all duration-500">
              Request Access
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-8 lg:px-16 border-t border-white/5">
        <div className="max-w-[1800px] mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <span className="text-xs tracking-[0.5em] uppercase font-light">Snowthere</span>
            <div className="flex items-center gap-8">
              <a href="#" className="text-xs tracking-wide text-white/40 hover:text-white transition-colors">Privacy</a>
              <a href="#" className="text-xs tracking-wide text-white/40 hover:text-white transition-colors">Terms</a>
              <a href="#" className="text-xs tracking-wide text-white/40 hover:text-white transition-colors">Contact</a>
            </div>
            <span className="text-xs text-white/30">© 2026</span>
          </div>
        </div>
      </footer>

      {/* Fixed Design Label */}
      <div className="fixed bottom-6 left-6 z-50">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-2 bg-white/5 backdrop-blur-md border border-white/10 rounded-full hover:bg-white/10 transition-colors"
        >
          <span className="text-xs tracking-wide text-white/60">Design 1</span>
          <span className="w-px h-3 bg-white/20" />
          <span className="text-xs font-medium">Obsidian Luxe</span>
        </Link>
      </div>
    </div>
  )
}
