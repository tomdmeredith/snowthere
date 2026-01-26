'use client'

import { useSearchParams } from 'next/navigation'
import { useState, Suspense } from 'react'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight, MailX, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

function UnsubscribeContent() {
  const searchParams = useSearchParams()
  const emailParam = searchParams.get('email') || ''

  const [email, setEmail] = useState(emailParam)
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  const handleUnsubscribe = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!email) {
      setStatus('error')
      setMessage('Please enter your email address.')
      return
    }

    setStatus('loading')

    try {
      const response = await fetch('/api/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim().toLowerCase() }),
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setStatus('success')
        setMessage(data.message)
      } else {
        setStatus('error')
        setMessage(data.error || 'Something went wrong. Please try again.')
      }
    } catch {
      setStatus('error')
      setMessage('Network error. Please try again.')
    }
  }

  return (
    <main className="min-h-screen bg-white">
      <Navbar />

      {/* Breadcrumb */}
      <nav className="bg-dark-50 py-4 border-b border-dark-100">
        <div className="container-page">
          <ol className="breadcrumb">
            <li>
              <Link href="/" className="hover:text-coral-500 transition-colors">
                Home
              </Link>
            </li>
            <li className="breadcrumb-separator">
              <ChevronRight className="w-4 h-4" />
            </li>
            <li className="text-dark-800 font-medium">Unsubscribe</li>
          </ol>
        </div>
      </nav>

      {/* Content */}
      <div className="container-page py-16">
        <div className="max-w-md mx-auto">
          {status === 'success' ? (
            // Success state
            <div className="text-center">
              <div className="inline-flex p-4 rounded-full bg-green-100 mb-6">
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>
              <h1 className="font-display text-3xl font-bold text-dark-800 mb-4">
                You&apos;re Unsubscribed
              </h1>
              <p className="text-dark-600 mb-8">
                {message}
              </p>
              <p className="text-dark-500 text-sm mb-8">
                Changed your mind? You can always{' '}
                <Link href="/#newsletter" className="text-coral-600 hover:underline">
                  subscribe again
                </Link>
                .
              </p>
              <Link
                href="/"
                className="inline-flex items-center justify-center px-6 py-3 rounded-full bg-dark-800 text-white font-medium hover:bg-dark-700 transition-colors"
              >
                Back to Home
              </Link>
            </div>
          ) : (
            // Form state
            <>
              <div className="text-center mb-8">
                <div className="inline-flex p-4 rounded-full bg-coral-100 mb-6">
                  <MailX className="w-12 h-12 text-coral-600" />
                </div>
                <h1 className="font-display text-3xl font-bold text-dark-800 mb-4">
                  Unsubscribe
                </h1>
                <p className="text-dark-600">
                  We&apos;re sorry to see you go. Enter your email below to unsubscribe from all Snowthere emails.
                </p>
              </div>

              <form onSubmit={handleUnsubscribe} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-dark-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="w-full px-4 py-3 rounded-xl border border-dark-200 focus:border-coral-500 focus:ring-2 focus:ring-coral-200 outline-none transition-all"
                    disabled={status === 'loading'}
                    required
                  />
                </div>

                {status === 'error' && (
                  <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 text-red-700 text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{message}</span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={status === 'loading'}
                  className="w-full py-3 px-6 rounded-full bg-dark-800 text-white font-medium hover:bg-dark-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {status === 'loading' ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Unsubscribing...
                    </>
                  ) : (
                    'Unsubscribe'
                  )}
                </button>
              </form>

              <p className="text-center text-dark-500 text-sm mt-6">
                This will remove you from all Snowthere marketing emails.
                You can resubscribe anytime from our homepage.
              </p>
            </>
          )}
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default function UnsubscribePage() {
  return (
    <Suspense fallback={
      <main className="min-h-screen bg-white flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-coral-500" />
      </main>
    }>
      <UnsubscribeContent />
    </Suspense>
  )
}
