/**
 * Shared filter types, constants, and pure functions for resort listing pages.
 * Used by /resorts and /resorts/[country] pages.
 */

// --- Types ---

export type AgeRange = '0-3' | '4-7' | '8-12' | '13+'
export type BudgetTier = '$' | '$$' | '$$$' | '$$$$'
export type SortOption = 'score' | 'price' | 'name'

export interface ResortListItem {
  id: string
  slug: string
  name: string
  country: string
  region: string
  family_metrics: {
    family_overall_score: number | null
    best_age_min: number | null
    best_age_max: number | null
  } | null
  costs: {
    estimated_family_daily: number | null
    currency: string
  } | null
  content: { tagline: string | null } | null
  images: { image_url: string; image_type: string }[] | null
}

export interface FilterParams {
  ages?: string
  country?: string
  budget?: string
  sort?: string
  q?: string
}

// --- Constants ---

export const VALID_AGE_RANGES: AgeRange[] = ['0-3', '4-7', '8-12', '13+']

export const AGE_BOUNDS: Record<AgeRange, { min: number; max: number }> = {
  '0-3': { min: 0, max: 3 },
  '4-7': { min: 4, max: 7 },
  '8-12': { min: 8, max: 12 },
  '13+': { min: 13, max: 99 },
}

export const AGE_LABELS: Record<AgeRange, string> = {
  '0-3': '0-3 years',
  '4-7': '4-7 years',
  '8-12': '8-12 years',
  '13+': '13+ years',
}

export const BUDGET_LABELS: Record<BudgetTier, string> = {
  '$': 'Budget',
  '$$': 'Mid-range',
  '$$$': 'Premium',
  '$$$$': 'Luxury',
}

export const SORT_LABELS: Record<SortOption, string> = {
  score: 'Family Score',
  price: 'Price',
  name: 'A-Z',
}

// --- Parse Functions ---

export function parseAgeRanges(param: string | undefined): AgeRange[] {
  if (!param) return []
  return param
    .split(',')
    .filter((age): age is AgeRange => VALID_AGE_RANGES.includes(age as AgeRange))
}

export function parseBudgetTiers(param: string | undefined): BudgetTier[] {
  if (!param) return []
  const valid: BudgetTier[] = ['$', '$$', '$$$', '$$$$']
  return param
    .split(',')
    .filter((b): b is BudgetTier => valid.includes(b as BudgetTier))
}

export function parseCountries(param: string | undefined): string[] {
  if (!param) return []
  return param.split(',').map((c) => c.trim()).filter(Boolean)
}

export function parseSortOption(param: string | undefined): SortOption {
  if (param === 'price' || param === 'name') return param
  return 'score'
}

// --- Price Tier ---

export function getPriceTier(dailyEstimate: number | null): BudgetTier {
  if (!dailyEstimate) return '$$'
  if (dailyEstimate < 400) return '$'
  if (dailyEstimate < 600) return '$$'
  if (dailyEstimate < 900) return '$$$'
  return '$$$$'
}

export function getPriceTierInfo(dailyEstimate: number | null): { tier: BudgetTier; label: string; isEstimated: boolean } {
  const tier = getPriceTier(dailyEstimate)
  return { tier, label: BUDGET_LABELS[tier], isEstimated: dailyEstimate === null }
}

// --- Filter Functions ---

function rangesOverlap(
  resortMin: number,
  resortMax: number,
  filterMin: number,
  filterMax: number
): boolean {
  return resortMin <= filterMax && resortMax >= filterMin
}

export function filterByAgeRanges(
  resorts: ResortListItem[],
  selectedAges: AgeRange[]
): ResortListItem[] {
  if (selectedAges.length === 0) return resorts

  return resorts.filter((resort) => {
    const metrics = resort.family_metrics
    if (!metrics?.best_age_min || !metrics?.best_age_max) return true

    return selectedAges.some((ageRange) => {
      const bounds = AGE_BOUNDS[ageRange]
      return rangesOverlap(
        metrics.best_age_min!,
        metrics.best_age_max!,
        bounds.min,
        bounds.max
      )
    })
  })
}

export function filterByBudget(
  resorts: ResortListItem[],
  selectedBudgets: BudgetTier[]
): ResortListItem[] {
  if (selectedBudgets.length === 0) return resorts

  return resorts.filter((resort) => {
    const daily = resort.costs?.estimated_family_daily
    if (!daily) return true // Don't exclude for missing data
    return selectedBudgets.includes(getPriceTier(daily))
  })
}

export function filterBySearch(
  resorts: ResortListItem[],
  query: string
): ResortListItem[] {
  if (!query) return resorts
  const q = query.toLowerCase()
  return resorts.filter(
    (r) =>
      r.name.toLowerCase().includes(q) ||
      r.country.toLowerCase().includes(q) ||
      r.region.toLowerCase().includes(q)
  )
}

export function filterByCountries(
  resorts: ResortListItem[],
  countries: string[]
): ResortListItem[] {
  if (countries.length === 0) return resorts
  const set = new Set(countries.map((c) => c.toLowerCase()))
  return resorts.filter((r) => set.has(r.country.toLowerCase()))
}

export function applyAllFilters(
  resorts: ResortListItem[],
  params: FilterParams
): ResortListItem[] {
  let result = resorts
  result = filterBySearch(result, params.q || '')
  result = filterByCountries(result, parseCountries(params.country))
  result = filterByAgeRanges(result, parseAgeRanges(params.ages))
  result = filterByBudget(result, parseBudgetTiers(params.budget))
  return result
}

// --- Sort Functions ---

export function sortResorts(
  resorts: ResortListItem[],
  sort: SortOption
): ResortListItem[] {
  const sorted = [...resorts]
  switch (sort) {
    case 'price':
      return sorted.sort((a, b) => {
        const aPrice = a.costs?.estimated_family_daily ?? Infinity
        const bPrice = b.costs?.estimated_family_daily ?? Infinity
        return aPrice - bPrice
      })
    case 'name':
      return sorted.sort((a, b) => a.name.localeCompare(b.name))
    case 'score':
    default:
      return sorted.sort((a, b) => {
        const aScore = a.family_metrics?.family_overall_score ?? 0
        const bScore = b.family_metrics?.family_overall_score ?? 0
        return bScore - aScore
      })
  }
}

// --- Grouping ---

export function groupByCountry(
  resorts: ResortListItem[]
): Record<string, ResortListItem[]> {
  return resorts.reduce(
    (acc, resort) => {
      if (!acc[resort.country]) acc[resort.country] = []
      acc[resort.country].push(resort)
      return acc
    },
    {} as Record<string, ResortListItem[]>
  )
}

// --- Display Helpers ---

export function getAgeDisplayText(selectedAges: AgeRange[]): string {
  if (selectedAges.length === 0) return ''
  if (selectedAges.length === 4) return 'all ages'

  const allMins = selectedAges.map((age) => AGE_BOUNDS[age].min)
  const allMaxes = selectedAges.map((age) => AGE_BOUNDS[age].max)
  const overallMin = Math.min(...allMins)
  const overallMax = Math.max(...allMaxes)

  if (overallMax >= 99) return `ages ${overallMin}+`
  return `ages ${overallMin}-${overallMax}`
}

// --- URL Construction ---

export function buildFilterUrl(
  base: string,
  params: Record<string, string | undefined>
): string {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value) searchParams.set(key, value)
  }
  const qs = searchParams.toString()
  return qs ? `${base}?${qs}` : base
}

/** Toggle a value in a comma-separated param string */
export function toggleParam(current: string | undefined, value: string): string | undefined {
  const values = current ? current.split(',').filter(Boolean) : []
  const idx = values.indexOf(value)
  if (idx >= 0) {
    values.splice(idx, 1)
  } else {
    values.push(value)
  }
  return values.length > 0 ? values.join(',') : undefined
}

// --- Slug Helpers ---

export function countryToSlug(country: string): string {
  return country.toLowerCase().replace(/\s+/g, '-')
}

export function slugToCountryName(slug: string): string {
  return decodeURIComponent(slug)
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
