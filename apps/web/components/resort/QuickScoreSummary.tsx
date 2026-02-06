'use client'

import { motion } from 'framer-motion'
import { Star, Users, CheckCircle, XCircle, Calendar } from 'lucide-react'

interface QuickScoreSummaryProps {
  familyScore: number | null
  bestAgeMin: number | null
  bestAgeMax: number | null
  perfectIf: string[]
  skipIf: string[]
  lastUpdated?: string
  scoreConfidence?: 'high' | 'medium' | 'low' | null
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

function getConfidenceLabel(confidence: 'high' | 'medium' | 'low' | null | undefined): string | null {
  switch (confidence) {
    case 'high': return 'Comprehensive assessment'
    case 'medium': return 'Based on available data'
    case 'low': return 'Limited data — score may update'
    default: return null
  }
}

export function QuickScoreSummary({
  familyScore,
  bestAgeMin,
  bestAgeMax,
  perfectIf,
  skipIf,
  lastUpdated,
  scoreConfidence,
}: QuickScoreSummaryProps) {
  if (!familyScore) return null

  const topPerfectIf = perfectIf.slice(0, 2)
  const topSkipIf = skipIf[0]

  // Format last updated date
  const formattedDate = lastUpdated
    ? new Date(lastUpdated).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-mint-50 to-teal-50 rounded-3xl p-5 border border-teal-100"
    >
      {/* Header with last updated */}
      {formattedDate && (
        <div className="flex items-center gap-1.5 text-xs text-dark-400 mb-4">
          <Calendar className="w-3 h-3" />
          <span>Updated {formattedDate}</span>
        </div>
      )}

      {/* Score and Age - Stacked Vertically */}
      <div className="space-y-4">
        {/* Score Section */}
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-gradient-to-br from-coral-500 to-coral-600 flex items-center justify-center shadow-coral">
            <span className="text-2xl font-display font-black text-white">
              {familyScore.toFixed(1)}
            </span>
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-xl">{getScoreEmoji(familyScore)}</span>
              <span className="font-display font-bold text-dark-800 text-sm">
                {getScoreLabel(familyScore)}
              </span>
            </div>
            <p className="text-xs text-dark-500">Family Score</p>
            {(() => {
              const confidenceText = scoreConfidence ? getConfidenceLabel(scoreConfidence) : null
              return confidenceText ? (
                <p className="text-[11px] text-dark-400 italic">{confidenceText}</p>
              ) : null
            })()}
          </div>
        </div>

        {/* Age Range */}
        {bestAgeMin && bestAgeMax && (
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-14 h-14 rounded-xl bg-teal-100 flex items-center justify-center">
              <Users className="w-6 h-6 text-teal-600" />
            </div>
            <div className="min-w-0">
              <p className="font-display font-bold text-dark-800 text-sm">
                Ages {bestAgeMin}-{bestAgeMax}
              </p>
              <p className="text-xs text-dark-500">Best for kids</p>
            </div>
          </div>
        )}
      </div>

      {/* Perfect If / Skip If - Stacked */}
      {(topPerfectIf.length > 0 || topSkipIf) && (
        <div className="mt-5 pt-4 border-t border-teal-100 space-y-4">
          {/* Perfect If */}
          {topPerfectIf.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-teal-600 uppercase tracking-wider mb-2">
                Perfect if...
              </p>
              <ul className="space-y-1.5">
                {topPerfectIf.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-dark-700">
                    <CheckCircle className="w-3.5 h-3.5 text-teal-500 flex-shrink-0 mt-0.5" />
                    <span className="leading-tight">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Skip If */}
          {topSkipIf && (
            <div>
              <p className="text-xs font-semibold text-coral-600 uppercase tracking-wider mb-2">
                Skip if...
              </p>
              <div className="flex items-start gap-2 text-xs text-dark-700">
                <XCircle className="w-3.5 h-3.5 text-coral-500 flex-shrink-0 mt-0.5" />
                <span className="leading-tight">{topSkipIf}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}
