import { Metadata } from 'next'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight, FileText, AlertTriangle, Scale, Bot } from 'lucide-react'

export const metadata: Metadata = {
  title: 'Terms of Service',
  description: 'Terms and conditions for using Snowthere. Read about our disclaimers, AI-generated content disclosure, and user responsibilities.',
}

export default function TermsPage() {
  const lastUpdated = 'January 22, 2026'

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
            <li className="text-dark-800 font-medium">Terms of Service</li>
          </ol>
        </div>
      </nav>

      {/* Header */}
      <header className="py-16 bg-gradient-to-br from-coral-50 to-white">
        <div className="container-page">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-coral-50 shadow-coral">
              <FileText className="w-6 h-6 text-coral-600" />
            </div>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-dark-800">
              Terms of Service
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
              Welcome to Snowthere. By accessing or using our website (snowthere.com), you agree to be
              bound by these Terms of Service. If you do not agree with any part of these terms,
              please do not use our website.
            </p>
          </section>

          {/* AI Content Disclosure - CRITICAL */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Bot className="w-5 h-5 text-coral-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">AI-Generated Content Disclosure</h2>
            </div>

            <div className="bg-gradient-to-br from-coral-50 to-gold-50 rounded-2xl p-6 border-2 border-coral-200 mb-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-coral-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="text-dark-800 font-semibold mb-2">Important Notice</p>
                  <p className="text-dark-600">
                    The resort guides, descriptions, pricing estimates, and recommendations on Snowthere
                    are generated using artificial intelligence (AI) technology. While we strive for
                    accuracy and have quality review processes in place, AI-generated content may
                    contain errors, outdated information, or inaccuracies.
                  </p>
                </div>
              </div>
            </div>

            <h3 className="font-display text-xl font-semibold text-dark-700 mt-6 mb-3">What This Means for You</h3>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Pricing:</strong> All prices are estimates and may not reflect current rates. Always verify directly with resorts, hotels, and lift ticket providers before booking.</li>
              <li><strong>Facilities:</strong> Information about ski schools, childcare, restaurants, and other amenities may have changed. Verify availability before traveling.</li>
              <li><strong>Recommendations:</strong> Our &quot;Perfect if&quot; and &quot;Skip if&quot; suggestions are based on AI analysis and may not apply to your specific situation.</li>
              <li><strong>Safety:</strong> Never rely solely on our guides for safety-critical information. Check official resort websites and local authorities.</li>
            </ul>
          </section>

          {/* Disclaimer of Warranties */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className="w-5 h-5 text-gold-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Disclaimer of Warranties</h2>
            </div>

            <p className="text-dark-600 mb-4">
              THE WEBSITE AND ALL CONTENT ARE PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES
              OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
            </p>

            <ul className="space-y-2 text-dark-600">
              <li>Implied warranties of merchantability</li>
              <li>Fitness for a particular purpose</li>
              <li>Non-infringement</li>
              <li>Accuracy, completeness, or reliability of content</li>
              <li>Availability or uninterrupted access</li>
            </ul>

            <p className="text-dark-600 mt-4">
              We do not warrant that the information on this website is accurate, complete, reliable,
              current, or error-free. Ski conditions, prices, and resort operations can change rapidly
              and without notice.
            </p>
          </section>

          {/* Limitation of Liability */}
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Scale className="w-5 h-5 text-teal-600" />
              <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Limitation of Liability</h2>
            </div>

            <p className="text-dark-600 mb-4">
              TO THE FULLEST EXTENT PERMITTED BY LAW, SNOWTHERE AND ITS OWNERS, OPERATORS, EMPLOYEES,
              AND AFFILIATES SHALL NOT BE LIABLE FOR:
            </p>

            <ul className="space-y-2 text-dark-600">
              <li>Any indirect, incidental, special, consequential, or punitive damages</li>
              <li>Loss of profits, revenue, data, or business opportunities</li>
              <li>Personal injury or property damage arising from your travel</li>
              <li>Reliance on information provided on this website</li>
              <li>Booking decisions made based on our content</li>
              <li>Third-party products, services, or websites linked from our site</li>
            </ul>

            <p className="text-dark-600 mt-4">
              OUR TOTAL LIABILITY FOR ANY CLAIMS ARISING FROM YOUR USE OF THE WEBSITE SHALL NOT
              EXCEED THE AMOUNT YOU PAID US IN THE PAST 12 MONTHS (WHICH, FOR FREE SERVICES, IS ZERO).
            </p>
          </section>

          {/* User Responsibilities */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Your Responsibilities</h2>
            <p className="text-dark-600 mb-4">By using Snowthere, you agree to:</p>
            <ul className="space-y-2 text-dark-600">
              <li>Verify all information with official sources before making travel decisions</li>
              <li>Not rely solely on our guides for safety-critical decisions</li>
              <li>Check current conditions, prices, and availability directly with providers</li>
              <li>Maintain appropriate travel insurance</li>
              <li>Use the website lawfully and not for any illegal purpose</li>
              <li>Not scrape, copy, or redistribute our content without permission</li>
            </ul>
          </section>

          {/* Trademark Notice */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Trademark Notice</h2>
            <p className="text-dark-600 mb-4">
              The following are trademarks of their respective owners, and Snowthere is not
              affiliated with, endorsed by, or sponsored by these companies:
            </p>

            <h3 className="font-display text-lg font-semibold text-dark-700 mt-6 mb-3">Multi-Resort Passes</h3>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Epic Pass</strong> and <strong>Epic Local Pass</strong> are trademarks of Vail Resorts, Inc.</li>
              <li><strong>Ikon Pass</strong> and <strong>Ikon Base Pass</strong> are trademarks of Alterra Mountain Company.</li>
              <li><strong>Mountain Collective</strong> is a trademark of Mountain Collective, LLC.</li>
              <li><strong>Indy Pass</strong> is a trademark of Indy Pass, LLC.</li>
            </ul>

            <h3 className="font-display text-lg font-semibold text-dark-700 mt-6 mb-3">European Regional Passes</h3>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Dolomiti Superski</strong> is a trademark of Dolomiti Superski Consortium.</li>
              <li><strong>Portes du Soleil</strong> is a trademark of Association Portes du Soleil.</li>
              <li><strong>Les 3 Vallées</strong> is a trademark of SETAM / Les 3 Vallées.</li>
              <li><strong>Paradiski</strong> is a trademark of Compagnie des Alpes.</li>
              <li><strong>4 Vallées</strong> is a trademark of Téléverbier SA.</li>
              <li><strong>Ski Arlberg</strong> is a trademark of Ski Arlberg Ski Pool.</li>
              <li><strong>SkiWelt Wilder Kaiser-Brixental</strong> is a trademark of SkiWelt.</li>
              <li><strong>Zermatt-Cervinia</strong> is a trademark of Zermatt Bergbahnen AG and Cervino S.p.A.</li>
            </ul>

            <h3 className="font-display text-lg font-semibold text-dark-700 mt-6 mb-3">North American Regional Passes</h3>
            <ul className="space-y-2 text-dark-600">
              <li><strong>Ski Big 3</strong> is a trademark of Banff &amp; Lake Louise Tourism.</li>
              <li><strong>Ski Utah Interconnect</strong> is a trademark of Ski Utah.</li>
              <li><strong>New England Pass</strong> is a trademark of Peak Resorts / Vail Resorts.</li>
            </ul>

            <p className="text-dark-600 mt-6">
              All resort names, logos, and related marks are trademarks of their respective owners.
              Reference to these marks is for informational purposes only and does not imply
              endorsement or affiliation.
            </p>
          </section>

          {/* Intellectual Property */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Intellectual Property</h2>
            <p className="text-dark-600 mb-4">
              Unless otherwise noted, all content on Snowthere, including text, graphics, logos,
              images, and software, is the property of Snowthere or its content suppliers and is
              protected by intellectual property laws.
            </p>
            <p className="text-dark-600">
              You may not reproduce, distribute, modify, or create derivative works from our content
              without our express written permission. Limited personal, non-commercial use (such as
              printing a guide for your trip) is permitted.
            </p>
          </section>

          {/* Third-Party Links */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Third-Party Links</h2>
            <p className="text-dark-600">
              Our website may contain links to third-party websites (resorts, booking platforms, etc.).
              We are not responsible for the content, accuracy, or practices of these external sites.
              Inclusion of a link does not imply endorsement. Your use of third-party websites is at
              your own risk and subject to their terms and policies.
            </p>
          </section>

          {/* Newsletter */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Newsletter and Communications</h2>
            <p className="text-dark-600 mb-4">
              By subscribing to our newsletter, you consent to receive periodic emails about ski
              destinations, deals, and tips. You may unsubscribe at any time by clicking the
              unsubscribe link in any email or contacting us.
            </p>
            <p className="text-dark-600">
              We comply with the CAN-SPAM Act and similar regulations. Our emails will always include
              our identity and a clear unsubscribe mechanism.
            </p>
          </section>

          {/* Indemnification */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Indemnification</h2>
            <p className="text-dark-600">
              You agree to indemnify and hold harmless Snowthere and its owners, employees, and
              affiliates from any claims, damages, losses, or expenses (including legal fees) arising
              from your use of the website or violation of these terms.
            </p>
          </section>

          {/* Governing Law */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Governing Law</h2>
            <p className="text-dark-600">
              These Terms of Service shall be governed by and construed in accordance with the laws
              of the State of California, United States, without regard to its conflict of law
              provisions. Any disputes shall be resolved in the courts of California.
            </p>
          </section>

          {/* Changes */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Changes to Terms</h2>
            <p className="text-dark-600">
              We reserve the right to modify these Terms of Service at any time. Changes will be
              effective immediately upon posting. Your continued use of the website after changes
              constitutes acceptance of the new terms.
            </p>
          </section>

          {/* Contact */}
          <section className="mb-12">
            <h2 className="font-display text-2xl font-bold text-dark-800 mb-4">Contact Us</h2>
            <p className="text-dark-600 mb-4">
              If you have questions about these Terms of Service, please contact us at:
            </p>
            <div className="bg-gradient-to-br from-coral-50 to-gold-50 rounded-2xl p-6 border border-coral-200">
              <p className="text-dark-700">
                <strong>Email:</strong>{' '}
                <a href="mailto:legal@snowthere.com" className="text-coral-600 hover:underline">
                  legal@snowthere.com
                </a>
              </p>
            </div>
          </section>

        </div>
      </div>

      <Footer />
    </main>
  )
}
