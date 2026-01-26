/**
 * Core Web Vitals reporting to Google Analytics.
 *
 * Metrics tracked:
 * - CLS (Cumulative Layout Shift): Visual stability
 * - FCP (First Contentful Paint): Loading performance
 * - INP (Interaction to Next Paint): Responsiveness
 * - LCP (Largest Contentful Paint): Loading performance
 * - TTFB (Time to First Byte): Server response time
 */

import { onCLS, onFCP, onINP, onLCP, onTTFB, Metric } from 'web-vitals'

// gtag is declared in CookieConsent.tsx - no need to redeclare

function sendToAnalytics(metric: Metric) {
  if (typeof window === 'undefined' || !window.gtag) return

  // CLS is reported as a decimal (e.g., 0.1), multiply by 1000 for better precision in GA
  const value = Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value)

  window.gtag('event', metric.name, {
    event_category: 'Web Vitals',
    value,
    event_label: metric.id,
    metric_rating: metric.rating,
    non_interaction: true,
  })
}

export function reportWebVitals() {
  onCLS(sendToAnalytics)
  onFCP(sendToAnalytics)
  onINP(sendToAnalytics)
  onLCP(sendToAnalytics)
  onTTFB(sendToAnalytics)
}
