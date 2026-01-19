import { ResortCosts } from '@/lib/database.types'
import { Ticket, Home, UtensilsCrossed, Calculator, Sparkles } from 'lucide-react'

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
    <section id="costs" className="space-y-6">
      {/* Editorial Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-2xl bg-camel-100 border border-camel-200">
          <Calculator className="w-5 h-5 text-camel-600" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="h-px w-4 bg-camel-300" />
            <h2 className="font-display text-2xl font-semibold text-espresso-900">
              Cost Breakdown
            </h2>
          </div>
          <p className="text-sm text-espresso-500 mt-0.5">Real prices for family budgeting</p>
        </div>
      </div>

      <div className="card bg-camel-50/50 border-camel-100 space-y-5">
        {/* Lift Tickets */}
        <div className="space-y-2.5">
          <div className="flex items-center gap-2 text-xs font-medium text-camel-600 uppercase tracking-wide">
            <Ticket className="w-3.5 h-3.5" />
            Lift Tickets
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white rounded-2xl p-4 text-center shadow-sm border border-ivory-100">
              <span className="block text-xs text-espresso-400 mb-1.5">Adult</span>
              <span className="font-semibold text-lg text-espresso-900">
                {formatCurrency(costs.lift_adult_daily, currency)}
              </span>
              <span className="text-xs text-espresso-300">/day</span>
            </div>
            <div className="bg-white rounded-2xl p-4 text-center shadow-sm border border-ivory-100">
              <span className="block text-xs text-espresso-400 mb-1.5">Child</span>
              <span className="font-semibold text-lg text-espresso-900">
                {formatCurrency(costs.lift_child_daily, currency)}
              </span>
              <span className="text-xs text-espresso-300">/day</span>
            </div>
          </div>
        </div>

        {/* Lodging */}
        <div className="space-y-2.5 pt-2">
          <div className="flex items-center gap-2 text-xs font-medium text-espresso-600 uppercase tracking-wide">
            <Home className="w-3.5 h-3.5" />
            Lodging
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center bg-white rounded-xl p-3.5 shadow-sm border border-ivory-100">
              <span className="text-sm text-espresso-600">Budget</span>
              <span className="font-medium text-espresso-900">
                {formatCurrency(costs.lodging_budget_nightly, currency)}<span className="text-xs text-espresso-300 ml-0.5">/night</span>
              </span>
            </div>
            <div className="flex justify-between items-center bg-white rounded-xl p-3.5 shadow-sm border-2 border-camel-200">
              <div className="flex items-center gap-2">
                <span className="text-sm text-espresso-600">Mid-Range</span>
                <span className="text-xs text-camel-600 bg-camel-100 px-2 py-0.5 rounded-full">Popular</span>
              </div>
              <span className="font-medium text-espresso-900">
                {formatCurrency(costs.lodging_mid_nightly, currency)}<span className="text-xs text-espresso-300 ml-0.5">/night</span>
              </span>
            </div>
            <div className="flex justify-between items-center bg-white rounded-xl p-3.5 shadow-sm border border-ivory-100">
              <span className="text-sm text-espresso-600">Luxury</span>
              <span className="font-medium text-espresso-900">
                {formatCurrency(costs.lodging_luxury_nightly, currency)}<span className="text-xs text-espresso-300 ml-0.5">/night</span>
              </span>
            </div>
          </div>
        </div>

        {/* Meals */}
        {costs.meal_family_avg && (
          <div className="space-y-2.5 pt-2">
            <div className="flex items-center gap-2 text-xs font-medium text-pine-600 uppercase tracking-wide">
              <UtensilsCrossed className="w-3.5 h-3.5" />
              Meals
            </div>
            <div className="flex justify-between items-center bg-white rounded-xl p-3.5 shadow-sm border border-ivory-100">
              <span className="text-sm text-espresso-600">Family of 4 avg</span>
              <span className="font-medium text-espresso-900">
                {formatCurrency(costs.meal_family_avg, currency)}<span className="text-xs text-espresso-300 ml-0.5">/day</span>
              </span>
            </div>
          </div>
        )}

        {/* Total Estimate - Softer warm version */}
        {costs.estimated_family_daily && (
          <div className="mt-4 pt-5 border-t border-camel-200">
            <div className="bg-gradient-to-br from-espresso-700 to-espresso-800 text-ivory-50 rounded-2xl p-5 shadow-lg">
              <div className="flex justify-between items-center">
                <div>
                  <div className="flex items-center gap-2 mb-0.5">
                    <Sparkles className="w-4 h-4 text-camel-200" />
                    <span className="text-ivory-100 text-sm font-medium">
                      Family of 4 Estimate
                    </span>
                  </div>
                  <span className="text-xs text-ivory-200/80">
                    Lifts + mid-range lodging + meals
                  </span>
                </div>
                <span className="font-display font-bold text-3xl text-ivory-50">
                  {formatCurrency(costs.estimated_family_daily, currency)}
                  <span className="text-base font-normal text-ivory-200">/day</span>
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
