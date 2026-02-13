import type { Metadata } from 'next'
import { SITE_URL } from '@/lib/constants'
import { Plus_Jakarta_Sans, Fraunces, Caveat } from 'next/font/google'
import './globals.css'
import { CookieConsent } from '@/components/CookieConsent'
import { WebVitalsReporter } from '@/components/WebVitalsReporter'
import { ExitIntentPopup } from '@/components/ExitIntentPopup'

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
  metadataBase: new URL(SITE_URL),
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
        {/* Skier emoji favicon */}
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎿</text></svg>" />
        {/* Preconnect to Google Fonts for faster font loading (LCP optimization) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {/* Google Analytics is loaded via CookieConsent component after user consent */}
        {/* Admitad affiliate verification */}
        <meta name="verify-admitad" content="c8b708cbb1" />
        {/* Pinterest domain verification */}
        <meta name="p:domain_verify" content="a1e29c5305037a91990662690e4d8371" />
        {/* Travelpayouts affiliate verification */}
        <script
          data-noptimize="1"
          data-cfasync="false"
          data-wpfc-render="false"
          dangerouslySetInnerHTML={{
            __html: `(function () { var script = document.createElement("script"); script.async = 1; script.src = 'https://tp-em.com/NDk4MDA0.js?t=498004'; document.head.appendChild(script); })();`
          }}
        />
        {/* AvantLink ownership verification (temporary - remove after approval) */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function () { var script = document.createElement("script"); script.async = 1; script.src = 'https://classic.avantlink.com/affiliate_app_confirm.php?mode=js&authResponse=d14bc919b2780f144a88cc1ad785f511963eaa85'; document.head.appendChild(script); })();`
          }}
        />
      </head>
      <body className="font-sans bg-white text-dark-800">
        {/* Skip to content link - visible on focus for keyboard users (WCAG 2.4.1) */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:px-4 focus:py-2 focus:bg-coral-500 focus:text-white focus:rounded-full focus:outline-none focus:ring-2 focus:ring-coral-600 focus:ring-offset-2"
        >
          Skip to main content
        </a>
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
        <CookieConsent />
        <WebVitalsReporter />
        <ExitIntentPopup />
      </body>
    </html>
  )
}
