'use client'

import { motion } from 'framer-motion'
import { ArrowRight, Shield } from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'

// gtag is declared in CookieConsent.tsx - no need to redeclare

export function Newsletter() {
  const [email, setEmail] = useState('')
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setStatus('submitting')

    // Track newsletter signup in Google Analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'newsletter_signup', {
        event_category: 'engagement',
        event_label: 'homepage_newsletter',
        value: 1,
      })
    }

    // TODO: Add actual newsletter signup API call here
    // For now, simulate success
    await new Promise((resolve) => setTimeout(resolve, 500))
    setStatus('success')
    setEmail('')
  }

  return (
    <section className="py-20 sm:py-28">
      <div className="container-page">
        <div className="max-w-2xl mx-auto">
          {/* Card with coral gradient */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative overflow-hidden p-10 sm:p-14 rounded-[40px]"
            style={{
              background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 50%, #FFABAB 100%)',
            }}
          >
            {/* Decorative elements */}
            <div className="absolute top-6 right-6 text-4xl opacity-20 animate-bounce-emoji">
              📬
            </div>
            <div className="absolute bottom-6 left-6 text-3xl opacity-20 animate-bounce-emoji" style={{ animationDelay: '0.5s' }}>
              🍦
            </div>

            <div className="relative z-10 text-center">
              {/* Header */}
              <h2 className="font-display text-3xl sm:text-4xl font-bold text-white mb-4">
                📬 Get the inside scoop! 🍦
              </h2>
              <p className="text-white/90 text-lg max-w-md mx-auto mb-8">
                Monthly destination spotlights, deal alerts, and trip tips.
                Designed for families, never spammy.
              </p>

              {/* Form */}
              {status === 'success' ? (
                <div className="bg-white/20 backdrop-blur-sm rounded-full px-8 py-4 max-w-md mx-auto">
                  <p className="text-white font-semibold flex items-center justify-center gap-2">
                    You&apos;re in! Check your inbox.
                    <span className="text-xl">🎉</span>
                  </p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
                  <label htmlFor="newsletter-email" className="sr-only">
                    Email address for newsletter
                  </label>
                  <input
                    id="newsletter-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    required
                    disabled={status === 'submitting'}
                    aria-describedby="newsletter-privacy"
                    className="flex-1 px-6 py-4 rounded-full border-2 border-white/30 bg-white/20 text-white placeholder:text-white/60 focus:outline-none focus:border-white focus:bg-white/30 transition-all disabled:opacity-50"
                  />
                  <motion.button
                    type="submit"
                    disabled={status === 'submitting'}
                    whileHover={{ scale: status === 'submitting' ? 1 : 1.05 }}
                    whileTap={{ scale: status === 'submitting' ? 1 : 0.95 }}
                    className="px-8 py-4 rounded-full bg-white text-coral-600 font-bold shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {status === 'submitting' ? 'Joining...' : 'Yay!'}
                    <span className="text-xl">{status === 'submitting' ? '⏳' : '🎉'}</span>
                  </motion.button>
                </form>
              )}

              {/* Privacy notice - CAN-SPAM compliance */}
              <div id="newsletter-privacy" className="mt-6 space-y-2">
                <p className="text-white/70 text-sm">
                  Join ski families getting monthly tips. Unsubscribe anytime.
                </p>
                <p className="text-white/50 text-xs flex items-center justify-center gap-1.5">
                  <Shield className="w-3 h-3" />
                  <span>
                    By subscribing, you agree to our{' '}
                    <Link href="/privacy" className="underline hover:text-white/70">
                      Privacy Policy
                    </Link>
                    . We respect your inbox.
                  </span>
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
