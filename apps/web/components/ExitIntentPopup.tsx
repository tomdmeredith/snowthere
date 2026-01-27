'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Shield } from 'lucide-react'
import Link from 'next/link'

const STORAGE_KEY = 'snowthere_exit_popup_shown'
const COOLDOWN_DAYS = 7 // Don't show again for 7 days after dismissal

export function ExitIntentPopup() {
  const [isVisible, setIsVisible] = useState(false)
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')

  // Check if popup should be shown
  const shouldShowPopup = useCallback(() => {
    if (typeof window === 'undefined') return false

    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return true

    const { timestamp, type } = JSON.parse(stored)
    const daysSince = (Date.now() - timestamp) / (1000 * 60 * 60 * 24)

    // If they subscribed, never show again
    if (type === 'subscribed') return false

    // If they dismissed, show again after cooldown
    if (type === 'dismissed' && daysSince < COOLDOWN_DAYS) return false

    return true
  }, [])

  // Exit intent detection
  useEffect(() => {
    if (!shouldShowPopup()) return

    let hasTriggered = false

    const handleMouseLeave = (e: MouseEvent) => {
      // Only trigger when mouse leaves toward top of viewport
      if (e.clientY <= 10 && !hasTriggered) {
        hasTriggered = true
        // Small delay to avoid triggering on scroll
        setTimeout(() => {
          if (shouldShowPopup()) {
            setIsVisible(true)
          }
        }, 100)
      }
    }

    // Only add listener after a delay (don't trigger immediately on page load)
    const timer = setTimeout(() => {
      document.addEventListener('mouseleave', handleMouseLeave)
    }, 5000) // Wait 5 seconds before enabling exit intent

    return () => {
      clearTimeout(timer)
      document.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [shouldShowPopup])

  const handleDismiss = () => {
    setIsVisible(false)
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      timestamp: Date.now(),
      type: 'dismissed'
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setStatus('submitting')

    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          source: 'exit_intent_popup',
          source_detail: window.location.pathname,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Subscription failed')
      }

      // Track in Google Analytics
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'newsletter_signup', {
          event_category: 'engagement',
          event_label: 'exit_intent_popup',
          value: 1,
        })
      }

      // Mark as subscribed (never show again)
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        timestamp: Date.now(),
        type: 'subscribed'
      }))

      setStatus('success')

      // Close after success message
      setTimeout(() => {
        setIsVisible(false)
      }, 2500)

    } catch (error) {
      console.error('Exit popup signup error:', error)
      setStatus('error')
      setTimeout(() => setStatus('idle'), 3000)
    }
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleDismiss}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            aria-hidden="true"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby="exit-popup-title"
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[90vw] max-w-md z-50"
          >
            <div
              className="relative overflow-hidden rounded-3xl p-8 sm:p-10 shadow-2xl"
              style={{
                background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FFABAB 100%)',
              }}
            >
              {/* Close button */}
              <button
                onClick={handleDismiss}
                className="absolute top-4 right-4 p-2 rounded-full bg-white/20 hover:bg-white/30 transition-colors"
                aria-label="Close popup"
              >
                <X className="w-5 h-5 text-white" />
              </button>

              {/* Content */}
              <div className="text-center">
                <div className="text-5xl mb-4">
                  <span aria-hidden="true">Wait!</span>
                </div>

                <h2
                  id="exit-popup-title"
                  className="font-display text-2xl sm:text-3xl font-bold text-white mb-3"
                >
                  Before you go...
                </h2>

                <p className="text-white/90 text-base sm:text-lg mb-6">
                  Get our free family ski trip checklist + monthly deals and destination tips.
                </p>

                {/* Form */}
                {status === 'success' ? (
                  <div className="bg-white/20 backdrop-blur-sm rounded-full px-6 py-4">
                    <p className="text-white font-semibold flex items-center justify-center gap-2">
                      You&apos;re in! Check your inbox.
                      <span className="text-xl" aria-hidden="true">🎉</span>
                    </p>
                  </div>
                ) : status === 'error' ? (
                  <div className="bg-red-500/20 backdrop-blur-sm rounded-full px-6 py-4">
                    <p className="text-white font-semibold">
                      Oops! Something went wrong. Try again?
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-3">
                    <label htmlFor="exit-popup-email" className="sr-only">
                      Email address
                    </label>
                    <input
                      id="exit-popup-email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      required
                      disabled={status === 'submitting'}
                      className="w-full px-6 py-4 rounded-full border-2 border-white/30 bg-white/20 text-white placeholder:text-white/60 focus:outline-none focus:border-white focus:bg-white/30 transition-all disabled:opacity-50"
                    />
                    <motion.button
                      type="submit"
                      disabled={status === 'submitting'}
                      whileHover={{ scale: status === 'submitting' ? 1 : 1.02 }}
                      whileTap={{ scale: status === 'submitting' ? 1 : 0.98 }}
                      className="w-full px-8 py-4 rounded-full bg-white text-coral-600 font-bold shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
                    >
                      {status === 'submitting' ? 'Joining...' : 'Send Me the Checklist!'}
                    </motion.button>
                  </form>
                )}

                {/* Privacy */}
                <p className="mt-4 text-white/60 text-xs flex items-center justify-center gap-1.5">
                  <Shield className="w-3 h-3" />
                  <span>
                    We respect your inbox.{' '}
                    <Link href="/privacy" className="underline hover:text-white/80">
                      Privacy Policy
                    </Link>
                  </span>
                </p>

                {/* No thanks link */}
                <button
                  onClick={handleDismiss}
                  className="mt-4 text-white/70 text-sm hover:text-white underline"
                >
                  No thanks, I&apos;ll figure it out myself
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
