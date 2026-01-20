'use client'

import Image from 'next/image'
import Link from 'next/link'

const moments = [
  {
    title: 'The First Run',
    description: 'That magical moment when fresh powder greets the morning sun.',
    image: '/images/generated/powder-sunrise.png',
  },
  {
    title: 'Together',
    description: 'Side by side, discovering the mountain as a family.',
    image: '/images/generated/family-skiing.png',
  },
  {
    title: 'The Lodge',
    description: 'Where stories are shared and memories are made.',
    image: '/images/generated/apres-ski-lodge.png',
  },
]

const destinations = [
  { name: 'Lech', country: 'Austria', vibe: 'Timeless elegance' },
  { name: 'Megève', country: 'France', vibe: 'Alpine charm' },
  { name: 'Aspen', country: 'USA', vibe: 'Mountain sophistication' },
  { name: 'St. Moritz', country: 'Switzerland', vibe: 'Quiet luxury' },
]

export default function Hygge() {
  return (
    <div className="min-h-screen bg-[#E8E4DF] text-[#3D3D3D]">
      {/* Navigation - Barely There */}
      <nav className="absolute top-0 left-0 right-0 z-50">
        <div className="max-w-6xl mx-auto px-8 py-8 flex items-center justify-between">
          <Link href="/" className="text-sm tracking-[0.4em] uppercase opacity-60 hover:opacity-100 transition-opacity">
            Snowthere
          </Link>
          <div className="hidden md:flex items-center gap-12">
            <a href="#" className="text-sm tracking-[0.2em] opacity-40 hover:opacity-100 transition-opacity">
              Explore
            </a>
            <a href="#" className="text-sm tracking-[0.2em] opacity-40 hover:opacity-100 transition-opacity">
              Guides
            </a>
            <a href="#" className="text-sm tracking-[0.2em] opacity-40 hover:opacity-100 transition-opacity">
              About
            </a>
          </div>
          <button className="text-sm tracking-[0.2em] opacity-60 hover:opacity-100 transition-opacity">
            Begin
          </button>
        </div>
      </nav>

      {/* Hero - Contemplative */}
      <section className="min-h-screen flex flex-col items-center justify-center px-8 text-center">
        {/* Soft Image Background */}
        <div className="absolute inset-0 z-0">
          <Image
            src="/images/generated/chalet-interior.png"
            alt="Cozy chalet"
            fill
            className="object-cover opacity-20"
            priority
          />
        </div>

        <div className="relative z-10 max-w-2xl">
          <p className="text-sm tracking-[0.4em] uppercase opacity-40 mb-8">
            A quiet guide to family skiing
          </p>

          <h1 className="font-[family-name:var(--font-cormorant)] text-5xl md:text-7xl font-light leading-[1.2] mb-8">
            Find your place<br />
            in the mountains
          </h1>

          <p className="text-lg text-[#3D3D3D]/70 leading-relaxed max-w-md mx-auto mb-12">
            Thoughtfully curated destinations for families who seek meaningful moments together.
          </p>

          <button className="px-8 py-4 text-sm tracking-[0.3em] uppercase border border-[#3D3D3D]/30 hover:border-[#8B9A87] hover:text-[#8B9A87] transition-all">
            Begin exploring
          </button>
        </div>

        {/* Subtle Scroll Indicator */}
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2">
          <div className="w-px h-16 bg-gradient-to-b from-[#3D3D3D]/20 to-transparent" />
        </div>
      </section>

      {/* Moments - Generous Whitespace */}
      <section className="py-32 px-8">
        <div className="max-w-6xl mx-auto">
          <p className="text-sm tracking-[0.4em] uppercase opacity-40 text-center mb-4">
            The essence
          </p>
          <h2 className="font-[family-name:var(--font-cormorant)] text-4xl md:text-5xl font-light text-center mb-24">
            What we seek
          </h2>

          <div className="space-y-32">
            {moments.map((moment, index) => (
              <div
                key={moment.title}
                className={`grid md:grid-cols-2 gap-12 md:gap-24 items-center ${
                  index % 2 === 1 ? 'md:flex-row-reverse' : ''
                }`}
              >
                {/* Image */}
                <div className={`${index % 2 === 1 ? 'md:order-2' : ''}`}>
                  <div className="relative aspect-[4/5] overflow-hidden">
                    <Image
                      src={moment.image}
                      alt={moment.title}
                      fill
                      className="object-cover"
                    />
                  </div>
                </div>

                {/* Content */}
                <div className={`${index % 2 === 1 ? 'md:order-1 md:text-right' : ''}`}>
                  <span className="text-sm tracking-[0.3em] opacity-30 block mb-4">
                    0{index + 1}
                  </span>
                  <h3 className="font-[family-name:var(--font-cormorant)] text-3xl md:text-4xl font-light mb-4">
                    {moment.title}
                  </h3>
                  <p className="text-[#3D3D3D]/60 text-lg leading-relaxed">
                    {moment.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Destinations - Simple Grid */}
      <section className="py-32 px-8 bg-[#F5F3F0]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-24">
            <p className="text-sm tracking-[0.4em] uppercase opacity-40 mb-4">
              Discover
            </p>
            <h2 className="font-[family-name:var(--font-cormorant)] text-4xl md:text-5xl font-light">
              Destinations we love
            </h2>
          </div>

          <div className="grid md:grid-cols-2 gap-px bg-[#3D3D3D]/10">
            {destinations.map((dest) => (
              <div
                key={dest.name}
                className="group bg-[#F5F3F0] p-12 md:p-16 hover:bg-white transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-[family-name:var(--font-cormorant)] text-3xl font-light mb-2 group-hover:text-[#8B9A87] transition-colors">
                      {dest.name}
                    </h3>
                    <p className="text-sm tracking-[0.2em] opacity-40 uppercase">
                      {dest.country}
                    </p>
                  </div>
                  <span className="text-2xl opacity-0 group-hover:opacity-100 transition-opacity text-[#8B9A87]">
                    →
                  </span>
                </div>
                <p className="mt-8 text-[#3D3D3D]/60 italic">
                  {dest.vibe}
                </p>
              </div>
            ))}
          </div>

          <div className="text-center mt-16">
            <a href="#" className="text-sm tracking-[0.3em] uppercase opacity-40 hover:opacity-100 transition-opacity">
              View all destinations →
            </a>
          </div>
        </div>
      </section>

      {/* Philosophy - Centered */}
      <section className="py-32 px-8">
        <div className="max-w-2xl mx-auto text-center">
          <blockquote className="font-[family-name:var(--font-cormorant)] text-3xl md:text-4xl font-light leading-relaxed italic text-[#3D3D3D]/80 mb-8">
            &quot;The best family trips aren&apos;t measured in runs completed, but in quiet moments shared.&quot;
          </blockquote>
          <p className="text-sm tracking-[0.3em] opacity-40">
            — Our philosophy
          </p>
        </div>
      </section>

      {/* Featured Image - Full Bleed */}
      <section className="relative h-[70vh]">
        <Image
          src="/images/generated/mother-daughter.png"
          alt="Mother and daughter"
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-[#E8E4DF] via-transparent to-transparent" />
      </section>

      {/* Values */}
      <section className="py-32 px-8 -mt-32 relative z-10">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-16 text-center">
            <div>
              <span className="inline-block w-12 h-px bg-[#8B9A87] mb-8" />
              <h3 className="font-[family-name:var(--font-cormorant)] text-2xl font-light mb-4">
                Intentional
              </h3>
              <p className="text-sm text-[#3D3D3D]/60 leading-relaxed">
                Every destination chosen with purpose. Quality over quantity.
              </p>
            </div>
            <div>
              <span className="inline-block w-12 h-px bg-[#8B9A87] mb-8" />
              <h3 className="font-[family-name:var(--font-cormorant)] text-2xl font-light mb-4">
                Honest
              </h3>
              <p className="text-sm text-[#3D3D3D]/60 leading-relaxed">
                Real experiences from real families. No hidden agendas.
              </p>
            </div>
            <div>
              <span className="inline-block w-12 h-px bg-[#8B9A87] mb-8" />
              <h3 className="font-[family-name:var(--font-cormorant)] text-2xl font-light mb-4">
                Thoughtful
              </h3>
              <p className="text-sm text-[#3D3D3D]/60 leading-relaxed">
                Consider what matters most to your family&apos;s unique rhythm.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Newsletter - Gentle */}
      <section className="py-24 px-8 bg-[#F5F3F0]">
        <div className="max-w-lg mx-auto text-center">
          <h2 className="font-[family-name:var(--font-cormorant)] text-3xl font-light mb-4">
            Stay inspired
          </h2>
          <p className="text-[#3D3D3D]/60 mb-8">
            Gentle updates, thoughtfully composed.
          </p>
          <form className="flex flex-col sm:flex-row gap-4">
            <input
              type="email"
              placeholder="Your email"
              className="flex-1 px-6 py-4 bg-white border border-[#3D3D3D]/10 text-sm placeholder:text-[#3D3D3D]/30 focus:outline-none focus:border-[#8B9A87] transition-colors"
            />
            <button
              type="submit"
              className="px-8 py-4 bg-[#8B9A87] text-white text-sm tracking-[0.2em] uppercase hover:bg-[#3D3D3D] transition-colors"
            >
              Subscribe
            </button>
          </form>
        </div>
      </section>

      {/* Footer - Minimal */}
      <footer className="py-16 px-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <span className="text-sm tracking-[0.4em] uppercase opacity-40">
              Snowthere
            </span>
            <div className="flex items-center gap-8">
              <a href="#" className="text-xs tracking-[0.2em] opacity-40 hover:opacity-100 transition-opacity">
                Privacy
              </a>
              <a href="#" className="text-xs tracking-[0.2em] opacity-40 hover:opacity-100 transition-opacity">
                Terms
              </a>
              <a href="#" className="text-xs tracking-[0.2em] opacity-40 hover:opacity-100 transition-opacity">
                Contact
              </a>
            </div>
            <span className="text-xs opacity-30">
              © 2026
            </span>
          </div>
        </div>
      </footer>

      {/* Fixed Design Label */}
      <div className="fixed bottom-6 left-6 z-50">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-2 bg-white/80 backdrop-blur-md border border-[#3D3D3D]/10 rounded-full hover:border-[#8B9A87] transition-colors"
        >
          <span className="text-xs tracking-wide opacity-40">Design 4</span>
          <span className="w-px h-3 bg-[#3D3D3D]/10" />
          <span className="text-xs">Hygge</span>
        </Link>
      </div>
    </div>
  )
}
