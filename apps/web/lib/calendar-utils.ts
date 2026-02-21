import { SkiQualityCalendar } from '@/lib/database.types'

export const MONTH_MAP: Record<number, string> = {
  1: 'January', 2: 'February', 3: 'March', 4: 'April',
  5: 'May', 6: 'June', 7: 'July', 8: 'August',
  9: 'September', 10: 'October', 11: 'November', 12: 'December',
}

export const MONTH_SHORT: Record<number, string> = {
  1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
  5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
  9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
}

// Northern hemisphere: Dec-Apr; Southern: Jun-Oct
const NORTH_ORDER = [12, 1, 2, 3, 4]
const SOUTH_ORDER = [6, 7, 8, 9, 10]

export function getSortOrder(months: number[]): number[] {
  const hasSouthern = months.some(m => m >= 6 && m <= 10)
  const hasNorthern = months.some(m => m === 12 || (m >= 1 && m <= 4))

  if (hasSouthern && !hasNorthern) return SOUTH_ORDER
  if (hasNorthern) return NORTH_ORDER
  return [...months].sort((a, b) => a - b)
}

export function sortCalendar(calendar: SkiQualityCalendar[]): SkiQualityCalendar[] {
  const months = calendar.map(c => c.month)
  const sortOrder = getSortOrder(months)
  return [...calendar].sort((a, b) => {
    const ai = sortOrder.indexOf(a.month)
    const bi = sortOrder.indexOf(b.month)
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })
}

export function findBestMonth(calendar: SkiQualityCalendar[]): SkiQualityCalendar | undefined {
  if (calendar.length === 0) return undefined
  return calendar.reduce((best, current) => {
    if (best.family_recommendation == null) return current
    if (current.family_recommendation == null) return best
    return current.family_recommendation > best.family_recommendation ? current : best
  }, calendar[0])
}
