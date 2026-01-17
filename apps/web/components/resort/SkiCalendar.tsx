import { SkiQualityCalendar } from '@/lib/database.types'
import { Snowflake, Users, Star, Calendar } from 'lucide-react'

interface SkiCalendarProps {
  calendar: SkiQualityCalendar[]
}

const MONTH_MAP: Record<number, string> = {
  12: 'December',
  1: 'January',
  2: 'February',
  3: 'March',
  4: 'April',
}

const MONTH_SHORT: Record<number, string> = {
  12: 'Dec',
  1: 'Jan',
  2: 'Feb',
  3: 'Mar',
  4: 'Apr',
}

const SnowDots = ({ score }: { score: number | null }) => {
  if (!score) return <span className="text-slate-400">—</span>
  return (
    <div className="flex justify-center gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full ${
            i <= score ? 'bg-glow-500' : 'bg-slate-200'
          }`}
        />
      ))}
    </div>
  )
}

const CrowdBadge = ({ level }: { level: string | null }) => {
  switch (level) {
    case 'low':
      return (
        <span className="badge bg-forest-100 text-forest-700 px-2 py-0.5 text-xs">
          Low
        </span>
      )
    case 'medium':
      return (
        <span className="badge bg-gold-100 text-gold-700 px-2 py-0.5 text-xs">
          Medium
        </span>
      )
    case 'high':
      return (
        <span className="badge bg-glow-100 text-glow-700 px-2 py-0.5 text-xs">
          High
        </span>
      )
    default:
      return <span className="text-slate-400">—</span>
  }
}

const FamilyScoreBadge = ({ score }: { score: number | null }) => {
  if (!score) return <span className="text-slate-400">—</span>

  let colorClass = 'bg-slate-100 text-slate-700'
  if (score >= 9) colorClass = 'bg-forest-500 text-white'
  else if (score >= 8) colorClass = 'bg-forest-100 text-forest-700'
  else if (score >= 6) colorClass = 'bg-gold-100 text-gold-700'
  else colorClass = 'bg-glow-100 text-glow-700'

  return (
    <span className={`badge ${colorClass} px-2.5 py-1 text-sm font-semibold`}>
      {score}/10
    </span>
  )
}

export function SkiCalendar({ calendar }: SkiCalendarProps) {
  // Sort calendar by month order for ski season (Dec-Apr)
  const sortOrder = [12, 1, 2, 3, 4]
  const sortedCalendar = [...calendar].sort((a, b) => {
    return sortOrder.indexOf(a.month) - sortOrder.indexOf(b.month)
  })

  // Find best month
  const bestMonth = sortedCalendar.reduce((best, current) => {
    if (!best.family_recommendation) return current
    if (!current.family_recommendation) return best
    return current.family_recommendation > best.family_recommendation ? current : best
  }, sortedCalendar[0])

  return (
    <section>
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-xl bg-forest-100">
          <Calendar className="w-5 h-5 text-forest-600" />
        </div>
        <div>
          <h2 className="font-display text-2xl font-semibold text-slate-900">
            Best Time to Visit
          </h2>
          <p className="text-slate-600 text-sm">
            Real talk on when to go, based on snow, crowds, and family-friendliness
          </p>
        </div>
      </div>

      {/* Month Cards for Mobile */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:hidden gap-3 mb-6">
        {sortedCalendar.map((row) => {
          const isBest = row.id === bestMonth?.id && row.family_recommendation && row.family_recommendation >= 8
          return (
            <div
              key={row.id}
              className={`card p-4 ${
                isBest ? 'border-2 border-forest-300 bg-forest-50' : ''
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <span className="font-display font-semibold text-slate-900">
                    {MONTH_MAP[row.month] || row.month}
                  </span>
                  {isBest && (
                    <span className="ml-2 text-xs font-medium text-forest-600 bg-forest-100 px-2 py-0.5 rounded-full">
                      Best
                    </span>
                  )}
                </div>
                <FamilyScoreBadge score={row.family_recommendation} />
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-slate-500 text-xs">Snow</span>
                  <div className="mt-1">
                    <SnowDots score={row.snow_quality_score} />
                  </div>
                </div>
                <div>
                  <span className="text-slate-500 text-xs">Crowds</span>
                  <div className="mt-1">
                    <CrowdBadge level={row.crowd_level} />
                  </div>
                </div>
              </div>
              {row.notes && (
                <p className="mt-3 text-xs text-slate-600 border-t border-cream-200 pt-3">
                  {row.notes}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Table for Desktop */}
      <div className="hidden lg:block">
        <div className="data-table">
          <table className="w-full">
            <thead>
              <tr>
                <th className="rounded-tl-xl">Month</th>
                <th className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Snowflake className="w-3.5 h-3.5" />
                    Snow
                  </div>
                </th>
                <th className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Users className="w-3.5 h-3.5" />
                    Crowds
                  </div>
                </th>
                <th className="text-center">
                  <div className="flex items-center justify-center gap-1">
                    <Star className="w-3.5 h-3.5" />
                    Family Score
                  </div>
                </th>
                <th className="rounded-tr-xl">Notes</th>
              </tr>
            </thead>
            <tbody>
              {sortedCalendar.map((row) => {
                const isBest = row.id === bestMonth?.id && row.family_recommendation && row.family_recommendation >= 8
                return (
                  <tr
                    key={row.id}
                    className={isBest ? 'bg-forest-50' : ''}
                  >
                    <td className="font-medium text-slate-900">
                      {MONTH_SHORT[row.month] || row.month}
                      {isBest && (
                        <span className="ml-2 text-xs font-medium text-forest-600 bg-forest-100 px-2 py-0.5 rounded-full">
                          Best
                        </span>
                      )}
                    </td>
                    <td className="text-center">
                      <SnowDots score={row.snow_quality_score} />
                    </td>
                    <td className="text-center">
                      <CrowdBadge level={row.crowd_level} />
                    </td>
                    <td className="text-center">
                      <FamilyScoreBadge score={row.family_recommendation} />
                    </td>
                    <td className="text-slate-600 text-sm">
                      {row.notes || '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-xs text-slate-500 mt-4">
        Snow rating (1-5 dots). Family Score considers snow, crowds, prices, and school holidays.
      </p>
    </section>
  )
}
