import { ResortCosts } from '@/lib/database.types'
import { Calculator, Sparkles } from 'lucide-react'

interface CostTableProps {
  costs: ResortCosts
}

const formatCurrency = (amount: number | null, currency: string) => {
  // Use 'is null' check to allow 0 values (e.g., free child tickets)
  if (amount === null || amount === undefined) return '—'
  // Handle 0 specially (free)
  if (amount === 0) return 'Free'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function getPriceTier(dailyEstimate: number | null): { tier: string; label: string } {
  if (!dailyEstimate) return { tier: '$$', label: 'Mid-range' }
  if (dailyEstimate < 400) return { tier: '$', label: 'Budget-friendly' }
  if (dailyEstimate < 600) return { tier: '$$', label: 'Mid-range' }
  if (dailyEstimate < 900) return { tier: '$$$', label: 'Premium' }
  return { tier: '$$$$', label: 'Luxury' }
}

export function CostTable({ costs }: CostTableProps) {
  const currency = costs.currency || 'USD'
  const priceTier = getPriceTier(costs.estimated_family_daily)

  return (
    <section id="costs" className="space-y-5">
      {/* Header with Price Tier */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-gold-100 to-gold-50">
            <Calculator className="w-5 h-5 text-gold-600" />
          </div>
          <h2 className="font-display text-lg font-bold text-dark-800">
            Cost Breakdown
          </h2>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gold-100 rounded-full">
          <span className="font-bold text-gold-700">{priceTier.tier}</span>
          <span className="text-xs text-gold-600">{priceTier.label}</span>
        </div>
      </div>

      {/* Semantic Table for 96% AI Parse Rate */}
      <div className="rounded-2xl bg-white border border-dark-100 overflow-hidden">
        <table className="w-full text-sm">
          <caption className="sr-only">
            Cost breakdown for family ski trip
          </caption>
          <thead>
            <tr className="bg-dark-50 border-b border-dark-100">
              <th scope="col" className="text-left py-3 px-4 font-semibold text-dark-600">Category</th>
              <th scope="col" className="text-right py-3 px-4 font-semibold text-dark-600">Price</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-dark-100">
            {/* Lift Tickets Section */}
            <tr className="bg-gold-50/50">
              <td colSpan={2} className="py-2 px-4 text-xs font-bold text-gold-700 uppercase tracking-wider">
                🎟️ Lift Tickets
              </td>
            </tr>
            <tr className="hover:bg-dark-50 transition-colors">
              <td className="py-3 px-4 text-dark-700">Adult (daily)</td>
              <td className="py-3 px-4 text-right font-semibold text-dark-800">
                {formatCurrency(costs.lift_adult_daily, currency)}
              </td>
            </tr>
            <tr className="hover:bg-dark-50 transition-colors">
              <td className="py-3 px-4 text-dark-700">Child (daily)</td>
              <td className="py-3 px-4 text-right font-semibold text-dark-800">
                {formatCurrency(costs.lift_child_daily, currency)}
              </td>
            </tr>
            {costs.lift_family_daily && (
              <tr className="hover:bg-dark-50 transition-colors">
                <td className="py-3 px-4 text-dark-700">Family pack (daily)</td>
                <td className="py-3 px-4 text-right font-semibold text-dark-800">
                  {formatCurrency(costs.lift_family_daily, currency)}
                </td>
              </tr>
            )}

            {/* Lodging Section */}
            <tr className="bg-teal-50/50">
              <td colSpan={2} className="py-2 px-4 text-xs font-bold text-teal-700 uppercase tracking-wider">
                🏠 Lodging (nightly)
              </td>
            </tr>
            <tr className="hover:bg-dark-50 transition-colors">
              <td className="py-3 px-4 text-dark-700">Budget</td>
              <td className="py-3 px-4 text-right font-semibold text-dark-800">
                {formatCurrency(costs.lodging_budget_nightly, currency)}
              </td>
            </tr>
            <tr className="hover:bg-dark-50 transition-colors bg-gold-50/30">
              <td className="py-3 px-4 text-dark-700">
                Mid-range
                <span className="ml-2 text-xs bg-gold-200 text-gold-700 px-2 py-0.5 rounded-full">Popular</span>
              </td>
              <td className="py-3 px-4 text-right font-semibold text-dark-800">
                {formatCurrency(costs.lodging_mid_nightly, currency)}
              </td>
            </tr>
            <tr className="hover:bg-dark-50 transition-colors">
              <td className="py-3 px-4 text-dark-700">Luxury</td>
              <td className="py-3 px-4 text-right font-semibold text-dark-800">
                {formatCurrency(costs.lodging_luxury_nightly, currency)}
              </td>
            </tr>

            {/* Meals Section */}
            {costs.meal_family_avg && (
              <>
                <tr className="bg-coral-50/50">
                  <td colSpan={2} className="py-2 px-4 text-xs font-bold text-coral-700 uppercase tracking-wider">
                    🍽️ Meals
                  </td>
                </tr>
                <tr className="hover:bg-dark-50 transition-colors">
                  <td className="py-3 px-4 text-dark-700">Family of 4 (daily avg)</td>
                  <td className="py-3 px-4 text-right font-semibold text-dark-800">
                    {formatCurrency(costs.meal_family_avg, currency)}
                  </td>
                </tr>
              </>
            )}
          </tbody>
        </table>
      </div>

      {/* Total Estimate Card */}
      {costs.estimated_family_daily && (
        <div className="relative overflow-hidden bg-gradient-to-br from-dark-700 via-dark-800 to-dark-900 text-white rounded-2xl p-5">
          {/* Decorative elements */}
          <div className="absolute top-2 right-2 w-12 h-12 bg-coral-400/20 rounded-full blur-xl" />
          <div className="absolute bottom-2 left-2 w-10 h-10 bg-gold-400/15 rounded-full blur-xl" />

          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-gold-300" />
              <span className="text-sm font-medium text-white/80">
                Family of 4 Daily Estimate
              </span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="font-display font-black text-3xl text-white">
                {formatCurrency(costs.estimated_family_daily, currency)}
              </span>
              <span className="text-white/50">/day</span>
            </div>
            <p className="text-xs text-white/50 mt-2">
              Includes lifts, mid-range lodging, and meals
            </p>
          </div>
        </div>
      )}
    </section>
  )
}
