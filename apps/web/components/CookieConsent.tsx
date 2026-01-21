'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Cookie, X, Settings } from 'lucide-react'

const CONSENT_COOKIE_NAME = 'snowthere_cookie_consent'
const CONSENT_EXPIRY_DAYS = 365

type ConsentStatus = 'pending' | 'accepted' | 'declined' | 'custom'

interface ConsentPreferences {
  essential: boolean // Always true
  analytics: boolean
  marketing: boolean
}

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void
    dataLayer?: unknown[]
  }
}

export function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [preferences, setPreferences] = useState<ConsentPreferences>({
    essential: true,
    analytics: false,
    marketing: false,
  })

  useEffect(() => {
    // Check if user has already made a choice
    const savedConsent = getCookie(CONSENT_COOKIE_NAME)
    if (!savedConsent) {
      // No consent given yet, show banner
      setIsVisible(true)
    } else {
      // Apply saved preferences
      try {
        const saved = JSON.parse(savedConsent)
        setPreferences(saved)
        if (saved.analytics) {
          enableAnalytics()
        }
      } catch {
        // Invalid cookie, show banner again
        setIsVisible(true)
      }
    }
  }, [])

  const getCookie = (name: string): string | null => {
    if (typeof document === 'undefined') return null
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() ?? null
    }
    return null
  }

  const setCookie = (name: string, value: string, days: number) => {
    if (typeof document === 'undefined') return
    const expires = new Date()
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`
  }

  const enableAnalytics = () => {
    // Initialize Google Analytics only after consent
    const gaId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID
    if (!gaId || typeof window === 'undefined') return

    // Load gtag.js script
    const script = document.createElement('script')
    script.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`
    script.async = true
    document.head.appendChild(script)

    // Initialize dataLayer and gtag
    window.dataLayer = window.dataLayer || []
    window.gtag = function gtag() {
      window.dataLayer?.push(arguments)
    }
    window.gtag('js', new Date())
    window.gtag('config', gaId, {
      anonymize_ip: true,
      cookie_flags: 'SameSite=None;Secure',
    })
  }

  const savePreferences = (prefs: ConsentPreferences) => {
    setCookie(CONSENT_COOKIE_NAME, JSON.stringify(prefs), CONSENT_EXPIRY_DAYS)
    setPreferences(prefs)
    setIsVisible(false)
    setShowSettings(false)

    if (prefs.analytics) {
      enableAnalytics()
    }
  }

  const handleAcceptAll = () => {
    savePreferences({
      essential: true,
      analytics: true,
      marketing: true,
    })
  }

  const handleDeclineAll = () => {
    savePreferences({
      essential: true,
      analytics: false,
      marketing: false,
    })
  }

  const handleSaveCustom = () => {
    savePreferences(preferences)
  }

  if (!isVisible) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-3xl shadow-2xl border border-dark-200 overflow-hidden">
          {!showSettings ? (
            // Simple consent banner
            <div className="p-6 sm:p-8">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-gold-100 to-gold-50 flex-shrink-0">
                  <Cookie className="w-6 h-6 text-gold-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-display text-xl font-bold text-dark-800 mb-2">
                    We use cookies
                  </h3>
                  <p className="text-dark-600 text-sm mb-4">
                    We use cookies to improve your experience and analyze site usage.
                    You can accept all cookies or customize your preferences.{' '}
                    <Link href="/privacy" className="text-teal-600 hover:underline">
                      Learn more
                    </Link>
                  </p>
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={handleAcceptAll}
                      className="px-6 py-2.5 bg-gradient-to-r from-coral-500 to-coral-600 text-white font-semibold rounded-full shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all"
                    >
                      Accept All
                    </button>
                    <button
                      onClick={handleDeclineAll}
                      className="px-6 py-2.5 bg-dark-100 text-dark-700 font-semibold rounded-full hover:bg-dark-200 transition-all"
                    >
                      Decline Optional
                    </button>
                    <button
                      onClick={() => setShowSettings(true)}
                      className="px-6 py-2.5 text-dark-600 font-medium hover:text-dark-800 transition-all flex items-center gap-2"
                    >
                      <Settings className="w-4 h-4" />
                      Customize
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Detailed settings panel
            <div className="p-6 sm:p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-display text-xl font-bold text-dark-800">
                  Cookie Preferences
                </h3>
                <button
                  onClick={() => setShowSettings(false)}
                  className="p-2 rounded-full hover:bg-dark-100 transition-colors"
                  aria-label="Close settings"
                >
                  <X className="w-5 h-5 text-dark-500" />
                </button>
              </div>

              <div className="space-y-4 mb-6">
                {/* Essential cookies - always on */}
                <div className="p-4 rounded-2xl bg-dark-50 border border-dark-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-dark-800">Essential Cookies</h4>
                      <p className="text-sm text-dark-500 mt-1">
                        Required for the website to function. Cannot be disabled.
                      </p>
                    </div>
                    <div className="px-3 py-1 bg-teal-100 text-teal-700 rounded-full text-sm font-medium">
                      Always On
                    </div>
                  </div>
                </div>

                {/* Analytics cookies */}
                <div className="p-4 rounded-2xl bg-dark-50 border border-dark-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-dark-800">Analytics Cookies</h4>
                      <p className="text-sm text-dark-500 mt-1">
                        Help us understand how visitors use our site (Google Analytics).
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.analytics}
                        onChange={(e) => setPreferences({ ...preferences, analytics: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-dark-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-teal-500"></div>
                    </label>
                  </div>
                </div>

                {/* Marketing cookies */}
                <div className="p-4 rounded-2xl bg-dark-50 border border-dark-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-dark-800">Marketing Cookies</h4>
                      <p className="text-sm text-dark-500 mt-1">
                        Used for personalized advertising (currently not in use).
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.marketing}
                        onChange={(e) => setPreferences({ ...preferences, marketing: e.target.checked })}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-dark-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-teal-500"></div>
                    </label>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleSaveCustom}
                  className="px-6 py-2.5 bg-gradient-to-r from-coral-500 to-coral-600 text-white font-semibold rounded-full shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all"
                >
                  Save Preferences
                </button>
                <button
                  onClick={handleAcceptAll}
                  className="px-6 py-2.5 bg-dark-100 text-dark-700 font-semibold rounded-full hover:bg-dark-200 transition-all"
                >
                  Accept All
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
