'use client'

import Link from 'next/link'
import Image from 'next/image'

const designs = [
  {
    id: 1,
    name: 'Obsidian Luxe',
    subtitle: 'Moncler / Tom Ford Inspired',
    description: 'Ultra-premium dark luxury. Cinematic. Exclusive.',
    colors: ['#0A0A0A', '#F5F0E8', '#B4846C'],
    image: '/images/generated/family-sunset.png',
  },
  {
    id: 2,
    name: 'Papier',
    subtitle: 'Condé Nast Traveler / NYT Travel',
    description: 'Editorial magazine layout. Story-first. Sophisticated.',
    colors: ['#FAF8F5', '#1A1A1A', '#C65D3E'],
    image: '/images/generated/mother-daughter.png',
  },
  {
    id: 3,
    name: 'Konstrukt',
    subtitle: 'Brutalist / Swiss Modernism',
    description: 'Raw typography. Data-forward. Unapologetic.',
    colors: ['#FFFFFF', '#000000', '#00D4FF'],
    image: '/images/generated/powder-sunrise.png',
  },
  {
    id: 4,
    name: 'Hygge',
    subtitle: 'Kinfolk / Cereal Magazine',
    description: 'Quiet luxury. Warm minimalism. Contemplative.',
    colors: ['#E8E4DF', '#3D3D3D', '#8B9A87'],
    image: '/images/generated/apres-ski-lodge.png',
  },
  {
    id: 5,
    name: 'Spielplatz',
    subtitle: 'Bauhaus / Memphis / Experimental',
    description: 'Playful. Unexpected. Joyful chaos.',
    colors: ['#FFE066', '#FF6B6B', '#4ECDC4'],
    image: '/images/generated/kids-ski-school.png',
  },
]

export default function DesignSelector() {
  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-black/50 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="text-lg font-light tracking-[0.3em] uppercase">
            Snowthere
          </Link>
          <span className="text-xs text-white/50 tracking-wide">Design Exploration</span>
        </div>
      </header>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-light tracking-tight mb-6">
            5 Visions
          </h1>
          <p className="text-xl text-white/60 max-w-2xl mx-auto leading-relaxed">
            Five radically different approaches to reimagining what a family ski directory can be.
            Each design starts from first principles.
          </p>
        </div>
      </section>

      {/* Design Grid */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <div className="grid gap-8">
          {designs.map((design, index) => (
            <Link
              key={design.id}
              href={`/design-${design.id}`}
              className="group relative overflow-hidden rounded-2xl border border-white/10 hover:border-white/30 transition-all duration-500"
            >
              <div className="grid md:grid-cols-2 min-h-[400px]">
                {/* Image Side */}
                <div className={`relative overflow-hidden ${index % 2 === 1 ? 'md:order-2' : ''}`}>
                  <Image
                    src={design.image}
                    alt={design.name}
                    fill
                    className="object-cover transition-transform duration-700 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-r from-black/50 to-transparent" />
                </div>

                {/* Content Side */}
                <div className="relative p-8 md:p-12 flex flex-col justify-center bg-[#0D0D0D]">
                  {/* Design Number */}
                  <span className="text-8xl font-light text-white/5 absolute top-4 right-8">
                    0{design.id}
                  </span>

                  {/* Content */}
                  <div className="relative z-10">
                    <span className="text-xs tracking-[0.3em] uppercase text-white/40 mb-4 block">
                      {design.subtitle}
                    </span>
                    <h2 className="text-4xl md:text-5xl font-light mb-4 tracking-tight">
                      {design.name}
                    </h2>
                    <p className="text-white/60 text-lg mb-8 max-w-md">
                      {design.description}
                    </p>

                    {/* Color Palette Preview */}
                    <div className="flex items-center gap-3 mb-8">
                      {design.colors.map((color, i) => (
                        <div
                          key={i}
                          className="w-8 h-8 rounded-full border border-white/20"
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>

                    {/* CTA */}
                    <div className="flex items-center gap-2 text-sm tracking-wide group-hover:gap-4 transition-all">
                      <span>View Design</span>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-white/40">
          <span>Snowthere Design Lab</span>
          <span>2026</span>
        </div>
      </footer>
    </div>
  )
}
