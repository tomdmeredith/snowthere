import { Metadata } from 'next'
import Link from 'next/link'
import { SITE_URL } from '@/lib/constants'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight, Shield, Cookie, Database, UserCheck, Mail } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'Learn how Snowthere collects, uses, and protects your personal information. GDPR and CCPA compliant.',
  alternates: {
    canonical: `${SITE_URL}/privacy`,
  },
  openGraph: {
    url: `${SITE_URL}/privacy`,
  },
}

export default function PrivacyPage() {
  const lastUpdated = 'January 20, 2026'

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
            <li className="text-dark-800 font-medium">Privacy Policy</li>
          </ol>
        </div>
      </nav>

      {/* Header */}
      <header className="py-16 bg-gradient-to-br from-teal-50 to-white">
        <div className="container-page">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 shadow-teal">
              <Shield className="w-6 h-6 text-teal-600" />
            </div>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-dark-800">
              Privacy Policy
            </h1>
          </div>
          <p className="text-dark-500 mt-4">Last updated: {lastUpdated}</p>
        </div>
      </header>

      {/* Content */}
      <div className="container-page py-12">
        <div className="max-w-3xl mx-auto prose-family">

          {/* Introduction */}
          <section className="mb-12">
            <p className="text-lg text-dark-600 leading-relaxed">
              Snowthere (&quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) is committed to protecting your privacy.
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information
              when you visit our website snowthere.com.
            </p>
          </section>

          {/* Data Collection */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Database className="w-5 h-5 text-teal-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Information We Collect</h2>
            </div>

            <h3 className="font-display text-xl font-semibold text-dark-700 mt-6 mb-3">Information You Provide</h3>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Email address</strong> - When you subscribe to our newsletter</li>
              <li><strong>Quiz responses</strong> - When you use our resort matching quiz</li>
              <li><strong>Feedback</strong> - When you contact us or report issues</li>
            </ul>

            <h3 className="font-display text-xl font-semibold text-dark-700 mt-6 mb-3">Information Collected Automatically</h3>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Device information</strong> - Browser type, operating system, device type</li>
              <li><strong>Usage data</strong> - Pages visited, time spent, referral source</li>
              <li><strong>IP address</strong> - Used for approximate geographic location</li>
              <li><strong>Cookies</strong> - See Cookie Policy section below</li>
            </ul>
          </section>

          {/* How We Use Data */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">How We Use Your Information</h2>
            <ul className="space-y-2 text-dark-600">
              <li>To send you our newsletter (with your consent)</li>
              <li>To improve our website and content</li>
              <li>To analyze usage patterns and optimize user experience</li>
              <li>To respond to your inquiries</li>
              <li>To comply with legal obligations</li>
            </ul>
          </section>

          {/* Cookie Policy */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Cookie className="w-5 h-5 text-coral-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Cookie Policy</h2>
            </div>

            <p className="text-dark-600 mb-4">
              We use cookies and similar tracking technologies to improve your experience.
              You can control cookies through your browser settings and our cookie consent banner.
            </p>

            <h3 className="font-display text-xl font-semibold text-dark-700 mt-6 mb-3">Types of Cookies We Use</h3>

            <div className="bg-dark-50 rounded-2xl p-6 mb-4">
              <h4 className="font-semibold text-dark-800 mb-2">Essential Cookies</h4>
              <p className="text-dark-600 text-sm">Required for the website to function. Cannot be disabled.</p>
            </div>

            <div className="bg-dark-50 rounded-2xl p-6 mb-4">
              <h4 className="font-semibold text-dark-800 mb-2">Analytics Cookies (Google Analytics)</h4>
              <p className="text-dark-600 text-sm">
                Help us understand how visitors use our site. Only set with your consent.
                Google Analytics may transfer data to the US. See{' '}
                <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:underline">
                  Google&apos;s Privacy Policy
                </a>.
              </p>
            </div>

            <div className="bg-dark-50 rounded-2xl p-6">
              <h4 className="font-semibold text-dark-800 mb-2">Preference Cookies</h4>
              <p className="text-dark-600 text-sm">Remember your cookie consent choice and preferences.</p>
            </div>
          </section>

          {/* Third Party Sharing */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Third-Party Services</h2>
            <p className="text-dark-600 mb-4">We use the following third-party services that may collect data:</p>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Google Analytics</strong> - Website analytics (with consent)</li>
              <li><strong>Vercel</strong> - Website hosting</li>
              <li><strong>Supabase</strong> - Database services</li>
            </ul>
            <p className="text-dark-600 mt-4">
              We do not sell your personal information to third parties.
            </p>
          </section>

          {/* GDPR Rights */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <UserCheck className="w-5 h-5 text-teal-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Your Rights (GDPR/CCPA)</h2>
            </div>

            <p className="text-dark-600 mb-4">
              If you are in the European Economic Area (EEA), UK, or California, you have the following rights:
            </p>

            <ul className="space-y-2 text-dark-600">
              <li><strong>Access</strong> - Request a copy of your personal data</li>
              <li><strong>Rectification</strong> - Request correction of inaccurate data</li>
              <li><strong>Erasure</strong> - Request deletion of your data (&quot;right to be forgotten&quot;)</li>
              <li><strong>Portability</strong> - Request your data in a machine-readable format</li>
              <li><strong>Objection</strong> - Object to processing of your data</li>
              <li><strong>Withdraw consent</strong> - Withdraw previously given consent at any time</li>
            </ul>

            <p className="text-dark-600 mt-4">
              <strong>California residents (CCPA):</strong> You also have the right to know what personal
              information we collect, the right to delete, and the right to opt-out of the sale of
              personal information. We do not sell personal information.
            </p>
          </section>

          {/* Data Retention */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Data Retention</h2>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Newsletter subscriptions:</strong> Until you unsubscribe</li>
              <li><strong>Analytics data:</strong> 26 months (Google Analytics default)</li>
              <li><strong>Server logs:</strong> 30 days</li>
            </ul>
          </section>

          {/* Security */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Data Security</h2>
            <p className="text-dark-600">
              We implement appropriate technical and organizational measures to protect your personal
              information, including encryption in transit (HTTPS) and secure data storage. However,
              no method of transmission over the Internet is 100% secure.
            </p>
          </section>

          {/* Children */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Children&apos;s Privacy</h2>
            <p className="text-dark-600">
              Our website is intended for adults planning family trips. We do not knowingly collect
              personal information from children under 13 (or 16 in the EEA). If you believe we have
              collected such information, please contact us immediately.
            </p>
          </section>

          {/* Contact */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Mail className="w-5 h-5 text-coral-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Contact Us</h2>
            </div>

            <p className="text-dark-600 mb-4">
              For privacy-related inquiries or to exercise your rights, contact us at:
            </p>

            <div className="bg-gradient-to-br from-teal-50 to-mint-50 rounded-2xl p-6 border border-teal-200">
              <p className="text-dark-700">
                <strong>Email:</strong>{' '}
                <a href="mailto:privacy@snowthere.com" className="text-teal-600 hover:underline">
                  privacy@snowthere.com
                </a>
              </p>
            </div>
          </section>

          {/* Changes */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Changes to This Policy</h2>
            <p className="text-dark-600">
              We may update this Privacy Policy from time to time. We will notify you of any changes
              by posting the new Privacy Policy on this page and updating the &quot;Last updated&quot; date.
              We encourage you to review this Privacy Policy periodically.
            </p>
          </section>

        </div>
      </div>

      <Footer />
    </main>
  )
}
