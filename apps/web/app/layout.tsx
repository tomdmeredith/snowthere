import type { Metadata } from 'next'
import { DM_Sans, Fraunces } from 'next/font/google'
import Script from 'next/script'
import './globals.css'

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-dm-sans',
  display: 'swap',
})

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
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
  const gaId = process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID

  return (
    <html lang="en" className={`${dmSans.variable} ${fraunces.variable}`}>
      <head>
        {gaId && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
              strategy="afterInteractive"
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${gaId}');
              `}
            </Script>
          </>
        )}
      </head>
      <body className="font-sans">
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  )
}
