'use client'

import { SkiQualityCalendar } from '@/lib/database.types'
import { motion } from 'framer-motion'

interface SnowConditionsChartProps {
  calendar: SkiQualityCalendar[]
}

// Northern hemisphere: Dec-Apr; Southern: Jun-Oct
const NORTH_ORDER = [12, 1, 2, 3, 4]
const SOUTH_ORDER = [6, 7, 8, 9, 10]

const MONTH_LABELS: Record<number, string> = {
  1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May',
  6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
  11: 'Nov', 12: 'Dec',
}

const CROWD_LABELS: Record<string, string> = {
  low: 'Quiet',
  medium: 'Moderate',
  high: 'Busy',
}

const CROWD_COLORS: Record<string, string> = {
  low: 'bg-teal-400',
  medium: 'bg-gold-400',
  high: 'bg-coral-400',
}

function getBarColor(score: number): string {
  if (score >= 8) return 'from-teal-400 to-teal-500'
  if (score >= 6) return 'from-gold-300 to-gold-400'
  return 'from-coral-400 to-coral-500'
}

function getSortOrder(months: number[]): number[] {
  const hasSouthern = months.some(m => m >= 6 && m <= 10)
  const hasNorthern = months.some(m => m === 12 || (m >= 1 && m <= 4))

  if (hasSouthern && !hasNorthern) return SOUTH_ORDER
  if (hasNorthern) return NORTH_ORDER
  // Fallback: sort by month number
  return [...months].sort((a, b) => a - b)
}

export function SnowConditionsChart({ calendar }: SnowConditionsChartProps) {
  if (!calendar || calendar.length === 0) return null

  const months = calendar.map(c => c.month)
  const sortOrder = getSortOrder(months)

  const sorted = [...calendar].sort((a, b) => {
    const ai = sortOrder.indexOf(a.month)
    const bi = sortOrder.indexOf(b.month)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })

  const bestMonth = sorted.reduce((best, current) => {
    if (!best.family_recommendation) return current
    if (!current.family_recommendation) return best
    return current.family_recommendation > best.family_recommendation ? current : best
  }, sorted[0])

  const maxScore = Math.max(...sorted.map(r => r.family_recommendation ?? 0), 1)

  return (
    <div
      role="img"
      aria-label={`Snow conditions chart showing family scores by month. Best month: ${MONTH_LABELS[bestMonth?.month] ?? 'unknown'} with a score of ${bestMonth?.family_recommendation ?? 'N/A'} out of 10.`}
      className="rounded-2xl bg-white border border-dark-100 shadow-card p-6 sm:p-8"
    >
      <div className="flex items-end justify-center gap-3 sm:gap-5 h-48 sm:h-56">
        {sorted.map((row, i) => {
          const score = row.family_recommendation ?? 0
          const heightPercent = maxScore > 0 ? (score / 10) * 100 : 0
          const isBest = row.id === bestMonth?.id && score >= 8

          return (
            <div key={row.id} className="flex flex-col items-center gap-2 flex-1 max-w-16 sm:max-w-20">
              {/* Best pill */}
              {isBest && (
                <motion.span
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + i * 0.05 }}
                  className="text-[10px] font-bold text-white bg-gradient-to-r from-teal-500 to-teal-600 px-2 py-0.5 rounded-full shadow-teal whitespace-nowrap"
                >
                  Best
                </motion.span>
              )}

              {/* Score label */}
              <span className="text-xs font-bold text-dark-600 tabular-nums">
                {score > 0 ? score : '—'}
              </span>

              {/* Bar */}
              <div className="w-full flex items-end" style={{ height: '100%' }}>
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: `${Math.max(heightPercent, 4)}%` }}
                  transition={{ duration: 0.5, delay: i * 0.07, ease: 'easeOut' }}
                  className={`w-full rounded-t-lg bg-gradient-to-t ${getBarColor(score)} ${
                    isBest ? 'ring-2 ring-teal-300 ring-offset-1' : ''
                  }`}
                />
              </div>

              {/* Crowd dot */}
              {row.crowd_level && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.6 + i * 0.05 }}
                  className="flex flex-col items-center gap-0.5"
                >
                  <div className={`w-2.5 h-2.5 rounded-full ${CROWD_COLORS[row.crowd_level] ?? 'bg-dark-200'}`} />
                  <span className="text-[9px] text-dark-400 font-medium">
                    {CROWD_LABELS[row.crowd_level] ?? ''}
                  </span>
                </motion.div>
              )}

              {/* Month label */}
              <span className="text-xs font-semibold text-dark-700">
                {MONTH_LABELS[row.month] ?? row.month}
              </span>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center gap-4 mt-5 pt-4 border-t border-dark-100">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gradient-to-t from-teal-400 to-teal-500" />
          <span className="text-[10px] text-dark-500 font-medium">Great (8+)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gradient-to-t from-gold-300 to-gold-400" />
          <span className="text-[10px] text-dark-500 font-medium">Good (6-7)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-sm bg-gradient-to-t from-coral-400 to-coral-500" />
          <span className="text-[10px] text-dark-500 font-medium">Fair (&lt;6)</span>
        </div>
      </div>
    </div>
  )
}
