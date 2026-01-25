/**
 * Resort Linker - Auto-links resort names mentioned in content
 *
 * When content mentions a resort we have a page for (e.g., "similar to Zermatt"),
 * this utility automatically turns the name into a link to that resort's page.
 */

import { supabase } from './supabase'

interface ResortLinkData {
  name: string
  slug: string
  country: string
  pattern: RegExp
}

// Module-level cache (populated on first use, shared across renders)
let resortLinkCache: ResortLinkData[] | null = null

/**
 * Generate name variants for fuzzy matching (St./Sankt/Saint, etc.)
 */
function generateNameVariants(name: string): string[] {
  const variants = [name]
  const lower = name.toLowerCase()

  // Handle St./Sankt/Saint variants (common in European resort names)
  if (lower.startsWith('st. ')) {
    const base = name.slice(4)
    variants.push(`Sankt ${base}`, `Saint ${base}`, `St ${base}`)
  } else if (lower.startsWith('st ')) {
    const base = name.slice(3)
    variants.push(`Sankt ${base}`, `Saint ${base}`, `St. ${base}`)
  } else if (lower.startsWith('sankt ')) {
    const base = name.slice(6)
    variants.push(`St. ${base}`, `St ${base}`, `Saint ${base}`)
  } else if (lower.startsWith('saint ')) {
    const base = name.slice(6)
    variants.push(`St. ${base}`, `St ${base}`, `Sankt ${base}`)
  }

  // Handle Mont/Mount variants
  if (lower.startsWith('mont ')) {
    const base = name.slice(5)
    variants.push(`Mount ${base}`, `Mt. ${base}`, `Mt ${base}`)
  } else if (lower.startsWith('mount ')) {
    const base = name.slice(6)
    variants.push(`Mont ${base}`, `Mt. ${base}`, `Mt ${base}`)
  } else if (lower.startsWith('mt. ')) {
    const base = name.slice(4)
    variants.push(`Mount ${base}`, `Mont ${base}`, `Mt ${base}`)
  } else if (lower.startsWith('mt ')) {
    const base = name.slice(3)
    variants.push(`Mount ${base}`, `Mont ${base}`, `Mt. ${base}`)
  }

  // Handle hyphenated resort names (e.g., "Lech-Zürs" matches "Lech" or "Zürs")
  // Only add components if they're substantial (3+ chars)
  if (name.includes('-')) {
    const parts = name.split('-')
    for (const part of parts) {
      const trimmed = part.trim()
      if (trimmed.length >= 3) {
        variants.push(trimmed)
      }
    }
  }

  return [...new Set(variants)]
}

/**
 * Escape special regex characters in a string
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * Load all published resorts for linking (cached in memory)
 */
export async function getResortLinkData(): Promise<ResortLinkData[]> {
  if (resortLinkCache) return resortLinkCache

  const { data, error } = await supabase
    .from('resorts')
    .select('name, slug, country')
    .eq('status', 'published')

  if (error || !data) {
    console.error('Failed to load resort link data:', error)
    return []
  }

  const resorts: ResortLinkData[] = data.map((r) => {
    const variants = generateNameVariants(r.name)
    // Create pattern that matches any variant, case-insensitive, word-boundary
    const patternStr = variants.map((v) => escapeRegex(v)).join('|')
    return {
      name: r.name,
      slug: r.slug,
      country: r.country,
      // Match whole words only, case-insensitive
      pattern: new RegExp(`\\b(${patternStr})\\b`, 'gi'),
    }
  })

  // Sort by name length descending (match longer names first)
  // e.g., "Whistler Blackcomb" before "Whistler"
  resorts.sort((a, b) => b.name.length - a.name.length)

  resortLinkCache = resorts
  return resorts
}

/**
 * Clear the resort link cache (useful for testing or after data updates)
 */
export function clearResortLinkCache(): void {
  resortLinkCache = null
}

/**
 * Inject resort links into HTML content
 *
 * @param html - The HTML content to process
 * @param excludeResort - Resort name to exclude (don't link current resort's own name)
 * @returns HTML with resort names turned into links
 */
/**
 * Pre-process multiple content sections with resort links
 * Useful for server components that need to process all sections at once
 *
 * @param sections - Object with section names as keys and HTML content as values
 * @param excludeResort - Resort name to exclude from linking
 * @returns Same structure with links injected
 */
export async function injectResortLinksInSections<T extends Record<string, string | null | undefined>>(
  sections: T,
  excludeResort?: string
): Promise<T> {
  const resorts = await getResortLinkData()
  if (resorts.length === 0) return sections

  const result = { ...sections }

  for (const key of Object.keys(result) as (keyof T)[]) {
    const html = result[key]
    if (typeof html === 'string' && html.trim()) {
      result[key] = injectResortLinksInHtml(html, resorts, excludeResort) as T[keyof T]
    }
  }

  return result
}

/**
 * Internal helper that injects links given pre-loaded resort data
 */
function injectResortLinksInHtml(
  html: string,
  resorts: ResortLinkData[],
  excludeResort?: string
): string {
  let result = html

  for (const resort of resorts) {
    if (excludeResort && resort.name.toLowerCase() === excludeResort.toLowerCase()) {
      continue
    }

    result = result.replace(resort.pattern, (match, _captured, offset) => {
      const before = result.slice(0, offset)
      const openTags = (before.match(/<a\b/gi) || []).length
      const closeTags = (before.match(/<\/a>/gi) || []).length

      if (openTags > closeTags) {
        return match
      }

      const countrySlug = resort.country.toLowerCase().replace(/\s+/g, '-')
      const href = `/resorts/${countrySlug}/${resort.slug}`
      return `<a href="${href}" class="resort-link">${match}</a>`
    })
  }

  return result
}

export async function injectResortLinks(
  html: string,
  excludeResort?: string
): Promise<string> {
  const resorts = await getResortLinkData()

  if (resorts.length === 0) return html

  let result = html

  for (const resort of resorts) {
    // Skip if this is the current page's resort (don't self-link)
    if (excludeResort && resort.name.toLowerCase() === excludeResort.toLowerCase()) {
      continue
    }

    // Replace matches with links
    result = result.replace(resort.pattern, (match, _captured, offset) => {
      // Safety check: Don't link if already inside an existing <a> tag
      // Count opening and closing <a> tags before this position
      const before = result.slice(0, offset)
      const openTags = (before.match(/<a\b/gi) || []).length
      const closeTags = (before.match(/<\/a>/gi) || []).length

      if (openTags > closeTags) {
        // We're inside an <a> tag, don't create nested link
        return match
      }

      // Build the link URL
      const countrySlug = resort.country.toLowerCase().replace(/\s+/g, '-')
      const href = `/resorts/${countrySlug}/${resort.slug}`

      // Return the linked version (preserve original case of the match)
      return `<a href="${href}" class="resort-link">${match}</a>`
    })
  }

  return result
}
