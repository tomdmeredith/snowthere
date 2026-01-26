'use client'

import { ExternalLink } from 'lucide-react'
import { trackOutboundClick } from '@/lib/analytics'

interface ResortLink {
  id: string
  title: string
  url: string
  category: string
  description?: string
  is_affiliate?: boolean
  affiliate_url?: string
}

interface UsefulLinksProps {
  links: ResortLink[]
  resortSlug: string
}

const CATEGORY_CONFIG: Record<string, { label: string; emoji: string }> = {
  official: { label: 'Official', emoji: '🌐' },
  lodging: { label: 'Stay', emoji: '🏨' },
  dining: { label: 'Eat', emoji: '🍽️' },
  activity: { label: 'Do', emoji: '🎿' },
  transport: { label: 'Travel', emoji: '✈️' },
  rental: { label: 'Rent', emoji: '🎿' },
  ski_school: { label: 'Learn', emoji: '👨‍🏫' },
  childcare: { label: 'Kids', emoji: '👶' },
}

function addUtmParams(url: string, resortSlug: string, category: string): string {
  try {
    const urlObj = new URL(url)
    urlObj.searchParams.set('utm_source', 'snowthere')
    urlObj.searchParams.set('utm_medium', 'resort_page')
    urlObj.searchParams.set('utm_campaign', resortSlug)
    urlObj.searchParams.set('utm_content', category)
    return urlObj.toString()
  } catch {
    // If URL parsing fails, return original
    return url
  }
}

export function UsefulLinks({ links, resortSlug }: UsefulLinksProps) {
  if (!links || links.length === 0) return null

  // Group links by category
  const groupedLinks = links.reduce((acc, link) => {
    const category = link.category || 'other'
    if (!acc[category]) acc[category] = []
    acc[category].push(link)
    return acc
  }, {} as Record<string, ResortLink[]>)

  // Priority order for categories
  const categoryOrder = ['official', 'lodging', 'ski_school', 'childcare', 'activity', 'dining', 'rental', 'transport']

  const sortedCategories = Object.keys(groupedLinks).sort((a, b) => {
    const aIndex = categoryOrder.indexOf(a)
    const bIndex = categoryOrder.indexOf(b)
    if (aIndex === -1 && bIndex === -1) return 0
    if (aIndex === -1) return 1
    if (bIndex === -1) return -1
    return aIndex - bIndex
  })

  return (
    <section id="useful-links" className="space-y-5">
      <h2 className="font-display text-xl font-bold text-dark-800 flex items-center gap-2">
        <span>🔗</span>
        <span>Useful Links</span>
      </h2>

      <div className="space-y-4">
        {sortedCategories.map((category) => {
          const config = CATEGORY_CONFIG[category] || { label: category, emoji: '🔗' }
          const categoryLinks = groupedLinks[category]

          return (
            <div key={category}>
              <h3 className="text-xs font-semibold text-dark-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <span>{config.emoji}</span>
                <span>{config.label}</span>
              </h3>
              <div className="space-y-2">
                {categoryLinks.map((link) => {
                  const targetUrl = link.is_affiliate && link.affiliate_url
                    ? link.affiliate_url
                    : addUtmParams(link.url, resortSlug, category)

                  return (
                    <a
                      key={link.id}
                      href={targetUrl}
                      target="_blank"
                      rel={link.is_affiliate ? 'noopener sponsored' : 'noopener noreferrer'}
                      className="flex items-center justify-between p-3 rounded-xl bg-white border border-dark-100 hover:border-coral-200 hover:bg-coral-50/30 transition-all group"
                      onClick={() => {
                        trackOutboundClick({
                          url: targetUrl,
                          linkText: link.title,
                          category,
                          isAffiliate: link.is_affiliate ?? false,
                          affiliateProgram: link.is_affiliate ? 'booking.com' : undefined, // TODO: Add affiliate_program to link data
                          resortSlug,
                        })
                      }}
                    >
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-dark-800 group-hover:text-coral-600 transition-colors truncate">
                          {link.title}
                        </p>
                        {link.description && (
                          <p className="text-xs text-dark-500 truncate">{link.description}</p>
                        )}
                      </div>
                      <ExternalLink className="w-4 h-4 text-dark-400 group-hover:text-coral-500 flex-shrink-0 ml-2 transition-colors" />
                    </a>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>

      {/* Attribution note for affiliate links */}
      {links.some(l => l.is_affiliate) && (
        <p className="text-xs text-dark-400 italic">
          Some links may earn us a commission at no extra cost to you.
        </p>
      )}
    </section>
  )
}
