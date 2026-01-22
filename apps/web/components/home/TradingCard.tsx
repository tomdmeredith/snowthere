'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { motion } from 'framer-motion'
import { Mountain } from 'lucide-react'

interface TradingCardProps {
  number: number
  resort: {
    id: string
    name: string
    slug: string
    country: string
    region: string
    family_metrics?: {
      family_overall_score?: number
      best_age_min?: number
      best_age_max?: number
    }
  }
  color: string
  baseRotation: number
  image?: string
  funFact?: string
}

// Color palette for trading cards
const CARD_COLORS = ['#FF6B6B', '#4ECDC4', '#FFE066', '#95E1D3']

export function getTradingCardColor(index: number): string {
  return CARD_COLORS[index % CARD_COLORS.length]
}

export function getTradingCardRotation(index: number, total: number): number {
  // Calculate rotation: cards fan out from center
  const center = (total - 1) / 2
  return (index - center) * 3
}

export function TradingCard({
  number,
  resort,
  color,
  baseRotation,
  image,
  funFact,
}: TradingCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const score = resort.family_metrics?.family_overall_score
  const hasScore = score !== null && score !== undefined && score > 0
  const scoreSegments = 5
  const filledSegments = hasScore ? Math.round((score / 10) * scoreSegments) : 0

  return (
    <Link
      href={`/resorts/${resort.country.toLowerCase().replace(/\s+/g, '-')}/${resort.slug}`}
      className="block"
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.1, rotate: 0, zIndex: 10 }}
        onHoverStart={() => setIsHovered(true)}
        onHoverEnd={() => setIsHovered(false)}
        style={{
          transform: `rotate(${baseRotation}deg)`,
        }}
        transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        className="relative bg-white rounded-3xl overflow-hidden cursor-pointer"
      >
        {/* Colored border */}
        <div
          className="absolute inset-0 rounded-3xl pointer-events-none"
          style={{
            border: `4px solid ${color}`,
          }}
        />

        {/* Number badge */}
        <div
          className="absolute top-4 right-4 z-10 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg"
          style={{ backgroundColor: color }}
        >
          {String(number).padStart(2, '0')}
        </div>

        {/* Image */}
        <div className="aspect-[4/3] relative overflow-hidden bg-gradient-to-br from-dark-100 to-mint-50">
          {image ? (
            <Image
              src={image}
              alt={resort.name}
              fill
              className={`object-cover transition-transform duration-500 ${
                isHovered ? 'scale-110' : 'scale-100'
              }`}
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <Mountain className="w-16 h-16 text-dark-200" />
            </div>
          )}

          {/* Hover overlay with fun fact */}
          {funFact && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: isHovered ? 1 : 0 }}
              className="absolute inset-0 bg-black/60 flex items-center justify-center p-4"
            >
              <p className="text-white text-center text-sm font-medium">{funFact}</p>
            </motion.div>
          )}

          {/* Country emoji */}
          <div className="absolute top-4 left-4 text-2xl">
            {getCountryEmoji(resort.country)}
          </div>
        </div>

        {/* Content */}
        <div className="p-5">
          <h3 className="font-display text-xl font-bold text-dark-800 mb-1">
            {resort.name}
          </h3>
          <p className="text-dark-500 text-sm mb-4">
            {resort.region ? `${resort.region}, ${resort.country}` : resort.country}
          </p>

          {/* Score bar */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-dark-500">Family:</span>
            {hasScore ? (
              <>
                <div className="flex gap-1 flex-1">
                  {Array.from({ length: scoreSegments }).map((_, i) => (
                    <div
                      key={i}
                      className="h-2 flex-1 rounded-full transition-colors"
                      style={{
                        backgroundColor: i < filledSegments ? color : `${color}30`,
                      }}
                    />
                  ))}
                </div>
                <span className="text-xs font-bold text-dark-700">{score}/10</span>
              </>
            ) : (
              <span className="text-xs text-dark-400 italic">Coming soon</span>
            )}
          </div>
        </div>
      </motion.div>
    </Link>
  )
}

function getCountryEmoji(country: string): string {
  const emojiMap: Record<string, string> = {
    'Switzerland': '🇨🇭',
    'Austria': '🇦🇹',
    'France': '🇫🇷',
    'Italy': '🇮🇹',
    'USA': '🇺🇸',
    'United States': '🇺🇸',
    'Canada': '🇨🇦',
    'Japan': '🇯🇵',
    'Norway': '🇳🇴',
    'Sweden': '🇸🇪',
    'Germany': '🇩🇪',
    'Spain': '🇪🇸',
    'Andorra': '🇦🇩',
  }
  return emojiMap[country] || '🏔️'
}
