'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, MapPin, Users, DollarSign } from 'lucide-react'
import { ResortMatch as ResortMatchType } from '@/lib/quiz/types'

interface ResortMatchProps {
  match: ResortMatchType
  rank: number
  delay?: number
}

const RANK_MEDALS: Record<number, { emoji: string; color: string; label: string }> = {
  1: { emoji: '🥇', color: '#FFD700', label: 'Best Match' },
  2: { emoji: '🥈', color: '#C0C0C0', label: 'Great Match' },
  3: { emoji: '🥉', color: '#CD7F32', label: 'Strong Match' },
}

const PRICE_INDICATORS: Record<string, { icons: number; label: string }> = {
  // Dollar symbol format (used by scoring algorithm)
  '$': { icons: 1, label: 'Budget-friendly' },
  '$$': { icons: 2, label: 'Good value' },
  '$$$': { icons: 3, label: 'Mid-range' },
  '$$$$': { icons: 4, label: 'Premium' },
  // Word format (fallback)
  budget: { icons: 1, label: 'Budget-friendly' },
  value: { icons: 2, label: 'Good value' },
  mid: { icons: 3, label: 'Mid-range' },
  luxury: { icons: 4, label: 'Premium' },
}

export function ResortMatchCard({ match, rank, delay = 0 }: ResortMatchProps) {
  const medal = RANK_MEDALS[rank] || RANK_MEDALS[3]
  const priceInfo = PRICE_INDICATORS[match.priceLevel] || PRICE_INDICATORS['mid']
  const matchPercent = Math.round(match.matchScore * 100)

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        delay,
        type: 'spring',
        stiffness: 200,
        damping: 20,
      }}
      className="relative bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300"
    >
      {/* Rank Banner */}
      <div
        className="absolute top-0 right-0 w-20 h-20 overflow-hidden"
        aria-hidden="true"
      >
        <div
          className="absolute transform rotate-45 text-center text-white text-xs font-bold py-1 right-[-35px] top-[20px] w-[120px]"
          style={{ backgroundColor: medal.color }}
        >
          #{rank}
        </div>
      </div>

      <div className="p-6">
        {/* Medal and Match Score Row */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <motion.span
              className="text-4xl"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{
                delay: delay + 0.2,
                type: 'spring',
                stiffness: 300,
                damping: 15,
              }}
            >
              {medal.emoji}
            </motion.span>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {medal.label}
              </p>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold text-coral-500">
                  {matchPercent}%
                </span>
                <span className="text-sm text-gray-400">match</span>
              </div>
            </div>
          </div>

          {/* Family Score Badge */}
          <div className="flex items-center gap-1 bg-teal-50 text-teal-700 px-3 py-1.5 rounded-full">
            <span className="text-sm">👨‍👩‍👧</span>
            <span className="text-sm font-semibold">{match.familyScore}/10</span>
          </div>
        </div>

        {/* Resort Name and Location */}
        <h3 className="font-display text-2xl font-bold text-gray-900 mb-1">
          {match.name}
        </h3>
        <div className="flex items-center gap-1 text-gray-500 mb-4">
          <MapPin className="w-4 h-4" />
          <span className="text-sm">
            {match.region}, {match.country}
          </span>
        </div>

        {/* Match Reason */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: delay + 0.3 }}
          className="text-gray-600 text-sm italic mb-4 bg-gray-50 p-3 rounded-lg"
        >
          &quot;{match.matchReason}&quot;
        </motion.p>

        {/* Quick Stats */}
        <div className="flex flex-wrap gap-3 mb-5">
          {/* Age Range */}
          <div className="flex items-center gap-1.5 bg-gold-50 text-gold-700 px-3 py-1.5 rounded-full text-sm">
            <Users className="w-3.5 h-3.5" />
            <span>Ages {match.bestAgeMin}-{match.bestAgeMax}</span>
          </div>

          {/* Price Level */}
          <div className="flex items-center gap-1.5 bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full text-sm">
            {Array.from({ length: priceInfo.icons }).map((_, i) => (
              <DollarSign key={i} className="w-3 h-3" />
            ))}
            <span>{priceInfo.label}</span>
          </div>
        </div>

        {/* CTA Button */}
        <Link href={`/resorts/${match.country.toLowerCase()}/${match.slug}`}>
          <motion.button
            whileHover={{ scale: 1.02, x: 4 }}
            whileTap={{ scale: 0.98 }}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-coral-500 to-coral-600 text-white py-3 px-4 rounded-xl font-semibold hover:shadow-lg hover:shadow-coral-500/25 transition-all duration-200"
          >
            See Full Guide
            <ArrowRight className="w-4 h-4" />
          </motion.button>
        </Link>
      </div>

      {/* Decorative gradient border on left */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1"
        style={{
          background: `linear-gradient(to bottom, ${medal.color}, transparent)`,
        }}
      />
    </motion.div>
  )
}
