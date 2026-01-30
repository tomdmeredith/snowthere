'use client'

import { useState } from 'react'
import { ChevronDown, MessageCircleQuestion } from 'lucide-react'
import { createSanitizedHTML } from '@/lib/sanitize'

interface FAQ {
  question: string
  answer: string
}

interface FAQSectionProps {
  faqs: FAQ[]
}

export function FAQSection({ faqs }: FAQSectionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <section id="faq" className="space-y-8">
      {/* Editorial Header - Design-5 */}
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-100 to-mint-100 border border-teal-200 shadow-teal">
          <MessageCircleQuestion className="w-6 h-6 text-teal-600" />
        </div>
        <div>
          <div className="flex items-center gap-3">
            <span className="h-1 w-6 bg-gradient-to-r from-teal-400 to-teal-500 rounded-full" />
            <h2 className="font-display text-3xl font-bold text-dark-800">
              Common Questions
            </h2>
          </div>
          <p className="text-dark-500 mt-1 font-medium">Everything families ask about this resort</p>
        </div>
      </div>

      {/* Design-5: Playful accordion cards */}
      <div className="space-y-4">
        {faqs.map((faq, index) => {
          const isOpen = openIndex === index
          const panelId = `faq-panel-${index}`
          const headingId = `faq-heading-${index}`
          return (
            <div
              key={index}
              className={`rounded-3xl overflow-hidden transition-all duration-300 ${
                isOpen
                  ? 'bg-white border-2 border-teal-300 shadow-teal'
                  : 'bg-gradient-to-br from-dark-50/80 to-white border border-dark-100 shadow-card hover:shadow-card-hover hover:border-teal-200'
              }`}
            >
              <h3 className="m-0">
                <button
                  id={headingId}
                  onClick={() => setOpenIndex(isOpen ? null : index)}
                  className="w-full flex items-start justify-between text-left gap-4 p-6"
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                >
                  <span className={`font-display font-semibold leading-relaxed transition-colors duration-300 ${
                    isOpen ? 'text-teal-700' : 'text-dark-800'
                  }`}>
                    {faq.question}
                  </span>
                  <span
                    aria-hidden="true"
                    className={`flex-shrink-0 p-2 rounded-xl transition-all duration-300 ${
                      isOpen
                        ? 'bg-gradient-to-br from-teal-400 to-teal-500 text-white rotate-180 shadow-teal'
                        : 'bg-dark-100 text-dark-500 hover:bg-teal-100 hover:text-teal-600'
                    }`}
                  >
                    <ChevronDown className="w-5 h-5" />
                  </span>
                </button>
              </h3>

              <div
                id={panelId}
                role="region"
                aria-labelledby={headingId}
                className={`grid transition-all duration-300 ease-out ${
                  isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                }`}
              >
                <div className="overflow-hidden">
                  <div className="px-6 pb-6 pt-2 border-t border-teal-200 mx-4 mb-2">
                    <div
                      className="text-dark-600 leading-relaxed [&>p]:mb-3 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:space-y-2 [&>ul]:text-dark-600 [&>strong]:text-dark-700 [&>strong]:font-semibold"
                      dangerouslySetInnerHTML={createSanitizedHTML(faq.answer)}
                    />
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Softer suggestion */}
      <p className="mt-8 text-dark-400 text-sm text-center italic">
        Have a question we didn&apos;t cover? We&apos;d love to add it to our guide.
      </p>
    </section>
  )
}
