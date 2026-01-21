'use client'

import { motion } from 'framer-motion'
import { Star, Users, CheckCircle, XCircle } from 'lucide-react'

interface QuickScoreSummaryProps {
  familyScore: number | null
  bestAgeMin: number | null
  bestAgeMax: number | null
  perfectIf: string[]
  skipIf: string[]
}

function getScoreEmoji(score: number): string {
  if (score >= 9) return '🌟'
  if (score >= 8) return '⭐'
  if (score >= 7) return '👍'
  if (score >= 6) return '👌'
  return '🤔'
}

function getScoreLabel(score: number): string {
  if (score >= 9) return 'Exceptional'
  if (score >= 8) return 'Excellent'
  if (score >= 7) return 'Very Good'
  if (score >= 6) return 'Good'
  return 'Fair'
}

export function QuickScoreSummary({
  familyScore,
  bestAgeMin,
  bestAgeMax,
  perfectIf,
  skipIf,
}: QuickScoreSummaryProps) {
  if (!familyScore) return null

  const topPerfectIf = perfectIf.slice(0, 3)
  const topSkipIf = skipIf[0]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-mint-50 to-teal-50 rounded-3xl p-6 border border-teal-100"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Score Section */}
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-br from-coral-500 to-coral-600 flex items-center justify-center shadow-coral">
            <span className="text-3xl font-display font-black text-white">
              {familyScore}
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">{getScoreEmoji(familyScore)}</span>
              <span className="font-display font-bold text-dark-800">
                {getScoreLabel(familyScore)}
              </span>
            </div>
            <p className="text-sm text-dark-500">Family Score</p>
          </div>
        </div>

        {/* Age Range */}
        {bestAgeMin && bestAgeMax && (
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-teal-100 flex items-center justify-center">
              <Users className="w-7 h-7 text-teal-600" />
            </div>
            <div>
              <p className="font-display font-bold text-dark-800">
                Ages {bestAgeMin}-{bestAgeMax}
              </p>
              <p className="text-sm text-dark-500">Best for kids</p>
            </div>
          </div>
        )}
      </div>

      {/* Perfect If / Skip If */}
      {(topPerfectIf.length > 0 || topSkipIf) && (
        <div className="mt-6 pt-6 border-t border-teal-100 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Perfect If */}
          {topPerfectIf.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-teal-600 uppercase tracking-wider mb-2">
                Perfect if you...
              </p>
              <ul className="space-y-1.5">
                {topPerfectIf.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-dark-700">
                    <CheckCircle className="w-4 h-4 text-teal-500 flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Skip If */}
          {topSkipIf && (
            <div>
              <p className="text-xs font-semibold text-coral-600 uppercase tracking-wider mb-2">
                Skip if you...
              </p>
              <div className="flex items-start gap-2 text-sm text-dark-700">
                <XCircle className="w-4 h-4 text-coral-500 flex-shrink-0 mt-0.5" />
                <span>{topSkipIf}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}
