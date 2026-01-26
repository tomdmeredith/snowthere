import { Metadata } from 'next'
import Link from 'next/link'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/home/Footer'
import { ChevronRight, Mail, MessageSquare, Clock, Building2 } from 'lucide-react'
import { ContactForm } from '@/components/ContactForm'

export const metadata: Metadata = {
  title: 'Contact Us | Snowthere',
  description: 'Get in touch with the Snowthere team. Questions about a resort, feedback on our guides, or partnership inquiries - we\'d love to hear from you.',
}

export default function ContactPage() {
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
            <li className="text-dark-800 font-medium">Contact</li>
          </ol>
        </div>
      </nav>

      {/* Header */}
      <header className="py-16 bg-gradient-to-br from-coral-50 to-white">
        <div className="container-page">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-coral-100 to-peach-100 shadow-coral">
              <Mail className="w-6 h-6 text-coral-600" />
            </div>
            <h1 className="font-display text-4xl sm:text-5xl font-bold text-dark-800">
              Contact Us
            </h1>
          </div>
          <p className="text-xl text-dark-600 mt-4 max-w-2xl">
            Have a question, suggestion, or just want to say hi? We&apos;d love to hear from you.
          </p>
        </div>
      </header>

      {/* Content */}
      <div className="container-page py-12">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-5 gap-12">

            {/* Contact Form */}
            <div className="md:col-span-3">
              <div className="flex items-center gap-3 mb-6">
                <MessageSquare className="w-5 h-5 text-coral-600" />
                <h2 className="font-display text-2xl font-bold text-dark-800 m-0">Send Us a Message</h2>
              </div>
              <ContactForm />
            </div>

            {/* Sidebar */}
            <div className="md:col-span-2 space-y-8">

              {/* Response Time */}
              <div className="bg-gradient-to-br from-teal-50 to-mint-50 rounded-2xl p-6 border border-teal-200">
                <div className="flex items-center gap-3 mb-3">
                  <Clock className="w-5 h-5 text-teal-600" />
                  <h3 className="font-semibold text-dark-800 m-0">Response Time</h3>
                </div>
                <p className="text-dark-600 text-sm">
                  We typically respond within 24-48 hours. During ski season (November-April),
                  we may be a bit slower - we&apos;re probably on the slopes!
                </p>
              </div>

              {/* What We Can Help With */}
              <div className="bg-dark-50 rounded-2xl p-6">
                <h3 className="font-semibold text-dark-800 mb-4">We Can Help With</h3>
                <ul className="space-y-3 text-dark-600 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-coral-500 mt-1">•</span>
                    <span>Questions about specific resorts</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-coral-500 mt-1">•</span>
                    <span>Suggestions for resorts we should cover</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-coral-500 mt-1">•</span>
                    <span>Feedback on our guides</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-coral-500 mt-1">•</span>
                    <span>Corrections or updates to resort info</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-coral-500 mt-1">•</span>
                    <span>General questions about family skiing</span>
                  </li>
                </ul>
              </div>

              {/* Business Inquiries */}
              <div className="bg-dark-50 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-3">
                  <Building2 className="w-5 h-5 text-teal-600" />
                  <h3 className="font-semibold text-dark-800 m-0">Business Inquiries</h3>
                </div>
                <p className="text-dark-600 text-sm mb-4">
                  For partnership opportunities, advertising, or press inquiries:
                </p>
                <a
                  href="mailto:hello@snowthere.com"
                  className="text-teal-600 hover:underline text-sm font-medium"
                >
                  hello@snowthere.com
                </a>
              </div>

            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}
