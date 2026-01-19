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
    <section id="the-numbers" className="space-y-6">
      {/* Editorial Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-2xl bg-slate-100 border border-slate-200">
          <BarChart3 className="w-5 h-5 text-slate-600" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="h-px w-4 bg-slate-300" />
            <h2 className="font-display text-2xl font-semibold text-espresso-900">
              The Numbers
            </h2>
          </div>
          <p className="text-sm text-espresso-500 mt-0.5">What families need to know</p>
        </div>
      </div>

      {/* Soft card container */}
      <div className="card bg-ivory-50/70 border-ivory-100 p-0 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-ivory-100/50">
              <th className="text-left px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                Metric
              </th>
              <th className="text-right px-5 py-3.5 text-xs font-medium uppercase tracking-wide text-espresso-500">
                Value
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ivory-100">
            {rows.map((row) => {
              const Icon = row.icon
              return (
                <tr
                  key={row.label}
                  className={`transition-colors ${row.highlight ? 'bg-crimson-50/50' : 'hover:bg-ivory-50'}`}
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <span className={`p-2 rounded-xl ${row.highlight ? 'bg-crimson-100' : 'bg-white'} shadow-sm`}>
                        <Icon className={`w-4 h-4 ${row.highlight ? 'text-crimson-600' : 'text-espresso-400'}`} />
                      </span>
                      <span className="font-medium text-espresso-800">{row.label}</span>
                    </div>
                  </td>
                  <td className="text-right px-5 py-4">
                    <span className={row.highlight ? 'font-semibold text-lg text-crimson-700' : 'text-espresso-700'}>
                      {row.value}
                    </span>
                    {row.subvalue && (
                      <span className="block text-xs text-espresso-400 mt-0.5">
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
