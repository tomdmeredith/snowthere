'use client'

import { useState } from 'react'
import { ChevronDown, MessageCircleQuestion } from 'lucide-react'

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
    <section id="faq" className="space-y-6">
      {/* Editorial Header */}
      <div className="flex items-center gap-3">
        <div className="p-2.5 rounded-2xl bg-pine-50 border border-pine-100">
          <MessageCircleQuestion className="w-5 h-5 text-pine-600" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="h-px w-4 bg-pine-300" />
            <h2 className="font-display text-2xl font-semibold text-espresso-900">
              Common Questions
            </h2>
          </div>
          <p className="text-sm text-espresso-500 mt-0.5">Everything families ask about this resort</p>
        </div>
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
              className={`card bg-ivory-50/70 border-ivory-100 overflow-hidden transition-all duration-200 ${
                isOpen ? 'ring-2 ring-pine-200 bg-white' : 'hover:bg-white'
              }`}
            >
              <button
                onClick={() => setOpenIndex(isOpen ? null : index)}
                className="w-full flex items-start justify-between text-left gap-4"
                aria-expanded={isOpen}
              >
                <span className="font-display font-medium text-espresso-900 leading-relaxed">
                  {faq.question}
                </span>
                <span
                  className={`flex-shrink-0 p-1.5 rounded-xl transition-all duration-200 ${
                    isOpen
                      ? 'bg-pine-100 text-pine-600 rotate-180'
                      : 'bg-ivory-100 text-espresso-400'
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
                  <div className="pt-4 border-t border-pine-100">
                    <div
                      className="text-espresso-600 leading-relaxed [&>p]:mb-3 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-4 [&>ul]:space-y-1.5 [&>ul]:text-espresso-600"
                      dangerouslySetInnerHTML={{ __html: faq.answer }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Softer suggestion */}
      <p className="mt-8 text-espresso-400 text-sm text-center italic">
        Have a question we didn&apos;t cover? We&apos;d love to add it to our guide.
      </p>
    </section>
  )
}
