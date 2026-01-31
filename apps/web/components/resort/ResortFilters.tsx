import Link from 'next/link'
import { X } from 'lucide-react'
import {
  type BudgetTier,
  type SortOption,
  type FilterParams,
  AGE_LABELS,
  BUDGET_LABELS,
  SORT_LABELS,
  VALID_AGE_RANGES,
  parseAgeRanges,
  parseBudgetTiers,
  parseSortOption,
  parseCountries,
  buildFilterUrl,
  toggleParam,
} from '@/lib/resort-filters'
import { MobileFilterToggle } from './MobileFilterToggle'

interface CountryInfo {
  name: string
  count: number
}

interface ResortFiltersProps {
  /** Base URL path ('/resorts' or '/resorts/austria') */
  basePath: string
  /** Current search params */
  searchParams: FilterParams
  /** Available countries with resort counts (omit for country pages) */
  countries?: CountryInfo[]
  /** Total unfiltered resort count */
  totalResorts: number
  /** Filtered resort count */
  filteredCount: number
}

export function ResortFilters({
  basePath,
  searchParams,
  countries,
  totalResorts,
  filteredCount,
}: ResortFiltersProps) {
  const selectedAges = parseAgeRanges(searchParams.ages)
  const selectedBudgets = parseBudgetTiers(searchParams.budget)
  const selectedCountries = parseCountries(searchParams.country)
  const currentSort = parseSortOption(searchParams.sort)
  const hasActiveFilters =
    selectedAges.length > 0 ||
    selectedBudgets.length > 0 ||
    selectedCountries.length > 0 ||
    !!searchParams.q
  const activeFilterCount =
    selectedAges.length + selectedBudgets.length + selectedCountries.length + (searchParams.q ? 1 : 0)

  function urlToggling(key: string, value: string): string {
    const params: Record<string, string | undefined> = {
      q: searchParams.q,
      ages: searchParams.ages,
      budget: searchParams.budget,
      sort: searchParams.sort,
      country: searchParams.country,
    }
    params[key] = toggleParam(params[key], value)
    return buildFilterUrl(basePath, params)
  }

  function urlWith(key: string, value: string | undefined): string {
    const params: Record<string, string | undefined> = {
      q: searchParams.q,
      ages: searchParams.ages,
      budget: searchParams.budget,
      sort: searchParams.sort,
      country: searchParams.country,
    }
    params[key] = value
    return buildFilterUrl(basePath, params)
  }

  function urlRemoving(key: string, value: string): string {
    const params: Record<string, string | undefined> = {
      q: searchParams.q,
      ages: searchParams.ages,
      budget: searchParams.budget,
      sort: searchParams.sort,
      country: searchParams.country,
    }
    const current = params[key]
    if (current) {
      const values = current.split(',').filter((v) => v !== value)
      params[key] = values.length > 0 ? values.join(',') : undefined
    }
    return buildFilterUrl(basePath, params)
  }

  const hasCountries = countries && countries.length > 0

  function renderCountryPills() {
    if (!hasCountries) return null
    return (
      <>
        <span className="text-xs font-semibold text-dark-400 uppercase tracking-wide shrink-0">Country</span>
        {countries.map((c) => {
          const isActive = selectedCountries.some(
            (sc) => sc.toLowerCase() === c.name.toLowerCase()
          )
          return (
            <Link
              key={c.name}
              href={urlToggling('country', c.name)}
              className={`shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-teal-100 text-teal-700'
                  : 'bg-dark-100 text-dark-600 hover:bg-dark-200'
              }`}
            >
              {c.name} ({c.count})
            </Link>
          )
        })}
      </>
    )
  }

  function renderAgePills() {
    return (
      <>
        <span className="text-xs font-semibold text-dark-400 uppercase tracking-wide shrink-0">Ages</span>
        {VALID_AGE_RANGES.map((age) => {
          const isActive = selectedAges.includes(age)
          return (
            <Link
              key={age}
              href={urlToggling('ages', age)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-coral-100 text-coral-700'
                  : 'bg-dark-100 text-dark-600 hover:bg-dark-200'
              }`}
            >
              {age === '13+' ? '13+' : age}
            </Link>
          )
        })}
      </>
    )
  }

  function renderBudgetPills() {
    return (
      <>
        <span className="text-xs font-semibold text-dark-400 uppercase tracking-wide shrink-0">Budget</span>
        {(['$', '$$', '$$$', '$$$$'] as BudgetTier[]).map((tier) => {
          const isActive = selectedBudgets.includes(tier)
          return (
            <Link
              key={tier}
              href={urlToggling('budget', tier)}
              className={`px-3 py-1.5 rounded-full text-sm font-bold transition-all duration-200 ${
                isActive
                  ? 'bg-gold-100 text-gold-700'
                  : 'bg-dark-100 text-dark-600 hover:bg-dark-200'
              }`}
              title={BUDGET_LABELS[tier]}
            >
              {tier}
            </Link>
          )
        })}
      </>
    )
  }

  function renderSortPills() {
    return (
      <>
        <span className="text-xs font-semibold text-dark-400 uppercase tracking-wide shrink-0">Sort</span>
        {(['score', 'price', 'name'] as SortOption[]).map((opt) => {
          const isActive = currentSort === opt
          return (
            <Link
              key={opt}
              href={urlWith('sort', opt === 'score' ? undefined : opt)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-dark-800 text-white'
                  : 'bg-dark-100 text-dark-600 hover:bg-dark-200'
              }`}
            >
              {SORT_LABELS[opt]}
            </Link>
          )
        })}
      </>
    )
  }

  return (
    <div className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-dark-100">
      <div className="container-page py-4 space-y-3">
        {/* Mobile: collapsed behind toggle */}
        <MobileFilterToggle activeCount={activeFilterCount}>
          {hasCountries && (
            <div className="flex flex-wrap items-center gap-2">
              {renderCountryPills()}
            </div>
          )}
          <div className="flex flex-wrap items-center gap-2">
            {renderAgePills()}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {renderBudgetPills()}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {renderSortPills()}
          </div>
        </MobileFilterToggle>

        {/* Desktop: inline horizontal layout */}
        <div className="hidden md:flex flex-wrap items-center gap-3">
          {hasCountries && (
            <div className="flex items-center gap-2 overflow-x-auto pb-1 -mb-1">
              {renderCountryPills()}
            </div>
          )}
          {hasCountries && (
            <div className="w-px h-6 bg-dark-200" />
          )}
          <div className="flex items-center gap-2">
            {renderAgePills()}
          </div>
          <div className="w-px h-6 bg-dark-200" />
          <div className="flex items-center gap-2">
            {renderBudgetPills()}
          </div>
          <div className="w-px h-6 bg-dark-200" />
          <div className="flex items-center gap-2">
            {renderSortPills()}
          </div>
        </div>

        {/* Active filter chips (visible on both mobile and desktop) */}
        {hasActiveFilters && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-dark-500 font-semibold">Filtering by:</span>
            {selectedCountries.map((c) => (
              <Link
                key={`c-${c}`}
                href={urlRemoving('country', c)}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-sm font-semibold hover:bg-teal-200 transition-all group"
              >
                {c}
                <X className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
              </Link>
            ))}
            {selectedAges.map((age) => (
              <Link
                key={`a-${age}`}
                href={urlRemoving('ages', age)}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-coral-100 text-coral-700 rounded-full text-sm font-semibold hover:bg-coral-200 transition-all group"
              >
                {AGE_LABELS[age]}
                <X className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
              </Link>
            ))}
            {selectedBudgets.map((tier) => (
              <Link
                key={`b-${tier}`}
                href={urlRemoving('budget', tier)}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-gold-100 text-gold-700 rounded-full text-sm font-semibold hover:bg-gold-200 transition-all group"
              >
                {tier} {BUDGET_LABELS[tier]}
                <X className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
              </Link>
            ))}
            {searchParams.q && (
              <Link
                href={urlWith('q', undefined)}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-dark-100 text-dark-700 rounded-full text-sm font-semibold hover:bg-dark-200 transition-all group"
              >
                &ldquo;{searchParams.q}&rdquo;
                <X className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
              </Link>
            )}
            <Link
              href={basePath}
              className="text-sm font-medium text-dark-500 hover:text-coral-600 underline underline-offset-2 transition-colors"
            >
              Clear all
            </Link>
            <span className="ml-auto text-sm text-dark-400">
              {filteredCount} of {totalResorts} resorts
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
