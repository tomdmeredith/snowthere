import type { Metadata } from 'next'
import { Plus_Jakarta_Sans, Fraunces, Caveat } from 'next/font/google'
import './globals.css'
import { CookieConsent } from '@/components/CookieConsent'

// SPIELPLATZ Design System Typography
// Plus Jakarta Sans - Swiss-inspired geometry with rounded terminals (body text, UI)
const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-plus-jakarta',
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap',
})

// Fraunces - Distinctive "wonky" serifs, editorial warmth (headlines, display)
const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

// Caveat - Handwritten warmth for personal moments (quotes, annotations)
const caveat = Caveat({
  subsets: ['latin'],
  variable: '--font-caveat',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'Snowthere | Family Ski Resort Guides',
    template: '%s | Snowthere',
  },
  description:
    'Complete family ski guides that make international skiing feel doable. Real costs, honest recommendations, and trip-ready itineraries from parents who get it.',
  keywords: [
    'family ski resorts',
    'skiing with kids',
    'ski vacation planning',
    'family-friendly ski resorts',
    'best ski resorts for families',
    'ski resorts with childcare',
    'affordable family skiing',
    'European ski resorts for families',
  ],
  authors: [{ name: 'Snowthere' }],
  creator: 'Snowthere',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    siteName: 'Snowthere',
  },
  twitter: {
    card: 'summary_large_image',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${plusJakarta.variable} ${fraunces.variable} ${caveat.variable}`}>
      <head>
        {/* Google Analytics is loaded via CookieConsent component after user consent */}
      </head>
      <body className="font-sans bg-white text-dark-800">
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
        <CookieConsent />
      </body>
    </html>
  )
}
