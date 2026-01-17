import { ResortCosts } from '@/lib/database.types'
import { Ticket, Home, UtensilsCrossed, Calculator } from 'lucide-react'

interface CostTableProps {
  costs: ResortCosts
}

const formatCurrency = (amount: number | null, currency: string) => {
  if (!amount) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export function CostTable({ costs }: CostTableProps) {
  const currency = costs.currency || 'USD'

  return (
    <div className="card card-warm">
      <div className="flex items-center gap-2 mb-6">
        <div className="p-2 rounded-xl bg-glow-100">
          <Calculator className="w-5 h-5 text-glow-600" />
        </div>
        <h3 className="font-display font-semibold text-slate-900">
          Cost Breakdown
        </h3>
      </div>

      <div className="space-y-4">
        {/* Lift Tickets */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 uppercase tracking-wide">
            <Ticket className="w-3.5 h-3.5" />
            Lift Tickets
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-white rounded-xl p-3 text-center shadow-sm">
              <span className="block text-xs text-slate-500 mb-1">Adult</span>
              <span className="font-semibold text-slate-900">
                {formatCurrency(costs.lift_adult_daily, currency)}
              </span>
              <span className="text-xs text-slate-400">/day</span>
            </div>
            <div className="bg-white rounded-xl p-3 text-center shadow-sm">
              <span className="block text-xs text-slate-500 mb-1">Child</span>
              <span className="font-semibold text-slate-900">
                {formatCurrency(costs.lift_child_daily, currency)}
              </span>
              <span className="text-xs text-slate-400">/day</span>
            </div>
          </div>
        </div>

        {/* Lodging */}
        <div className="space-y-2 pt-2">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 uppercase tracking-wide">
            <Home className="w-3.5 h-3.5" />
            Lodging
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center bg-white rounded-xl p-3 shadow-sm">
              <span className="text-sm text-slate-600">Budget</span>
              <span className="font-medium text-slate-900">
                {formatCurrency(costs.lodging_budget_nightly, currency)}<span className="text-xs text-slate-400">/night</span>
              </span>
            </div>
            <div className="flex justify-between items-center bg-white rounded-xl p-3 shadow-sm border border-forest-200">
              <span className="text-sm text-slate-600">Mid-Range</span>
              <span className="font-medium text-slate-900">
                {formatCurrency(costs.lodging_mid_nightly, currency)}<span className="text-xs text-slate-400">/night</span>
              </span>
            </div>
            <div className="flex justify-between items-center bg-white rounded-xl p-3 shadow-sm">
              <span className="text-sm text-slate-600">Luxury</span>
              <span className="font-medium text-slate-900">
                {formatCurrency(costs.lodging_luxury_nightly, currency)}<span className="text-xs text-slate-400">/night</span>
              </span>
            </div>
          </div>
        </div>

        {/* Meals */}
        {costs.meal_family_avg && (
          <div className="space-y-2 pt-2">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-500 uppercase tracking-wide">
              <UtensilsCrossed className="w-3.5 h-3.5" />
              Meals
            </div>
            <div className="flex justify-between items-center bg-white rounded-xl p-3 shadow-sm">
              <span className="text-sm text-slate-600">Family of 4 avg</span>
              <span className="font-medium text-slate-900">
                {formatCurrency(costs.meal_family_avg, currency)}<span className="text-xs text-slate-400">/day</span>
              </span>
            </div>
          </div>
        )}

        {/* Total Estimate */}
        {costs.estimated_family_daily && (
          <div className="mt-4 pt-4 border-t border-cream-200">
            <div className="bg-forest-800 text-cream-50 rounded-2xl p-4">
              <div className="flex justify-between items-center">
                <div>
                  <span className="block text-forest-200 text-sm">
                    Family of 4 Estimate
                  </span>
                  <span className="text-xs text-forest-300">
                    Lifts + lodging + meals
                  </span>
                </div>
                <span className="font-display font-bold text-2xl">
                  {formatCurrency(costs.estimated_family_daily, currency)}
                  <span className="text-sm font-normal text-forest-300">/day</span>
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
