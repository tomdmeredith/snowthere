import { ResortFamilyMetrics } from '@/lib/database.types'
import {
  Star,
  Users,
  Mountain,
  Baby,
  GraduationCap,
  Ticket,
  Sparkles,
  TreePine,
  BarChart3
} from 'lucide-react'

interface FamilyMetricsTableProps {
  metrics: ResortFamilyMetrics
}

export function FamilyMetricsTable({ metrics }: FamilyMetricsTableProps) {
  const rows = [
    {
      icon: Star,
      label: 'Family Score',
      value: metrics.family_overall_score ? `${metrics.family_overall_score}/10` : '—',
      highlight: true,
    },
    {
      icon: Users,
      label: 'Best Age Range',
      value:
        metrics.best_age_min && metrics.best_age_max
          ? `${metrics.best_age_min}–${metrics.best_age_max} years`
          : '—',
    },
    {
      icon: Mountain,
      label: 'Kid-Friendly Terrain',
      value: metrics.kid_friendly_terrain_pct
        ? `${metrics.kid_friendly_terrain_pct}%`
        : '—',
    },
    {
      icon: Baby,
      label: 'Childcare Available',
      value: metrics.has_childcare === true ? 'Yes' : metrics.has_childcare === false ? 'No' : '—',
      subvalue: metrics.childcare_min_age ? `From ${metrics.childcare_min_age} months` : undefined,
    },
    {
      icon: GraduationCap,
      label: 'Ski School Min Age',
      value: metrics.ski_school_min_age
        ? `${metrics.ski_school_min_age} years`
        : '—',
    },
    {
      icon: Ticket,
      label: 'Kids Ski Free',
      value: metrics.kids_ski_free_age
        ? `Under ${metrics.kids_ski_free_age}`
        : '—',
    },
    {
      icon: Sparkles,
      label: 'Magic Carpet',
      value: metrics.has_magic_carpet === true ? 'Yes' : metrics.has_magic_carpet === false ? 'No' : '—',
    },
    {
      icon: TreePine,
      label: 'Kids Terrain Park',
      value: metrics.has_terrain_park_kids === true ? 'Yes' : metrics.has_terrain_park_kids === false ? 'No' : '—',
    },
  ]

  return (
    <section id="the-numbers" className="space-y-8">
      {/* Editorial Header - Design-5 */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-dark-100 to-dark-50 border border-dark-200 shadow-card">
          <BarChart3 className="w-6 h-6 text-dark-600" />
        </div>
        <div>
          <div className="flex items-center gap-3">
            <span className="h-1 w-6 bg-gradient-to-r from-coral-400 to-coral-500 rounded-full" />
            <h2 className="font-display text-3xl font-bold text-dark-800">
              The Numbers
            </h2>
          </div>
          <p className="text-dark-500 mt-1 font-medium">What families need to know</p>
        </div>
      </div>

      {/* Design-5: Rounded card with shadow escalation */}
      <div className="rounded-3xl bg-white border border-dark-100 shadow-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gradient-to-r from-dark-100 to-dark-50">
              <th className="text-left px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                Metric
              </th>
              <th className="text-right px-6 py-4 text-xs font-bold uppercase tracking-wider text-dark-600">
                Value
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-100">
            {rows.map((row) => {
              const Icon = row.icon
              return (
                <tr
                  key={row.label}
                  className={`transition-all duration-300 ${
                    row.highlight
                      ? 'bg-gradient-to-r from-coral-50/80 to-coral-50/40'
                      : 'hover:bg-mint-50/30'
                  }`}
                >
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-4">
                      <span className={`p-2.5 rounded-xl transition-all duration-300 ${
                        row.highlight
                          ? 'bg-gradient-to-br from-coral-100 to-coral-50 shadow-coral'
                          : 'bg-white shadow-card group-hover:shadow-card-hover'
                      }`}>
                        <Icon className={`w-5 h-5 ${row.highlight ? 'text-coral-600' : 'text-dark-400'}`} />
                      </span>
                      <span className={`font-semibold ${row.highlight ? 'text-dark-800' : 'text-dark-700'}`}>
                        {row.label}
                      </span>
                    </div>
                  </td>
                  <td className="text-right px-6 py-5">
                    <span className={
                      row.highlight
                        ? 'inline-flex items-center gap-1 px-4 py-1.5 rounded-full bg-gradient-to-r from-coral-500 to-coral-600 text-white font-bold text-lg shadow-coral'
                        : 'font-semibold text-dark-700'
                    }>
                      {row.value}
                    </span>
                    {row.subvalue && (
                      <span className="block text-sm text-dark-400 mt-1 font-medium">
                        {row.subvalue}
                      </span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
