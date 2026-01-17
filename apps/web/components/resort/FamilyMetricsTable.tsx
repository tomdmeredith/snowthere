import { ResortFamilyMetrics } from '@/lib/database.types'
import {
  Star,
  Users,
  Mountain,
  Baby,
  GraduationCap,
  Ticket,
  Sparkles,
  TreePine
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
    <section>
      <h2 className="font-display text-2xl font-semibold text-slate-900 mb-6">
        The Numbers
      </h2>

      <div className="data-table">
        <table className="w-full">
          <thead>
            <tr>
              <th className="rounded-tl-xl">Metric</th>
              <th className="text-right rounded-tr-xl">Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => {
              const Icon = row.icon
              return (
                <tr key={row.label}>
                  <td className="flex items-center gap-3">
                    <span className={`p-2 rounded-lg ${row.highlight ? 'bg-glow-100' : 'bg-cream-100'}`}>
                      <Icon className={`w-4 h-4 ${row.highlight ? 'text-glow-600' : 'text-slate-500'}`} />
                    </span>
                    <span className="font-medium text-slate-800">{row.label}</span>
                  </td>
                  <td className="text-right">
                    <span className={row.highlight ? 'highlight text-lg' : 'text-slate-700'}>
                      {row.value}
                    </span>
                    {row.subvalue && (
                      <span className="block text-xs text-slate-500 mt-0.5">
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
