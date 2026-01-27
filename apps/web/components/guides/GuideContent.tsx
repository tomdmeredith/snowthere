'use client'

import Link from 'next/link'
import { Check, ChevronRight, HelpCircle } from 'lucide-react'
import type { GuideSection, GuideListItem, GuideChecklistItem, GuideFAQItem, GuideCTA } from '@/lib/guides'

// =============================================================================
// SECTION RENDERERS
// =============================================================================

function IntroSection({ content }: { content?: string }) {
  if (!content) return null

  return (
    <div className="prose prose-lg max-w-none text-gray-700">
      <div dangerouslySetInnerHTML={{ __html: content }} />
    </div>
  )
}

function TextSection({ title, content }: { title?: string; content?: string }) {
  return (
    <div className="space-y-4">
      {title && (
        <h2 className="font-display text-2xl font-bold text-gray-900">{title}</h2>
      )}
      {content && (
        <div className="prose prose-lg max-w-none text-gray-700">
          <div dangerouslySetInnerHTML={{ __html: content }} />
        </div>
      )}
    </div>
  )
}

function ListSection({ title, items }: { title?: string; items?: GuideListItem[] }) {
  if (!items || items.length === 0) return null

  return (
    <div className="space-y-6">
      {title && (
        <h2 className="font-display text-2xl font-bold text-gray-900">{title}</h2>
      )}
      <div className="space-y-4">
        {items.map((item, idx) => (
          <div
            key={idx}
            className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-4">
              <span className="flex-shrink-0 w-8 h-8 bg-coral-100 text-coral-600 rounded-full flex items-center justify-center font-bold text-sm">
                {idx + 1}
              </span>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">
                  {item.resort_slug ? (
                    <Link
                      href={`/resorts/${item.resort_slug}`}
                      className="hover:text-coral-500 transition-colors"
                    >
                      {item.name}
                    </Link>
                  ) : (
                    item.name
                  )}
                </h3>
                {item.description && (
                  <p className="text-gray-600 text-sm">{item.description}</p>
                )}
              </div>
              {item.resort_slug && (
                <Link
                  href={`/resorts/${item.resort_slug}`}
                  className="flex-shrink-0 text-coral-500 hover:text-coral-600"
                >
                  <ChevronRight className="w-5 h-5" />
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ChecklistSection({ title, items }: { title?: string; items?: GuideChecklistItem[] }) {
  if (!items || items.length === 0) return null

  return (
    <div className="space-y-6">
      {title && (
        <h2 className="font-display text-2xl font-bold text-gray-900">{title}</h2>
      )}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <ul className="space-y-3">
          {items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-3">
              <span className="flex-shrink-0 w-5 h-5 border-2 border-gray-300 rounded flex items-center justify-center mt-0.5">
                {item.checked && <Check className="w-3 h-3 text-green-500" />}
              </span>
              <span className={`text-gray-700 ${item.checked ? 'line-through text-gray-400' : ''}`}>
                {item.text}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function ComparisonTableSection({
  title,
  columns,
  rows,
}: {
  title?: string
  columns?: string[]
  rows?: string[][]
}) {
  if (!columns || !rows || rows.length === 0) return null

  return (
    <div className="space-y-6">
      {title && (
        <h2 className="font-display text-2xl font-bold text-gray-900">{title}</h2>
      )}
      <div className="overflow-x-auto">
        <table className="w-full bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className="px-4 py-3 text-left text-sm font-semibold text-gray-700 border-b border-gray-100"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIdx) => (
              <tr key={rowIdx} className="border-b border-gray-50 last:border-0">
                {row.map((cell, cellIdx) => (
                  <td
                    key={cellIdx}
                    className={`px-4 py-3 text-sm ${
                      cellIdx === 0 ? 'font-medium text-gray-900' : 'text-gray-600'
                    }`}
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function FAQSection({ title, items }: { title?: string; items?: GuideFAQItem[] }) {
  if (!items || items.length === 0) return null

  return (
    <div className="space-y-6">
      {title && (
        <h2 className="font-display text-2xl font-bold text-gray-900 flex items-center gap-2">
          <HelpCircle className="w-6 h-6 text-coral-500" />
          {title}
        </h2>
      )}
      <div className="space-y-4">
        {items.map((item, idx) => (
          <details
            key={idx}
            className="group bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
          >
            <summary className="px-5 py-4 cursor-pointer list-none flex items-center justify-between font-medium text-gray-900 hover:bg-gray-50 transition-colors">
              {item.question}
              <ChevronRight className="w-5 h-5 text-gray-400 group-open:rotate-90 transition-transform" />
            </summary>
            <div className="px-5 pb-4 text-gray-600">
              {item.answer}
            </div>
          </details>
        ))}
      </div>
    </div>
  )
}

function CTASection({ cta }: { cta?: GuideCTA }) {
  if (!cta) return null

  const isPrimary = cta.variant !== 'secondary'

  return (
    <div className="text-center py-8">
      <Link
        href={cta.href}
        className={`inline-flex items-center gap-2 px-8 py-4 rounded-xl font-semibold transition-all ${
          isPrimary
            ? 'bg-gradient-to-r from-coral-500 to-coral-600 text-white shadow-lg hover:shadow-xl hover:shadow-coral-500/25'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        {cta.text}
        <ChevronRight className="w-5 h-5" />
      </Link>
    </div>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

interface GuideContentProps {
  sections: GuideSection[]
}

export function GuideContent({ sections }: GuideContentProps) {
  return (
    <div className="space-y-12">
      {sections.map((section, idx) => {
        switch (section.type) {
          case 'intro':
            return <IntroSection key={idx} content={section.content} />
          case 'text':
            return <TextSection key={idx} title={section.title} content={section.content} />
          case 'list':
            return (
              <ListSection
                key={idx}
                title={section.title}
                items={section.items as GuideListItem[]}
              />
            )
          case 'checklist':
            return (
              <ChecklistSection
                key={idx}
                title={section.title}
                items={section.items as GuideChecklistItem[]}
              />
            )
          case 'comparison_table':
            return (
              <ComparisonTableSection
                key={idx}
                title={section.title}
                columns={section.columns}
                rows={section.rows}
              />
            )
          case 'faq':
            return (
              <FAQSection
                key={idx}
                title={section.title || 'Frequently Asked Questions'}
                items={section.items as GuideFAQItem[]}
              />
            )
          case 'cta':
            return <CTASection key={idx} cta={section.cta} />
          default:
            return null
        }
      })}
    </div>
  )
}
