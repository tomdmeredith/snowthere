'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useState } from 'react'

const stats = [
  { number: '3,000+', label: 'RESORTS' },
  { number: '47', label: 'COUNTRIES' },
  { number: '∞', label: 'MEMORIES' },
]

const resorts = [
  {
    id: '001',
    name: 'ZERMATT',
    country: 'CH',
    familyScore: 9.2,
    terrain: { beginner: 20, intermediate: 45, advanced: 35 },
    highlight: 'CAR-FREE VILLAGE',
  },
  {
    id: '002',
    name: 'PARK CITY',
    country: 'US',
    familyScore: 9.5,
    terrain: { beginner: 35, intermediate: 40, advanced: 25 },
    highlight: 'EPIC PASS',
  },
  {
    id: '003',
    name: 'ST. ANTON',
    country: 'AT',
    familyScore: 8.4,
    terrain: { beginner: 10, intermediate: 40, advanced: 50 },
    highlight: 'LEGENDARY APRÈS',
  },
  {
    id: '004',
    name: 'NISEKO',
    country: 'JP',
    familyScore: 9.0,
    terrain: { beginner: 30, intermediate: 50, advanced: 20 },
    highlight: 'POWDER PARADISE',
  },
]

export default function Konstrukt() {
  const [hoveredResort, setHoveredResort] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-white text-black font-[family-name:var(--font-space-grotesk)]">
      {/* Navigation - Raw, Functional */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b-4 border-black">
        <div className="flex items-stretch">
          <Link
            href="/"
            className="px-6 py-4 text-xs font-bold tracking-[0.5em] border-r-4 border-black hover:bg-black hover:text-white transition-colors"
          >
            SNOWTHERE
          </Link>
          <div className="flex-1 flex items-center px-6">
            <span className="text-xs tracking-[0.3em] opacity-50">FAMILY SKI DIRECTORY</span>
          </div>
          <button className="px-8 py-4 bg-[#00D4FF] text-black text-xs font-bold tracking-[0.2em] border-l-4 border-black hover:bg-black hover:text-[#00D4FF] transition-colors">
            SEARCH
          </button>
        </div>
      </nav>

      {/* Hero - Massive Typography */}
      <section className="min-h-screen pt-20 flex flex-col">
        <div className="flex-1 grid lg:grid-cols-2">
          {/* Left - Typography */}
          <div className="flex flex-col justify-center p-8 lg:p-16">
            <div className="mb-8">
              <h1 className="text-[12vw] lg:text-[8vw] font-bold leading-[0.85] tracking-tighter">
                FAMILY
                <br />
                SKI
                <br />
                GUIDE
              </h1>
            </div>

            <div className="w-full h-1 bg-black mb-8" />

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-4">
              {stats.map((stat) => (
                <div key={stat.label}>
                  <span className="text-3xl lg:text-5xl font-bold">{stat.number}</span>
                  <p className="text-xs tracking-[0.2em] mt-1 opacity-50">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right - Image + Geometric Overlay */}
          <div className="relative bg-black">
            <Image
              src="/images/generated/powder-sunrise.png"
              alt="Pristine powder"
              fill
              className="object-cover opacity-60"
              priority
            />
            {/* Geometric Overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-48 h-48 border-4 border-[#00D4FF] rotate-45" />
            </div>
            {/* Corner Text */}
            <div className="absolute bottom-8 right-8 text-white text-right">
              <p className="text-xs tracking-[0.3em] opacity-50">2026</p>
              <p className="text-xs tracking-[0.3em]">EDITION 01</p>
            </div>
          </div>
        </div>

        {/* Search Bar - Brutalist */}
        <div className="border-t-4 border-black">
          <div className="grid grid-cols-4 divide-x-4 divide-black">
            <div className="p-4 lg:p-6">
              <label className="text-xs tracking-[0.2em] opacity-50 block mb-2">AGE</label>
              <select className="w-full bg-transparent text-lg font-bold focus:outline-none cursor-pointer">
                <option>ALL AGES</option>
                <option>0-3</option>
                <option>4-7</option>
                <option>8-12</option>
                <option>13+</option>
              </select>
            </div>
            <div className="p-4 lg:p-6">
              <label className="text-xs tracking-[0.2em] opacity-50 block mb-2">BUDGET</label>
              <select className="w-full bg-transparent text-lg font-bold focus:outline-none cursor-pointer">
                <option>ANY</option>
                <option>$ BUDGET</option>
                <option>$$ MODERATE</option>
                <option>$$$ PREMIUM</option>
              </select>
            </div>
            <div className="p-4 lg:p-6">
              <label className="text-xs tracking-[0.2em] opacity-50 block mb-2">REGION</label>
              <select className="w-full bg-transparent text-lg font-bold focus:outline-none cursor-pointer">
                <option>WORLDWIDE</option>
                <option>EUROPE</option>
                <option>NORTH AMERICA</option>
                <option>ASIA</option>
              </select>
            </div>
            <button className="p-4 lg:p-6 bg-black text-white text-lg font-bold tracking-[0.2em] hover:bg-[#00D4FF] hover:text-black transition-colors">
              → FIND
            </button>
          </div>
        </div>
      </section>

      {/* Resort Data Grid */}
      <section className="border-t-4 border-black">
        {/* Section Header */}
        <div className="border-b-4 border-black p-4 lg:p-8 flex items-baseline justify-between">
          <h2 className="text-4xl lg:text-6xl font-bold tracking-tighter">TOP RATED</h2>
          <span className="text-xs tracking-[0.3em] opacity-50">FAMILY SCORE ≥ 8.0</span>
        </div>

        {/* Data Table */}
        <div className="divide-y-4 divide-black">
          {resorts.map((resort) => (
            <div
              key={resort.id}
              className={`grid grid-cols-12 transition-colors cursor-pointer ${
                hoveredResort === resort.id ? 'bg-[#00D4FF]' : ''
              }`}
              onMouseEnter={() => setHoveredResort(resort.id)}
              onMouseLeave={() => setHoveredResort(null)}
            >
              {/* ID */}
              <div className="col-span-1 p-4 lg:p-6 border-r-4 border-black flex items-center">
                <span className="text-xs font-mono opacity-50">{resort.id}</span>
              </div>

              {/* Name + Country */}
              <div className="col-span-3 p-4 lg:p-6 border-r-4 border-black">
                <h3 className="text-2xl lg:text-4xl font-bold tracking-tight">{resort.name}</h3>
                <p className="text-xs tracking-[0.3em] opacity-50 mt-1">{resort.country}</p>
              </div>

              {/* Family Score */}
              <div className="col-span-2 p-4 lg:p-6 border-r-4 border-black flex flex-col justify-center">
                <span className="text-xs tracking-[0.2em] opacity-50 block">FAMILY</span>
                <span className="text-3xl lg:text-5xl font-bold">{resort.familyScore}</span>
              </div>

              {/* Terrain Bar */}
              <div className="col-span-3 p-4 lg:p-6 border-r-4 border-black flex flex-col justify-center">
                <span className="text-xs tracking-[0.2em] opacity-50 block mb-2">TERRAIN</span>
                <div className="flex h-4">
                  <div
                    className="bg-green-400"
                    style={{ width: `${resort.terrain.beginner}%` }}
                  />
                  <div
                    className="bg-blue-500"
                    style={{ width: `${resort.terrain.intermediate}%` }}
                  />
                  <div
                    className="bg-black"
                    style={{ width: `${resort.terrain.advanced}%` }}
                  />
                </div>
                <div className="flex justify-between text-[10px] mt-1 opacity-50">
                  <span>B{resort.terrain.beginner}%</span>
                  <span>I{resort.terrain.intermediate}%</span>
                  <span>A{resort.terrain.advanced}%</span>
                </div>
              </div>

              {/* Highlight */}
              <div className="col-span-2 p-4 lg:p-6 border-r-4 border-black flex items-center">
                <span className="text-xs font-bold tracking-[0.1em]">{resort.highlight}</span>
              </div>

              {/* Arrow */}
              <div className="col-span-1 p-4 lg:p-6 flex items-center justify-center">
                <span className="text-2xl">→</span>
              </div>
            </div>
          ))}
        </div>

        {/* View All */}
        <div className="border-t-4 border-black">
          <button className="w-full p-6 text-center text-xs font-bold tracking-[0.3em] hover:bg-black hover:text-white transition-colors">
            VIEW ALL 3,000+ RESORTS →
          </button>
        </div>
      </section>

      {/* Feature Grid - Asymmetric */}
      <section className="border-t-4 border-black">
        <div className="grid lg:grid-cols-3">
          {/* Large Feature */}
          <div className="lg:col-span-2 relative aspect-square lg:aspect-auto border-b-4 lg:border-b-0 lg:border-r-4 border-black">
            <Image
              src="/images/generated/family-skiing.png"
              alt="Family skiing together"
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 p-8">
              <span className="inline-block px-4 py-2 bg-[#FF00FF] text-black text-xs font-bold tracking-[0.2em] mb-4">
                FEATURED
              </span>
              <h3 className="text-4xl lg:text-6xl font-bold text-white tracking-tight">
                THE COMPLETE<br />GUIDE
              </h3>
            </div>
          </div>

          {/* Stacked Features */}
          <div className="divide-y-4 divide-black">
            <div className="p-8 bg-[#FFFF00]">
              <span className="text-xs tracking-[0.3em] opacity-50 block mb-4">01</span>
              <h3 className="text-2xl font-bold tracking-tight mb-2">SKI PASSES</h3>
              <p className="text-sm opacity-70">Epic. Ikon. Everything in between.</p>
            </div>
            <div className="p-8">
              <span className="text-xs tracking-[0.3em] opacity-50 block mb-4">02</span>
              <h3 className="text-2xl font-bold tracking-tight mb-2">BUDGET PICKS</h3>
              <p className="text-sm opacity-70">Incredible skiing. Sensible prices.</p>
            </div>
            <div className="p-8 bg-[#00D4FF]">
              <span className="text-xs tracking-[0.3em] opacity-50 block mb-4">03</span>
              <h3 className="text-2xl font-bold tracking-tight mb-2">FIRST TIMERS</h3>
              <p className="text-sm opacity-70">Start here. We&apos;ve got you.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Manifesto Section */}
      <section className="border-t-4 border-black bg-black text-white">
        <div className="p-8 lg:p-16">
          <div className="max-w-4xl">
            <h2 className="text-6xl lg:text-[10vw] font-bold leading-[0.85] tracking-tighter mb-12">
              NO<br />
              FLUFF.<br />
              JUST<br />
              DATA.
            </h2>
            <p className="text-xl lg:text-2xl opacity-70 max-w-lg">
              We believe in radical transparency. Real costs. Honest ratings. Information that helps you decide, not marketing that tries to sell.
            </p>
          </div>
        </div>
      </section>

      {/* Newsletter - Functional Form */}
      <section className="border-t-4 border-black">
        <div className="grid lg:grid-cols-2">
          <div className="p-8 lg:p-16">
            <h2 className="text-4xl lg:text-6xl font-bold tracking-tighter mb-4">
              GET THE<br />BRIEF.
            </h2>
            <p className="text-lg opacity-70">
              Weekly resort intel. No fluff. Unsubscribe anytime.
            </p>
          </div>
          <div className="border-t-4 lg:border-t-0 lg:border-l-4 border-black p-8 lg:p-16 flex items-center">
            <form className="w-full flex">
              <input
                type="email"
                placeholder="EMAIL"
                className="flex-1 px-6 py-4 border-4 border-black text-lg font-bold placeholder:opacity-30 focus:outline-none focus:border-[#00D4FF]"
              />
              <button
                type="submit"
                className="px-8 py-4 bg-black text-white text-lg font-bold tracking-[0.2em] hover:bg-[#00D4FF] hover:text-black transition-colors"
              >
                →
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer - Minimal */}
      <footer className="border-t-4 border-black">
        <div className="grid grid-cols-2 lg:grid-cols-4 divide-x-4 divide-black">
          <div className="p-6">
            <span className="text-xs tracking-[0.3em] opacity-50">SNOWTHERE</span>
          </div>
          <div className="p-6">
            <span className="text-xs tracking-[0.3em] opacity-50">2026</span>
          </div>
          <div className="p-6">
            <a href="#" className="text-xs tracking-[0.2em] hover:text-[#00D4FF]">PRIVACY</a>
          </div>
          <div className="p-6">
            <a href="#" className="text-xs tracking-[0.2em] hover:text-[#00D4FF]">TERMS</a>
          </div>
        </div>
      </footer>

      {/* Fixed Design Label */}
      <div className="fixed bottom-6 left-6 z-50">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-2 bg-black text-white border-2 border-black hover:bg-[#00D4FF] hover:text-black transition-colors"
        >
          <span className="text-xs tracking-wide opacity-60">Design 3</span>
          <span className="w-px h-3 bg-white/20" />
          <span className="text-xs font-bold">KONSTRUKT</span>
        </Link>
      </div>
    </div>
  )
}
