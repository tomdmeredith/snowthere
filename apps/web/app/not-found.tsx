import Link from 'next/link'
import { Mountain, Search, Home } from 'lucide-react'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'

export default function NotFoundPage() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="mx-auto w-24 h-24 rounded-full bg-teal-50 flex items-center justify-center mb-8">
            <Mountain className="w-12 h-12 text-teal-400" />
          </div>

          <h1 className="font-display text-4xl font-bold text-dark-800 mb-3">
            This trail doesn&apos;t exist
          </h1>
          <p className="text-lg text-dark-500 mb-8">
            The page you&apos;re looking for may have moved or doesn&apos;t
            exist. Let&apos;s find what you need.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/resorts"
              className="inline-flex items-center gap-2 px-6 py-3 bg-coral-500 text-white rounded-full font-semibold hover:bg-coral-600 transition-colors"
            >
              <Search className="w-4 h-4" />
              Browse resorts
            </Link>
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
      <Footer />
    </>
  )
}
