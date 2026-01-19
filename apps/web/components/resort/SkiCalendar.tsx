import { SkiQualityCalendar } from '@/lib/database.types'
import { Snowflake, Users, Star, CalendarHeart } from 'lucide-react'

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
  if (!score) return <span className="text-espresso-300">—</span>
  return (
    <div className="flex justify-center gap-1">
      {[1, 2, 3, 4, 5].map((i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full transition-colors ${
            i <= score ? 'bg-slate-500' : 'bg-ivory-200'
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
        <span className="inline-flex items-center gap-1 bg-pine-50 text-pine-700 px-2.5 py-1 text-xs font-medium rounded-full border border-pine-200">
          <span className="w-1.5 h-1.5 rounded-full bg-pine-500" />
          Quiet
        </span>
      )
    case 'medium':
      return (
        <span className="inline-flex items-center gap-1 bg-camel-50 text-camel-700 px-2.5 py-1 text-xs font-medium rounded-full border border-camel-200">
          <span className="w-1.5 h-1.5 rounded-full bg-camel-500" />
          Moderate
        </span>
      )
    case 'high':
      return (
        <span className="inline-flex items-center gap-1 bg-crimson-50 text-crimson-700 px-2.5 py-1 text-xs font-medium rounded-full border border-crimson-200">
          <span className="w-1.5 h-1.5 rounded-full bg-crimson-500" />
          Busy
        </span>
      )
    default:
      return <span className="text-espresso-300">—</span>
  }
}

const FamilyScoreBadge = ({ score }: { score: number | null }) => {
  if (!score) return <span className="text-espresso-300">—</span>

  let colorClass = 'bg-espresso-50 text-espresso-700 border-espresso-200'
  if (score >= 9) colorClass = 'bg-pine-500 text-white border-pine-600'
  else if (score >= 8) colorClass = 'bg-pine-50 text-pine-700 border-pine-200'
  else if (score >= 6) colorClass = 'bg-camel-50 text-camel-700 border-camel-200'
  else colorClass = 'bg-crimson-50 text-crimson-700 border-crimson-200'

  return (
    <span className={`inline-block ${colorClass} px-3 py-1 text-sm font-semibold rounded-full border`}>
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
    <section id="when-to-go" className="space-y-6">
      {/* Editorial Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-2xl bg-slate-100 border border-slate-200">
          <CalendarHeart className="w-5 h-5 text-slate-600" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="h-px w-4 bg-slate-300" />
            <h2 className="font-display text-2xl font-semibold text-espresso-900">
              When to Go
            </h2>
          </div>
          <p className="text-sm text-espresso-500 mt-0.5">
            Snow conditions, crowd levels, and family scores by month
          </p>
        </div>
      </div>

      {/* Month Cards for Mobile */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:hidden gap-4">
        {sortedCalendar.map((row) => {
          const isBest = row.id === bestMonth?.id && row.family_recommendation && row.family_recommendation >= 8
          return (
            <div
              key={row.id}
              className={`card p-5 transition-all ${
                isBest
                  ? 'border-2 border-pine-300 bg-pine-50/70 shadow-md'
                  : 'bg-ivory-50/70 border-ivory-100 hover:bg-white'
              }`}
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-2">
                  <span className="font-display font-semibold text-lg text-espresso-900">
                    {MONTH_MAP[row.month] || row.month}
                  </span>
                  {isBest && (
                    <span className="text-xs font-medium text-white bg-pine-500 px-2 py-0.5 rounded-full">
                      Best for families
                    </span>
                  )}
                </div>
                <FamilyScoreBadge score={row.family_recommendation} />
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="space-y-1.5">
                  <span className="text-espresso-400 text-xs font-medium uppercase tracking-wide">Snow</span>
                  <div>
                    <SnowDots score={row.snow_quality_score} />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <span className="text-espresso-400 text-xs font-medium uppercase tracking-wide">Crowds</span>
                  <div>
                    <CrowdBadge level={row.crowd_level} />
                  </div>
                </div>
              </div>
              {row.notes && (
                <p className="mt-4 text-sm text-espresso-600 border-t border-pine-100 pt-4 leading-relaxed">
                  {row.notes}
                </p>
              )}
            </div>
          )
        })}
      </div>

      {/* Table for Desktop */}
      <div className="hidden lg:block">
        <div className="card bg-ivory-50/70 border-ivory-100 p-0 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-slate-100/50">
                <th className="text-left px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                  Month
                </th>
                <th className="text-center px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                  <div className="flex items-center justify-center gap-1.5">
                    <Snowflake className="w-3.5 h-3.5 text-slate-500" />
                    Snow
                  </div>
                </th>
                <th className="text-center px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                  <div className="flex items-center justify-center gap-1.5">
                    <Users className="w-3.5 h-3.5 text-camel-500" />
                    Crowds
                  </div>
                </th>
                <th className="text-center px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                  <div className="flex items-center justify-center gap-1.5">
                    <Star className="w-3.5 h-3.5 text-camel-500" />
                    Family Score
                  </div>
                </th>
                <th className="text-left px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ivory-100">
              {sortedCalendar.map((row) => {
                const isBest = row.id === bestMonth?.id && row.family_recommendation && row.family_recommendation >= 8
                return (
                  <tr
                    key={row.id}
                    className={`transition-colors ${isBest ? 'bg-pine-50/70' : 'hover:bg-ivory-50'}`}
                  >
                    <td className="px-5 py-4 font-medium text-espresso-900">
                      <div className="flex items-center gap-2">
                        {MONTH_SHORT[row.month] || row.month}
                        {isBest && (
                          <span className="text-xs font-medium text-white bg-pine-500 px-2 py-0.5 rounded-full">
                            Best
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-center">
                      <SnowDots score={row.snow_quality_score} />
                    </td>
                    <td className="px-5 py-4 text-center">
                      <CrowdBadge level={row.crowd_level} />
                    </td>
                    <td className="px-5 py-4 text-center">
                      <FamilyScoreBadge score={row.family_recommendation} />
                    </td>
                    <td className="px-5 py-4 text-espresso-600 text-sm">
                      {row.notes || '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <p className="text-xs text-espresso-400 mt-5 text-center italic">
        Snow rating shown as dots (1-5). Family score considers snow, crowds, prices, and school holidays.
      </p>
    </section>
  )
}
