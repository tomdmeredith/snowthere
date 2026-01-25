'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { TradingCard, getTradingCardColor, getTradingCardRotation } from './TradingCard'

interface Resort {
  id: string
  name: string
  slug: string
  country: string
  region: string | null
  family_metrics?: {
    family_overall_score?: number | null
    best_age_min?: number | null
    best_age_max?: number | null
  }[] | null
  images?: {
    image_url: string
    image_type: string
  }[] | null
}

interface TradingCardGridProps {
  resorts: Resort[]
}

// Fun facts for resorts (could come from DB)
const FUN_FACTS: Record<string, string> = {
  'park-city': 'Largest ski resort in the USA with over 7,300 acres!',
  'zermatt': 'You can ski across the border to Italy for lunch!',
  'st-anton': 'The birthplace of modern alpine skiing since 1901.',
  'niseko': 'Gets over 15 meters of powder snow each season!',
  'chamonix': 'Home to the first Winter Olympics in 1924.',
}

export function TradingCardGrid({ resorts }: TradingCardGridProps) {
  // Show up to 4 resorts for the trading card display
  const displayResorts = resorts.slice(0, 4)

  return (
    <section className="py-20 sm:py-28 bg-white overflow-hidden">
      <div className="container-page">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <span className="font-accent text-2xl text-teal-500 block mb-2">
            Start exploring
          </span>
          <h2 className="font-display text-4xl sm:text-5xl font-bold tracking-tight text-dark-800">
            <span className="text-gold-500">★</span> TOP PICKS <span className="text-gold-500">★</span>
          </h2>
        </motion.div>

        {/* Trading Cards Grid */}
        <div className="flex flex-wrap justify-center gap-6 lg:gap-8 mb-12 px-4">
          {displayResorts.length > 0 ? (
            displayResorts.map((resort, index) => {
              // Find hero image, falling back to any available image
              const heroImage = resort.images?.find(img => img.image_type === 'hero')?.image_url
                || resort.images?.[0]?.image_url

              // Transform family_metrics array to single object for TradingCard
              const metrics = Array.isArray(resort.family_metrics)
                ? resort.family_metrics[0]
                : resort.family_metrics

              return (
                <div key={resort.id} className="w-full sm:w-[280px] max-w-[320px]">
                  <TradingCard
                    number={index + 1}
                    resort={{
                      ...resort,
                      family_metrics: metrics,
                    }}
                    color={getTradingCardColor(index)}
                    baseRotation={getTradingCardRotation(index, displayResorts.length)}
                    image={heroImage}
                    funFact={FUN_FACTS[resort.slug]}
                  />
                </div>
              )
            })
          ) : (
            // Placeholder cards when no resorts
            ['Park City', 'Zermatt', 'St. Anton', 'Niseko'].map((name, index) => (
              <div key={name} className="w-full sm:w-[280px] max-w-[320px]">
                <TradingCard
                  number={index + 1}
                  resort={{
                    id: `placeholder-${index}`,
                    name,
                    slug: name.toLowerCase().replace(/\s+/g, '-'),
                    country: ['USA', 'Switzerland', 'Austria', 'Japan'][index],
                    region: ['Utah', 'Valais', 'Tyrol', 'Hokkaido'][index],
                    family_metrics: {
                      family_overall_score: [8.5, 9.0, 7.5, 8.0][index],
                    },
                  }}
                  color={getTradingCardColor(index)}
                  baseRotation={getTradingCardRotation(index, 4)}
                  funFact={['Largest in USA!', 'Ski to Italy!', 'Birthplace of skiing!', '15m of powder!'][index]}
                />
              </div>
            ))
          )}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
          className="text-center"
        >
          <Link
            href="/resorts"
            className="inline-flex items-center gap-2 bg-coral-500 hover:bg-coral-600 text-white px-8 py-4 rounded-full font-bold text-lg shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all"
          >
            Browse All Resorts
            <motion.span
              animate={{ x: [0, 4, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <ArrowRight className="w-5 h-5" />
            </motion.span>
          </Link>
        </motion.div>
      </div>
    </section>
  )
}
