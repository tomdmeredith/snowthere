'use client'

import { useEffect } from 'react'

/**
 * Web Vitals Reporter component.
 *
 * Only loads and reports web vitals after the user has consented to cookies.
 * This ensures we respect user privacy preferences while still collecting
 * performance data for users who have opted in.
 */
export function WebVitalsReporter() {
  useEffect(() => {
    // Only report if user has consented to cookies
    const hasConsent = document.cookie.includes('snowthere_cookie_consent')
    if (!hasConsent) return

    // Dynamically import to avoid loading web-vitals if no consent
    import('@/lib/web-vitals').then(({ reportWebVitals }) => {
      reportWebVitals()
    })
  }, [])

  // This component renders nothing
  return null
}
