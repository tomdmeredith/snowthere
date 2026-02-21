import { SkiQualityCalendar } from '@/lib/database.types'
import { Snowflake, Users, Star, CalendarHeart } from 'lucide-react'
import { SnowConditionsChart } from './SnowConditionsChart'

interface SkiCalendarProps {
  calendar: SkiQualityCalendar[]
}

const MONTH_MAP: Record<number, string> = {
  1: 'January', 2: 'February', 3: 'March', 4: 'April',
  5: 'May', 6: 'June', 7: 'July', 8: 'August',
  9: 'September', 10: 'October', 11: 'November', 12: 'December',
}

const MONTH_SHORT: Record<number, string> = {
  1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
  5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
  9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
}

// Hemisphere-aware sort ordering (matches SnowConditionsChart.tsx)
const NORTH_ORDER = [12, 1, 2, 3, 4]
const SOUTH_ORDER = [6, 7, 8, 9, 10]

function getSortOrder(months: number[]): number[] {
  const hasSouthern = months.some(m => m >= 6 && m <= 10)
  const hasNorthern = months.some(m => m === 12 || (m >= 1 && m <= 4))

  if (hasSouthern && !hasNorthern) return SOUTH_ORDER
  if (hasNorthern) return NORTH_ORDER
  return [...months].sort((a, b) => a - b)
}

const SnowQualityBadge = ({ score }: { score: number | null }) => {
  if (!score) return <span className="text-dark-300">—</span>
  if (score >= 5) {
    return (
      <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-teal-50 to-mint-50 text-teal-700 px-3 py-1.5 text-xs font-semibold rounded-full border border-teal-200 shadow-sm">
        <span className="w-2 h-2 rounded-full bg-gradient-to-br from-teal-400 to-teal-500" />
        Amazing
      </span>
    )
  }
  if (score >= 4) {
    return (
      <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-teal-50/70 to-mint-50/50 text-teal-600 px-3 py-1.5 text-xs font-semibold rounded-full border border-teal-200/70 shadow-sm">
        <span className="w-2 h-2 rounded-full bg-gradient-to-br from-teal-300 to-teal-400" />
        Great
      </span>
    )
  }
  if (score >= 3) {
    return (
      <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-gold-50 to-gold-100/50 text-gold-700 px-3 py-1.5 text-xs font-semibold rounded-full border border-gold-200 shadow-sm">
        <span className="w-2 h-2 rounded-full bg-gradient-to-br from-gold-400 to-gold-500" />
        Good
      </span>
    )
  }
  if (score >= 2) {
    return (
      <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-coral-50/70 to-coral-100/30 text-coral-600 px-3 py-1.5 text-xs font-semibold rounded-full border border-coral-200/70 shadow-sm">
        <span className="w-2 h-2 rounded-full bg-gradient-to-br from-coral-300 to-coral-400" />
        Okay
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-coral-50 to-coral-100/50 text-coral-700 px-3 py-1.5 text-xs font-semibold rounded-full border border-coral-200 shadow-sm">
      <span className="w-2 h-2 rounded-full bg-gradient-to-br from-coral-400 to-coral-500" />
      Slim
    </span>
  )
}

const CrowdBadge = ({ level }: { level: string | null }) => {
  switch (level) {
    case 'low':
      return (
        <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-teal-50 to-mint-50 text-teal-700 px-3 py-1.5 text-xs font-semibold rounded-full border border-teal-200 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-gradient-to-br from-teal-400 to-teal-500" />
          Quiet
        </span>
      )
    case 'medium':
      return (
        <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-gold-50 to-gold-100/50 text-gold-700 px-3 py-1.5 text-xs font-semibold rounded-full border border-gold-200 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-gradient-to-br from-gold-400 to-gold-500" />
          Moderate
        </span>
      )
    case 'high':
      return (
        <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-coral-50 to-coral-100/50 text-coral-700 px-3 py-1.5 text-xs font-semibold rounded-full border border-coral-200 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-gradient-to-br from-coral-400 to-coral-500" />
          Busy
        </span>
      )
    default:
      return <span className="text-dark-300">—</span>
  }
}

const FamilyScoreBadge = ({ score }: { score: number | null }) => {
  if (!score) return <span className="text-dark-300">—</span>

  // Design-5: Use gradients for better scores
  if (score >= 9) {
    return (
      <span className="inline-flex items-center gap-1 px-4 py-1.5 text-sm font-bold rounded-full bg-gradient-to-r from-teal-500 to-teal-600 text-white shadow-teal">
        {score}
      </span>
    )
  }
  if (score >= 8) {
    return (
      <span className="inline-block px-4 py-1.5 text-sm font-bold rounded-full bg-gradient-to-r from-teal-50 to-mint-50 text-teal-700 border border-teal-200">
        {score}
      </span>
    )
  }
  if (score >= 6) {
    return (
      <span className="inline-block px-4 py-1.5 text-sm font-bold rounded-full bg-gradient-to-r from-gold-50 to-gold-100/50 text-gold-700 border border-gold-200">
        {score}
      </span>
    )
  }
  return (
    <span className="inline-block px-4 py-1.5 text-sm font-bold rounded-full bg-gradient-to-r from-coral-50 to-coral-100/50 text-coral-700 border border-coral-200">
      {score}
    </span>
  )
}

export function SkiCalendar({ calendar }: SkiCalendarProps) {
  // Hemisphere-aware sort: northern (Dec-Apr) or southern (Jun-Oct)
  const months = calendar.map(c => c.month)
  const sortOrder = getSortOrder(months)
  const sortedCalendar = [...calendar].sort((a, b) => {
    const ai = sortOrder.indexOf(a.month)
    const bi = sortOrder.indexOf(b.month)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })

  // Find best month
  const bestMonth = sortedCalendar.reduce((best, current) => {
    if (!best.family_recommendation) return current
    if (!current.family_recommendation) return best
    return current.family_recommendation > best.family_recommendation ? current : best
  }, sortedCalendar[0])

  return (
    <section id="when-to-go" className="space-y-8">
      {/* Editorial Header - Design-5 */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 border border-teal-200 shadow-teal">
          <CalendarHeart className="w-6 h-6 text-teal-600" />
        </div>
        <div>
          <div className="flex items-center gap-3">
            <span className="h-1 w-6 bg-gradient-to-r from-teal-400 to-teal-500 rounded-full" />
            <h2 className="font-display text-3xl font-bold text-dark-800">
              When to Go
            </h2>
          </div>
          <p className="text-dark-500 mt-1 font-medium">
            Snow conditions, crowd levels, and family scores by month
          </p>
        </div>
      </div>

      {/* Visual Bar Chart */}
      <SnowConditionsChart calendar={calendar} />

      {/* Month Cards for Mobile - Design-5 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:hidden gap-5">
        {sortedCalendar.map((row) => {
          const isBest = row.id === bestMonth?.id && row.family_recommendation && row.family_recommendation >= 8
          return (
            <div
              key={row.id}
              className={`rounded-3xl p-6 transition-all duration-300 ${
                isBest
                  ? 'border-2 border-teal-300 bg-gradient-to-br from-teal-50 to-mint-50/70 shadow-teal'
                  : 'bg-white border border-dark-100 shadow-card hover:shadow-card-hover hover:border-teal-200'
              }`}
            >
              <div className="flex justify-between items-start mb-5">
                <div className="flex items-center gap-2">
                  <span className="font-display font-bold text-xl text-dark-800">
                    {MONTH_MAP[row.month] || row.month}
                  </span>
                  {isBest && (
                    <span className="text-xs font-bold text-white bg-gradient-to-r from-teal-500 to-teal-600 px-3 py-1 rounded-full shadow-teal">
                      Best for families
                    </span>
                  )}
                </div>
                <FamilyScoreBadge score={row.family_recommendation} />
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <span className="text-dark-500 text-xs font-bold uppercase tracking-wider">Snow</span>
                  <div>
                    <SnowQualityBadge score={row.snow_quality_score} />
                  </div>
                </div>
                <div className="space-y-2">
                  <span className="text-dark-500 text-xs font-bold uppercase tracking-wider">Crowds</span>
                  <div>
                    <CrowdBadge level={row.crowd_level} />
                  </div>
                </div>
              </div>
              {row.notes && (
                <p className="mt-5 text-sm text-dark-600 border-t border-teal-200/50 pt-5 leading-relaxed">
                  {row.notes}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Table for Desktop - Design-5 */}
      <div className="hidden lg:block">
        <div className="rounded-3xl bg-white border border-dark-100 shadow-card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-dark-100 to-dark-50">
                <th scope="col" className="text-left px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                  Month
                </th>
                <th scope="col" className="text-center px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                  <div className="flex items-center justify-center gap-2">
                    <Snowflake className="w-4 h-4 text-teal-500" />
                    Snow
                  </div>
                </th>
                <th scope="col" className="text-center px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                  <div className="flex items-center justify-center gap-2">
                    <Users className="w-4 h-4 text-gold-500" />
                    Crowds
                  </div>
                </th>
                <th scope="col" className="text-center px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                  <div className="flex items-center justify-center gap-2">
                    <Star className="w-4 h-4 text-coral-500" />
                    Family Score
                  </div>
                </th>
                <th scope="col" className="text-left px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-100">
              {sortedCalendar.map((row) => {
                const isBest = row.id === bestMonth?.id && row.family_recommendation && row.family_recommendation >= 8
                return (
                  <tr
                    key={row.id}
                    className={`transition-all duration-300 ${
                      isBest
                        ? 'bg-gradient-to-r from-teal-50/80 to-mint-50/50'
                        : 'hover:bg-mint-50/30'
                    }`}
                  >
                    <td className="px-6 py-5 font-semibold text-dark-800">
                      <div className="flex items-center gap-3">
                        {MONTH_SHORT[row.month] || row.month}
                        {isBest && (
                          <span className="text-xs font-bold text-white bg-gradient-to-r from-teal-500 to-teal-600 px-2.5 py-1 rounded-full shadow-teal">
                            Best
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-5 text-center">
                      <SnowQualityBadge score={row.snow_quality_score} />
                    </td>
                    <td className="px-6 py-5 text-center">
                      <CrowdBadge level={row.crowd_level} />
                    </td>
                    <td className="px-6 py-5 text-center">
                      <FamilyScoreBadge score={row.family_recommendation} />
                    </td>
                    <td className="px-6 py-5 text-dark-600 text-sm leading-relaxed">
                      {row.notes || '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-xs text-dark-400 mt-5 text-center italic">
        Family score considers snow quality, crowd levels, pricing, and school holidays.
      </p>
    </section>
  )
}
