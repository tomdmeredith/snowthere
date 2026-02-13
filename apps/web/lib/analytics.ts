/**
 * Analytics utilities for GA4 event tracking.
 *
 * Events are only sent if:
 * 1. User has consented to analytics cookies
 * 2. GA4 is initialized (window.gtag exists)
 *
 * @module analytics
 */

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void
  }
}

/**
 * Check if GA4 is available and user has consented.
 */
function isAnalyticsReady(): boolean {
  return typeof window !== 'undefined' && typeof window.gtag === 'function'
}

/**
 * Track an outbound link click.
 *
 * Sends a GA4 event with link details for understanding which external
 * resources users find valuable.
 *
 * @param params - Link click parameters
 * @param params.url - The destination URL
 * @param params.linkText - The visible link text
 * @param params.category - Link category (lodging, dining, activity, etc.)
 * @param params.isAffiliate - Whether this is an affiliate link
 * @param params.affiliateProgram - The affiliate program name (if applicable)
 * @param params.resortSlug - The resort page where the click occurred
 */
export function trackOutboundClick({
  url,
  linkText,
  category,
  isAffiliate = false,
  affiliateProgram,
  resortSlug,
}: {
  url: string
  linkText: string
  category: string
  isAffiliate?: boolean
  affiliateProgram?: string
  resortSlug: string
}): void {
  if (!isAnalyticsReady()) return

  // Extract domain for cleaner reporting
  let linkDomain = ''
  try {
    linkDomain = new URL(url).hostname.replace('www.', '')
  } catch {
    linkDomain = 'unknown'
  }

  // GA4 recommended event for outbound links
  window.gtag?.('event', 'click', {
    event_category: 'outbound',
    event_label: linkText,
    link_url: url,
    link_domain: linkDomain,
    link_category: category,
    is_affiliate: isAffiliate,
    affiliate_program: affiliateProgram || undefined,
    resort_slug: resortSlug,
    // transport_type: 'beacon' ensures the event is sent even if user navigates away
    transport_type: 'beacon',
  })
}

/**
 * Track a newsletter signup.
 *
 * @param source - Where the signup form was displayed
 */
export function trackNewsletterSignup(source: string): void {
  if (!isAnalyticsReady()) return

  window.gtag?.('event', 'sign_up', {
    method: 'newsletter',
    source,
  })
}

/**
 * Track a quiz completion.
 *
 * @param resultCount - Number of resort matches shown
 * @param topResult - Slug of the top-ranked resort match
 */
export function trackQuizComplete(resultCount: number, topResult: string): void {
  if (!isAnalyticsReady()) return

  window.gtag?.('event', 'quiz_complete', {
    result_count: resultCount,
    top_result: topResult,
  })
}

/**
 * Track an affiliate link click.
 *
 * @param params - Affiliate click parameters
 * @param params.partner - Affiliate partner name (e.g. 'booking', 'viator')
 * @param params.resortSlug - The resort page where the click occurred
 * @param params.linkUrl - The destination URL
 */
export function trackAffiliateClick({
  partner,
  resortSlug,
  linkUrl,
}: {
  partner: string
  resortSlug: string
  linkUrl: string
}): void {
  if (!isAnalyticsReady()) return

  window.gtag?.('event', 'affiliate_click', {
    partner,
    resort_slug: resortSlug,
    link_url: linkUrl,
    transport_type: 'beacon',
  })
}

/**
 * Track a resort page view with enhanced data.
 *
 * @param resortSlug - The resort slug
 * @param resortName - The resort name
 * @param country - The country
 */
export function trackResortView(
  resortSlug: string,
  resortName: string,
  country: string
): void {
  if (!isAnalyticsReady()) return

  window.gtag?.('event', 'view_item', {
    item_id: resortSlug,
    item_name: resortName,
    item_category: country,
  })
}
