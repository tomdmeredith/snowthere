'use client'

import Link from 'next/link'
import { Check, ChevronRight, HelpCircle } from 'lucide-react'
import { sanitizeHTML } from '@/lib/sanitize'
import type { GuideSection, GuideListItem, GuideChecklistItem, GuideFAQItem, GuideCTA } from '@/lib/guides'

// Build correct resort URL using country slug map
function buildResortHref(slug: string, countryMap?: Record<string, string>): string {
  const countrySlug = countryMap?.[slug]
  // Fallback to valid index route when country is unknown.
  return countrySlug ? `/resorts/${countrySlug}/${slug}` : '/resorts'
}

// =============================================================================
// SECTION EMOJI MAPPING
// =============================================================================

function getSectionEmoji(type: string, title?: string): string | null {
  // FAQ and checklist always get their emoji
  if (type === 'faq') return '❓'
  if (type === 'checklist') return '📋'
  if (type === 'comparison_table') return '📊'

  // For text/list sections, match by title keywords
  if (!title) return null
  const t = title.toLowerCase()

  if (t.includes('budget') || t.includes('cost') || t.includes('price') || t.includes('afford')) return '💰'
  if (t.includes('transport') || t.includes('getting') || t.includes('travel') || t.includes('fly') || t.includes('drive')) return '✈️'
  if (t.includes('stay') || t.includes('hotel') || t.includes('lodg') || t.includes('accommodat')) return '🏠'
  if (t.includes('ski') || t.includes('slope') || t.includes('mountain') || t.includes('terrain') || t.includes('snow')) return '⛷️'
  if (t.includes('kid') || t.includes('child') || t.includes('family') || t.includes('toddler') || t.includes('parent')) return '👨‍👩‍👧‍👦'
  if (t.includes('pack') || t.includes('check') || t.includes('essential') || t.includes('gear') || t.includes('bring')) return '✅'
  if (t.includes('eat') || t.includes('food') || t.includes('restaurant') || t.includes('dine') || t.includes('lunch')) return '☕'
  if (t.includes('tip') || t.includes('pro') || t.includes('insider') || t.includes('hack') || t.includes('secret')) return '💡'
  if (t.includes('pass') || t.includes('ticket') || t.includes('lift')) return '🎟️'
  if (t.includes('itinerar') || t.includes('day') || t.includes('schedule') || t.includes('plan')) return '📅'
  if (t.includes('best') || t.includes('top') || t.includes('recommend')) return '🎯'
  if (t.includes('olympic') || t.includes('event') || t.includes('competition')) return '🏅'
  if (t.includes('safe') || t.includes('warn') || t.includes('important')) return '⚠️'

  return null
}

// Section header with optional emoji
function SectionHeader({ title, type }: { title: string; type: string }) {
  const emoji = getSectionEmoji(type, title)

  return (
    <h2 className="font-display text-2xl font-bold text-gray-900 flex items-center gap-3">
      {emoji && <span aria-hidden="true">{emoji}</span>}
      <span>{title}</span>
    </h2>
  )
}

// =============================================================================
// SECTION RENDERERS
// =============================================================================

function IntroSection({ content }: { content?: string }) {
  if (!content) return null

  return (
    <div className="prose prose-lg max-w-none text-gray-700">
      <div dangerouslySetInnerHTML={{ __html: sanitizeHTML(content) }} />
    </div>
  )
}

function TextSection({ title, content }: { title?: string; content?: string }) {
  return (
    <div className="space-y-4">
      {title && <SectionHeader title={title} type="text" />}
      {content && (
        <div className="prose prose-lg max-w-none text-gray-700">
          <div dangerouslySetInnerHTML={{ __html: sanitizeHTML(content) }} />
        </div>
      )}
    </div>
  )
}

function ListSection({ title, items, resortCountryMap }: { title?: string; items?: GuideListItem[]; resortCountryMap?: Record<string, string> }) {
  if (!items || items.length === 0) return null

  return (
    <div className="space-y-6">
      {title && <SectionHeader title={title} type="list" />}
      <div className="space-y-4">
        {items.map((item, idx) => {
          const isOdd = idx % 2 === 0
          return (
            <div
              key={idx}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:shadow-md hover:scale-[1.01] transition-all duration-200"
              style={{
                boxShadow: undefined,
              }}
            >
              <div className="flex items-start gap-4">
                <span
                  className={`flex-shrink-0 w-9 h-9 ${
                    isOdd
                      ? 'bg-coral-100 text-coral-600'
                      : 'bg-teal-100 text-teal-600'
                  } rounded-full flex items-center justify-center font-bold text-sm`}
                >
                  {idx + 1}
                </span>
                <div className="flex-1">
                  <h3 className="font-display font-semibold text-gray-900 mb-1">
                    {item.resort_slug ? (
                      <Link
                        href={buildResortHref(item.resort_slug, resortCountryMap)}
                        className="hover:text-coral-500 transition-colors"
                      >
                        {item.name}
                      </Link>
                    ) : (
                      item.name
                    )}
                  </h3>
                  {item.description && (
                    <div
                      className="text-gray-600 text-sm prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: sanitizeHTML(item.description) }}
                    />
                  )}
                </div>
                {item.resort_slug && (
                  <Link
                    href={buildResortHref(item.resort_slug, resortCountryMap)}
                    className="flex-shrink-0 text-coral-500 hover:text-coral-600 mt-1"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </Link>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function ChecklistSection({ title, items }: { title?: string; items?: GuideChecklistItem[] }) {
  if (!items || items.length === 0) return null

  return (
    <div className="space-y-6">
      {title && <SectionHeader title={title} type="checklist" />}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <ul className="space-y-3">
          {items.map((item, idx) => (
            <li key={idx} className="flex items-start gap-3">
              <span className={`flex-shrink-0 w-5 h-5 rounded flex items-center justify-center mt-0.5 ${
                item.checked
                  ? 'bg-teal-100 border-2 border-teal-400'
                  : 'border-2 border-gray-300'
              }`}>
                {item.checked && <Check className="w-3 h-3 text-teal-600" />}
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
      {title && <SectionHeader title={title} type="comparison_table" />}
      <div className="overflow-x-auto rounded-2xl shadow-sm border border-gray-100">
        <table className="w-full bg-white overflow-hidden">
          <thead>
            <tr className="bg-gradient-to-r from-coral-500 to-teal-500">
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className="px-4 py-3 text-left text-sm font-semibold text-white"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className={`border-b border-gray-50 last:border-0 ${
                  rowIdx % 2 === 1 ? 'bg-gray-50/60' : ''
                }`}
              >
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
      {title && <SectionHeader title={title} type="faq" />}
      <div className="space-y-3">
        {items.map((item, idx) => (
          <details
            key={idx}
            className="group bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden"
          >
            <summary className="px-5 py-4 cursor-pointer list-none flex items-center justify-between font-medium text-gray-900 hover:bg-gray-50 transition-colors">
              {item.question}
              <ChevronRight className="w-5 h-5 text-gray-400 group-open:rotate-90 transition-transform flex-shrink-0 ml-2" />
            </summary>
            <div
              className="px-5 pb-4 text-gray-600 prose prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: sanitizeHTML(item.answer) }}
            />
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
        className={`inline-flex items-center gap-2 px-8 py-4 rounded-full font-semibold transition-all ${
          isPrimary
            ? 'bg-gradient-to-r from-coral-500 to-coral-600 text-white shadow-lg hover:shadow-xl hover:shadow-coral-500/25 hover:scale-105'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        {cta.text}
        <ChevronRight className="w-5 h-5" />
      </Link>
    </div>
  )
}

function ImageSection({ section }: { section: GuideSection }) {
  if (!section.image_url) return null

  return (
    <figure className="my-8">
      <div className="rounded-2xl overflow-hidden shadow-lg">
        <img
          src={section.image_url}
          alt={section.alt_text || ''}
          className="w-full h-auto"
          loading="lazy"
        />
      </div>
      {section.caption && (
        <figcaption className="text-center text-sm text-gray-500 mt-3 italic font-sans">
          {section.caption}
        </figcaption>
      )}
    </figure>
  )
}

function CalloutSection({ section }: { section: GuideSection }) {
  const variant = section.variant || 'tip'

  const styles = {
    tip: {
      bg: 'bg-amber-50/80',
      border: 'border-amber-300',
      titleColor: 'text-amber-800',
      emoji: '💡',
      label: 'PRO TIP',
    },
    warning: {
      bg: 'bg-coral-50/80',
      border: 'border-coral-300',
      titleColor: 'text-coral-800',
      emoji: '⚠️',
      label: 'HEADS UP',
    },
    celebration: {
      bg: 'bg-teal-50/80',
      border: 'border-teal-300',
      titleColor: 'text-teal-800',
      emoji: '🎉',
      label: 'GREAT NEWS',
    },
  }

  const s = styles[variant] || styles.tip

  return (
    <div className={`${s.bg} border-2 ${s.border} rounded-2xl p-5`}>
      <span className={`font-display font-semibold ${s.titleColor} text-sm`}>
        {s.emoji} {section.title || s.label}
      </span>
      {section.content && (
        <div
          className="mt-2 prose prose-sm max-w-none text-gray-700"
          dangerouslySetInnerHTML={{ __html: sanitizeHTML(section.content) }}
        />
      )}
    </div>
  )
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

interface GuideContentProps {
  sections: GuideSection[]
  resortCountryMap?: Record<string, string>
}

export function GuideContent({ sections, resortCountryMap }: GuideContentProps) {
  return (
    <div className="space-y-10">
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
                resortCountryMap={resortCountryMap}
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
          case 'image':
            return <ImageSection key={idx} section={section} />
          case 'callout':
            return <CalloutSection key={idx} section={section} />
          default:
            return null
        }
      })}
    </div>
  )
}
