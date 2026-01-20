'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useState, useEffect } from 'react'

const resorts = [
  { name: 'Zermatt', country: 'Switzerland', emoji: '🏔️', color: '#FF6B6B', funFact: 'No cars allowed!' },
  { name: 'Park City', country: 'USA', emoji: '⛷️', color: '#4ECDC4', funFact: 'Biggest in the US!' },
  { name: 'Niseko', country: 'Japan', emoji: '🍜', color: '#FFE066', funFact: 'Powder paradise!' },
  { name: 'Chamonix', country: 'France', emoji: '🥐', color: '#95E1D3', funFact: 'Mont Blanc views!' },
]

const shapes = ['○', '△', '□', '◇', '★', '◆']

export default function Spielplatz() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [activeCard, setActiveCard] = useState<number | null>(null)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF] text-[#2D3436] overflow-hidden">
      {/* Floating Geometric Shapes - Parallax Effect */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div
          className="absolute text-8xl text-[#FF6B6B]/20 transition-transform duration-1000"
          style={{
            top: '10%',
            left: '5%',
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)`,
          }}
        >
          ○
        </div>
        <div
          className="absolute text-9xl text-[#4ECDC4]/20 transition-transform duration-1000"
          style={{
            top: '60%',
            right: '10%',
            transform: `translate(${-mousePosition.x * 0.03}px, ${mousePosition.y * 0.03}px)`,
          }}
        >
          △
        </div>
        <div
          className="absolute text-7xl text-[#FFE066]/30 transition-transform duration-1000"
          style={{
            bottom: '20%',
            left: '15%',
            transform: `translate(${mousePosition.x * 0.01}px, ${-mousePosition.y * 0.01}px) rotate(45deg)`,
          }}
        >
          □
        </div>
        <div
          className="absolute text-6xl text-[#95E1D3]/20 transition-transform duration-1000"
          style={{
            top: '30%',
            right: '20%',
            transform: `translate(${-mousePosition.x * 0.025}px, ${-mousePosition.y * 0.025}px)`,
          }}
        >
          ◇
        </div>
      </div>

      {/* Navigation - Playful & Bouncy */}
      <nav className="relative z-50 p-4 md:p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link
            href="/"
            className="group flex items-center gap-2"
          >
            <span className="text-3xl group-hover:animate-bounce">❄️</span>
            <span className="font-bold text-xl tracking-tight">
              snow<span className="text-[#FF6B6B]">there</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {['Explore', 'Quiz', 'Deals', 'About'].map((item, i) => (
              <a
                key={item}
                href="#"
                className="relative px-4 py-2 font-semibold hover:text-[#FF6B6B] transition-colors group"
              >
                {item}
                <span
                  className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-lg opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  {shapes[i]}
                </span>
              </a>
            ))}
          </div>

          <button className="px-6 py-3 bg-[#FF6B6B] text-white font-bold rounded-full hover:scale-110 hover:rotate-2 transition-transform shadow-lg hover:shadow-xl">
            Let&apos;s Go! 🎿
          </button>
        </div>
      </nav>

      {/* Hero Section - Chaotic Fun */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-4">
        {/* Tilted Image Background */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative w-[80%] max-w-4xl aspect-video transform rotate-[-3deg] rounded-3xl overflow-hidden shadow-2xl">
            <Image
              src="/images/generated/hero-snowy-family.png"
              alt="Family skiing on snowy slopes"
              fill
              className="object-cover"
              priority
            />
            {/* Colorful Border */}
            <div className="absolute inset-0 border-8 border-[#FFE066] rounded-3xl" />
          </div>
        </div>

        {/* Floating Content Boxes */}
        <div className="relative z-10 text-center">
          {/* Main Title - Stacked & Offset */}
          <div className="relative mb-8">
            <h1 className="text-6xl md:text-8xl lg:text-9xl font-black leading-[0.9]">
              <span className="block transform -rotate-3 text-[#2D3436]">
                WHERE
              </span>
              <span className="block transform rotate-2 text-[#FF6B6B] relative left-4 md:left-8">
                SHOULD
              </span>
              <span className="block transform -rotate-1 text-[#4ECDC4] relative -left-2 md:-left-4">
                WE
              </span>
              <span className="block transform rotate-3 text-[#FFE066] text-stroke relative left-6 md:left-12">
                SKI?
              </span>
            </h1>
          </div>

          {/* Subtitle in a fun bubble */}
          <div className="inline-block bg-white px-8 py-4 rounded-full shadow-lg transform rotate-1 hover:rotate-0 transition-transform">
            <p className="text-lg md:text-xl font-medium">
              The <span className="text-[#FF6B6B]">fun</span> way to find your next family ski adventure ✨
            </p>
          </div>
        </div>

        {/* Floating Emojis */}
        <div className="absolute top-20 left-10 text-4xl animate-bounce delay-100">⛷️</div>
        <div className="absolute top-40 right-20 text-3xl animate-bounce delay-300">🎿</div>
        <div className="absolute bottom-40 left-20 text-5xl animate-bounce delay-500">🏔️</div>
        <div className="absolute bottom-20 right-10 text-4xl animate-bounce delay-700">❄️</div>
      </section>

      {/* Age Selector - Interactive Slider */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-[32px] p-8 md:p-12 shadow-xl transform hover:scale-[1.01] transition-transform">
            <h2 className="text-3xl md:text-4xl font-black text-center mb-8">
              How old are your kiddos? 👶👧👦
            </h2>

            {/* Age Bubbles */}
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              {[
                { age: '0-3', emoji: '👶', color: '#FFE066' },
                { age: '4-7', emoji: '🧒', color: '#4ECDC4' },
                { age: '8-12', emoji: '👧', color: '#FF6B6B' },
                { age: '13+', emoji: '🧑', color: '#95E1D3' },
              ].map((item) => (
                <button
                  key={item.age}
                  className="group px-8 py-4 rounded-full font-bold text-lg transition-all hover:scale-110 border-4"
                  style={{ borderColor: item.color, backgroundColor: `${item.color}20` }}
                >
                  <span className="text-2xl mr-2 group-hover:animate-bounce inline-block">{item.emoji}</span>
                  {item.age}
                </button>
              ))}
            </div>

            {/* Visual Slider Track */}
            <div className="relative h-4 my-2 bg-gradient-to-r from-[#FFE066] via-[#4ECDC4] to-[#FF6B6B] rounded-full">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-lg border-4 border-[#2D3436] cursor-grab hover:scale-125 transition-transform" />
            </div>

            <p className="text-center mt-6 text-gray-500">
              Drag to select ages • We&apos;ll find the perfect resorts! 🎯
            </p>
          </div>
        </div>
      </section>

      {/* Resort Cards - Trading Card Style */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-black mb-4">
              <span className="text-[#FF6B6B]">★</span> TOP PICKS <span className="text-[#4ECDC4]">★</span>
            </h2>
            <p className="text-xl text-gray-600">Collect them all! (Just kidding... or are we? 🤔)</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {resorts.map((resort, index) => (
              <div
                key={resort.name}
                className={`group relative cursor-pointer transition-all duration-300 ${
                  activeCard === index ? 'scale-110 z-10 rotate-0' : 'hover:scale-105'
                }`}
                style={{ transform: `rotate(${(index - 1.5) * 3}deg)` }}
                onMouseEnter={() => setActiveCard(index)}
                onMouseLeave={() => setActiveCard(null)}
              >
                {/* Card */}
                <div
                  className="relative bg-white rounded-3xl overflow-hidden shadow-xl border-4 transition-colors"
                  style={{ borderColor: resort.color }}
                >
                  {/* Card Number */}
                  <div
                    className="absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center text-white font-black text-lg z-10"
                    style={{ backgroundColor: resort.color }}
                  >
                    {String(index + 1).padStart(2, '0')}
                  </div>

                  {/* Image */}
                  <div className="relative aspect-[4/3] overflow-hidden">
                    <Image
                      src="/images/generated/family-skiing.png"
                      alt={resort.name}
                      fill
                      className="object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                    {/* Fun Fact Overlay */}
                    <div
                      className="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <span className="text-white text-xl font-bold px-4 text-center">
                        {resort.funFact}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{resort.emoji}</span>
                      <h3 className="text-xl font-black">{resort.name}</h3>
                    </div>
                    <p className="text-gray-500 text-sm">{resort.country}</p>

                    {/* Stats Bar */}
                    <div className="mt-4 flex gap-1">
                      {[...Array(5)].map((_, i) => (
                        <div
                          key={i}
                          className="flex-1 h-2 rounded-full transition-all"
                          style={{
                            backgroundColor: i < 4 ? resort.color : `${resort.color}30`,
                          }}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-gray-400 mt-1">Family Score: 4/5</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* View All Button */}
          <div className="text-center mt-12">
            <button className="group px-10 py-4 bg-[#2D3436] text-white font-bold text-lg rounded-full hover:bg-[#FF6B6B] transition-colors shadow-lg">
              See All 3,000+ Resorts
              <span className="inline-block ml-2 group-hover:translate-x-2 transition-transform">→</span>
            </button>
          </div>
        </div>
      </section>

      {/* How It Works - Playful Steps */}
      <section className="py-16 px-4 bg-white/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-black text-center mb-16">
            Easy as <span className="text-[#FFE066]">1</span> <span className="text-[#4ECDC4]">2</span> <span className="text-[#FF6B6B]">3</span>! 🎉
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: 1, title: 'Pick Your Kids Ages', emoji: '👶', color: '#FFE066', desc: 'Toddlers? Teens? We got you!' },
              { step: 2, title: 'Set Your Budget', emoji: '💰', color: '#4ECDC4', desc: 'From budget to bougie!' },
              { step: 3, title: 'Plan & Go!', emoji: '✈️', color: '#FF6B6B', desc: 'Powder days await!' },
            ].map((item) => (
              <div
                key={item.step}
                className="relative text-center group"
              >
                {/* Step Number - Big & Bold */}
                <div
                  className="w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center text-5xl font-black text-white shadow-lg group-hover:scale-110 group-hover:rotate-12 transition-all"
                  style={{ backgroundColor: item.color }}
                >
                  {item.step}
                </div>

                <div className="text-4xl mb-4">{item.emoji}</div>
                <h3 className="text-xl font-bold mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Fun Quote Section */}
      <section className="py-24 px-4 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative inline-block">
            {/* Quote marks as decoration */}
            <span className="absolute -top-8 -left-8 text-8xl text-[#FFE066]/30 font-serif">&quot;</span>
            <span className="absolute -bottom-8 -right-8 text-8xl text-[#FFE066]/30 font-serif">&quot;</span>

            <blockquote className="text-3xl md:text-4xl font-bold leading-relaxed">
              The best family ski trip isn&apos;t about
              <span className="inline-block mx-2 px-3 py-1 bg-[#4ECDC4] text-white rounded-lg transform -rotate-2">perfect runs</span>
              — it&apos;s about the
              <span className="inline-block mx-2 px-3 py-1 bg-[#FF6B6B] text-white rounded-lg transform rotate-2">hot chocolate</span>
              breaks and
              <span className="inline-block mx-2 px-3 py-1 bg-[#FFE066] rounded-lg transform -rotate-1">silly photos</span>
              in between.
            </blockquote>
          </div>
        </div>
      </section>

      {/* Newsletter - Fun Form */}
      <section className="py-16 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="bg-gradient-to-br from-[#FF6B6B] to-[#FF8E8E] rounded-[40px] p-8 md:p-12 text-white text-center shadow-2xl transform hover:rotate-1 transition-transform">
            <div className="text-6xl mb-4">📬</div>
            <h2 className="text-3xl md:text-4xl font-black mb-4">
              Get the inside scoop! 🍦
            </h2>
            <p className="text-lg opacity-90 mb-8">
              Deals, tips, and ski memes. Weekly. No spam, pinky promise! 🤙
            </p>

            <form className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="your@email.com"
                className="flex-1 px-6 py-4 rounded-full text-[#2D3436] font-medium text-lg focus:outline-none focus:ring-4 focus:ring-white/30"
              />
              <button
                type="submit"
                className="px-8 py-4 bg-[#2D3436] text-white font-bold rounded-full hover:bg-black hover:scale-105 transition-all"
              >
                Yay! 🎉
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer - Playful */}
      <footer className="py-12 px-4 bg-[#2D3436] text-white">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-2">
              <span className="text-3xl">❄️</span>
              <span className="font-bold text-xl">
                snow<span className="text-[#FF6B6B]">there</span>
              </span>
            </div>

            <div className="flex items-center gap-6 text-sm">
              <a href="#" className="hover:text-[#4ECDC4] transition-colors">About</a>
              <a href="#" className="hover:text-[#FFE066] transition-colors">Contact</a>
              <a href="#" className="hover:text-[#FF6B6B] transition-colors">Privacy</a>
              <a href="#" className="hover:text-[#95E1D3] transition-colors">Terms</a>
            </div>

            <div className="flex items-center gap-4 text-2xl">
              <a href="#" className="hover:scale-125 transition-transform">📸</a>
              <a href="#" className="hover:scale-125 transition-transform">🐦</a>
              <a href="#" className="hover:scale-125 transition-transform">📘</a>
            </div>
          </div>

          <div className="text-center mt-8 text-sm text-white/50">
            <p>Made with ❤️ and ☕ and probably too many ❄️ emojis</p>
            <p className="mt-2">© 2026 Snowthere. Keep it fun!</p>
          </div>
        </div>
      </footer>

      {/* Fixed Design Label */}
      <div className="fixed bottom-6 left-6 z-50">
        <Link
          href="/"
          className="flex items-center gap-3 px-4 py-2 bg-[#FFE066] text-[#2D3436] rounded-full shadow-lg hover:scale-110 hover:rotate-3 transition-all border-2 border-[#2D3436]"
        >
          <span className="text-xs tracking-wide">Design 5</span>
          <span className="w-px h-3 bg-[#2D3436]/20" />
          <span className="text-xs font-bold">Spielplatz</span>
          <span className="text-lg">🎪</span>
        </Link>
      </div>

      {/* Custom Styles for Text Stroke */}
      <style jsx>{`
        .text-stroke {
          -webkit-text-stroke: 3px #2D3436;
          color: transparent;
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-bounce {
          animation: bounce 2s infinite;
        }
        .delay-100 { animation-delay: 0.1s; }
        .delay-300 { animation-delay: 0.3s; }
        .delay-500 { animation-delay: 0.5s; }
        .delay-700 { animation-delay: 0.7s; }
      `}</style>
    </div>
  )
}
