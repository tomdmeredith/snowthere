'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { Mountain, RefreshCw, Home } from 'lucide-react'

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Unhandled error:', error)
  }, [error])

  return (
    <main className="min-h-screen bg-white flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="mx-auto w-24 h-24 rounded-full bg-coral-50 flex items-center justify-center mb-8">
          <Mountain className="w-12 h-12 text-coral-400" />
        </div>

        <h1 className="font-display text-3xl font-bold text-dark-800 mb-3">
          Oops, something went wrong
        </h1>
        <p className="text-lg text-dark-500 mb-8">
          We hit an unexpected bump on the slopes. Let&apos;s get you back on
          track.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-6 py-3 bg-coral-500 text-white rounded-full font-semibold hover:bg-coral-600 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try again
          </button>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-dark-100 text-dark-700 rounded-full font-semibold hover:bg-dark-200 transition-colors"
          >
            <Home className="w-4 h-4" />
            Go home
          </Link>
        </div>
      </div>
    </main>
  )
}
