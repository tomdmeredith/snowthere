'use client'

import { useState } from 'react'
import { ChevronDown, HelpCircle } from 'lucide-react'

interface FAQ {
  question: string
  answer: string
}

interface FAQSectionProps {
  faqs: FAQ[]
}

export function FAQSection({ faqs }: FAQSectionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  // Generate FAQ Schema.org markup
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  }

  return (
    <section id="faq">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-xl bg-glow-100">
          <HelpCircle className="w-5 h-5 text-glow-600" />
        </div>
        <h2 className="font-display text-2xl font-semibold text-slate-900">
          Frequently Asked Questions
        </h2>
      </div>

      {/* Schema.org structured data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
      />

      <div className="space-y-3">
        {faqs.map((faq, index) => {
          const isOpen = openIndex === index
          return (
            <div
              key={index}
              className={`card overflow-hidden transition-all duration-200 ${
                isOpen ? 'ring-2 ring-glow-200' : ''
              }`}
            >
              <button
                onClick={() => setOpenIndex(isOpen ? null : index)}
                className="w-full flex items-start justify-between text-left"
                aria-expanded={isOpen}
              >
                <span className="font-display font-medium text-slate-900 pr-4 leading-relaxed">
                  {faq.question}
                </span>
                <span
                  className={`flex-shrink-0 p-1 rounded-full transition-all duration-200 ${
                    isOpen
                      ? 'bg-glow-100 text-glow-600 rotate-180'
                      : 'bg-cream-100 text-slate-400'
                  }`}
                >
                  <ChevronDown className="w-4 h-4" />
                </span>
              </button>

              <div
                className={`grid transition-all duration-200 ${
                  isOpen ? 'grid-rows-[1fr] opacity-100 mt-4' : 'grid-rows-[0fr] opacity-0'
                }`}
              >
                <div className="overflow-hidden">
                  <div className="pt-4 border-t border-cream-200">
                    <div
                      className="text-slate-700 prose-sm leading-relaxed [&>p]:mb-3 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-4 [&>ul]:space-y-1"
                      dangerouslySetInnerHTML={{ __html: faq.answer }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Pro tip */}
      <div className="pro-tip mt-6">
        <span className="pro-tip-label">Pro tip:</span>
        <p className="text-slate-700 text-sm">
          Have a question we didn&apos;t answer? Reach out and we&apos;ll add it to our guide!
        </p>
      </div>
    </section>
  )
}
