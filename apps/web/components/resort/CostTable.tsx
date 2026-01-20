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
      {/* Editorial Header - Design-5 */}
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-gold-100 to-gold-50 shadow-gold">
          <Calculator className="w-5 h-5 text-gold-600" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="h-1 w-5 bg-gradient-to-r from-gold-400 to-gold-500 rounded-full" />
            <h2 className="font-display text-xl font-bold text-dark-800">
              Cost Breakdown
            </h2>
          </div>
          <p className="text-sm text-dark-500 mt-1 font-medium">Real prices for family budgeting</p>
        </div>
      </div>

      {/* Design-5: Card with playful styling */}
      <div className="rounded-3xl bg-gradient-to-br from-gold-50/80 to-gold-100/30 border border-gold-200 shadow-gold p-6 space-y-6">
        {/* Lift Tickets */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-gold-700 uppercase tracking-wide">
            <Ticket className="w-4 h-4" />
            Lift Tickets
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-2xl p-5 text-center shadow-card border border-gold-100 hover:shadow-card-hover hover:scale-[1.02] transition-all duration-300">
              <span className="block text-xs text-dark-400 mb-2 font-medium">Adult</span>
              <span className="font-bold text-xl text-dark-800">
                {formatCurrency(costs.lift_adult_daily, currency)}
              </span>
              <span className="text-xs text-dark-400">/day</span>
            </div>
            <div className="bg-white rounded-2xl p-5 text-center shadow-card border border-gold-100 hover:shadow-card-hover hover:scale-[1.02] transition-all duration-300">
              <span className="block text-xs text-dark-400 mb-2 font-medium">Child</span>
              <span className="font-bold text-xl text-dark-800">
                {formatCurrency(costs.lift_child_daily, currency)}
              </span>
              <span className="text-xs text-dark-400">/day</span>
            </div>
          </div>
        </div>

        {/* Lodging */}
        <div className="space-y-3 pt-2">
          <div className="flex items-center gap-2 text-xs font-bold text-dark-600 uppercase tracking-wide">
            <Home className="w-4 h-4" />
            Lodging
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center bg-white rounded-2xl p-4 shadow-card border border-dark-100 hover:shadow-card-hover transition-all duration-300">
              <span className="text-sm text-dark-600 font-medium">Budget</span>
              <span className="font-semibold text-dark-800">
                {formatCurrency(costs.lodging_budget_nightly, currency)}<span className="text-xs text-dark-400 ml-1">/night</span>
              </span>
            </div>
            <div className="flex justify-between items-center bg-white rounded-2xl p-4 shadow-card border-2 border-gold-300 hover:shadow-gold transition-all duration-300">
              <div className="flex items-center gap-2">
                <span className="text-sm text-dark-700 font-medium">Mid-Range</span>
                <span className="text-xs font-semibold text-gold-700 bg-gold-200 px-2.5 py-1 rounded-full">Popular</span>
              </div>
              <span className="font-semibold text-dark-800">
                {formatCurrency(costs.lodging_mid_nightly, currency)}<span className="text-xs text-dark-400 ml-1">/night</span>
              </span>
            </div>
            <div className="flex justify-between items-center bg-white rounded-2xl p-4 shadow-card border border-dark-100 hover:shadow-card-hover transition-all duration-300">
              <span className="text-sm text-dark-600 font-medium">Luxury</span>
              <span className="font-semibold text-dark-800">
                {formatCurrency(costs.lodging_luxury_nightly, currency)}<span className="text-xs text-dark-400 ml-1">/night</span>
              </span>
            </div>
          </div>
        </div>

        {/* Meals */}
        {costs.meal_family_avg && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center gap-2 text-xs font-bold text-teal-700 uppercase tracking-wide">
              <UtensilsCrossed className="w-4 h-4" />
              Meals
            </div>
            <div className="flex justify-between items-center bg-white rounded-2xl p-4 shadow-card border border-teal-100 hover:shadow-teal transition-all duration-300">
              <span className="text-sm text-dark-600 font-medium">Family of 4 avg</span>
              <span className="font-semibold text-dark-800">
                {formatCurrency(costs.meal_family_avg, currency)}<span className="text-xs text-dark-400 ml-1">/day</span>
              </span>
            </div>
          </div>
        )}

        {/* Total Estimate - Design-5 playful dark card */}
        {costs.estimated_family_daily && (
          <div className="mt-2 pt-6 border-t border-gold-200">
            <div className="relative overflow-hidden bg-gradient-to-br from-dark-700 via-dark-800 to-dark-900 text-white rounded-3xl p-6 shadow-2xl">
              {/* Decorative elements */}
              <div className="absolute top-3 right-3 w-16 h-16 bg-coral-400/20 rounded-full blur-2xl" />
              <div className="absolute bottom-3 left-3 w-12 h-12 bg-gold-400/15 rounded-full blur-2xl" />

              <div className="relative z-10 flex justify-between items-center">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Sparkles className="w-5 h-5 text-gold-300" />
                    <span className="text-white font-semibold">
                      Family of 4 Estimate
                    </span>
                  </div>
                  <span className="text-sm text-white/70">
                    Lifts + mid-range lodging + meals
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-display font-black text-3xl sm:text-4xl text-white">
                    {formatCurrency(costs.estimated_family_daily, currency)}
                  </span>
                  <span className="text-lg font-normal text-white/60">/day</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
