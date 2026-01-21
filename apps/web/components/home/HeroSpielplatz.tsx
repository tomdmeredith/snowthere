'use client'

import { motion } from 'framer-motion'
import Image from 'next/image'
import { AgeSelector } from './AgeSelector'

const HEADLINE_WORDS = [
  { text: 'WHERE', color: '#FF6B6B', rotate: -2 },
  { text: 'SHOULD', color: '#4ECDC4', rotate: 1 },
  { text: 'WE', color: '#FFE066', rotate: -1 },
  { text: 'SKI?', color: '#95E1D3', rotate: 3, outlined: true },
]

export function HeroSpielplatz() {
  return (
    <section className="relative overflow-hidden py-16 sm:py-20 lg:py-24">
      {/* Warm gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]" />

      {/* Decorative bouncing emojis */}
      <div className="absolute top-20 left-[8%] animate-bounce-emoji" style={{ animationDelay: '0s' }}>
        <span className="text-4xl">⛷️</span>
      </div>
      <div className="absolute bottom-32 right-[12%] animate-bounce-emoji" style={{ animationDelay: '0.5s' }}>
        <span className="text-3xl">🎿</span>
      </div>
      <div className="absolute top-1/3 right-[5%] animate-bounce-emoji" style={{ animationDelay: '1s' }}>
        <span className="text-2xl">🏔️</span>
      </div>

      <div className="container-page relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Tilted Hero Image */}
          <motion.div
            initial={{ opacity: 0, rotate: 0 }}
            animate={{ opacity: 1, rotate: -3 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="relative order-2 lg:order-1"
          >
            <div
              className="relative overflow-hidden rounded-3xl"
              style={{
                border: '8px solid #FFE066',
                boxShadow: '0 20px 60px rgba(255, 107, 107, 0.2), 0 10px 30px rgba(45, 52, 54, 0.1)',
              }}
            >
              <Image
                src="/images/generated/hero-snowy-family.png"
                alt="Family enjoying a ski vacation together"
                width={600}
                height={450}
                className="w-full h-auto object-cover"
                priority
              />
              {/* Subtle overlay for text contrast if needed */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />
            </div>

            {/* Fun label on image */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, duration: 0.4 }}
              className="absolute -bottom-4 -right-4 bg-coral-500 text-white px-4 py-2 rounded-full font-semibold shadow-coral-lg transform rotate-3"
            >
              Adventure awaits! ✨
            </motion.div>
          </motion.div>

          {/* Right: Stacked Rotated Headline */}
          <div className="order-1 lg:order-2 text-center lg:text-left">
            {/* Stacked headline */}
            <div className="mb-8 space-y-1">
              {HEADLINE_WORDS.map((word, index) => (
                <motion.div
                  key={word.text}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                  className="block"
                >
                  <span
                    className={`
                      font-display font-black text-5xl sm:text-6xl md:text-7xl lg:text-8xl
                      inline-block leading-[0.85]
                      ${word.outlined ? 'text-stroke-dark' : ''}
                    `}
                    style={{
                      color: word.outlined ? 'transparent' : word.color,
                      transform: `rotate(${word.rotate}deg)`,
                      display: 'inline-block',
                      WebkitTextStroke: word.outlined ? '3px #2D3436' : undefined,
                    }}
                  >
                    {word.text}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Tagline */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="text-lg sm:text-xl text-dark-600 max-w-md mx-auto lg:mx-0 mb-10"
            >
              The fun way to find your next family adventure ✨
            </motion.p>

            {/* Age Selector */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.6 }}
            >
              <AgeSelector />
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  )
}
