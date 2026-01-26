'use client'

import { useMemo } from 'react'
import { ProTipCallout } from './ProTipCallout'
import { WarningCallout } from './WarningCallout'

interface ContentRendererProps {
  /** HTML content - must be pre-sanitized server-side via lib/sanitize.ts */
  html: string
  className?: string
}

interface ParsedContent {
  type: 'html' | 'pro_tip' | 'warning'
  content: string
}

/**
 * Renders HTML content with automatic extraction of Pro Tips and Warnings
 * into visual callout components.
 *
 * IMPORTANT: Content must be sanitized server-side before passing to this component.
 * Use sanitizeHTML() from lib/sanitize.ts in server components/pages.
 *
 * Detects patterns like:
 * - "Pro tip:" or "Pro Tip:" followed by text
 * - "Warning:" or "Heads up:" followed by text
 * - "Real talk:" followed by text
 */
export function ContentRenderer({ html, className = 'prose-family' }: ContentRendererProps) {
  const parsedContent = useMemo(() => {
    // Content is pre-sanitized server-side - just use it directly
    const sanitized = html

    // Split content by paragraph tags and strong/bold patterns
    const segments: ParsedContent[] = []
    let remaining = sanitized

    // Pattern to match callout markers
    // Looks for <p> or <strong> containing Pro tip:, Warning:, etc.
    const calloutPattern = /<p>(?:<strong>)?(Pro [Tt]ip|Warning|Heads [Uu]p|Real [Tt]alk):?\s*(?:<\/strong>)?\s*(.*?)<\/p>/gi

    let lastIndex = 0
    let match

    while ((match = calloutPattern.exec(sanitized)) !== null) {
      // Add any HTML before this match
      if (match.index > lastIndex) {
        const beforeHtml = sanitized.slice(lastIndex, match.index)
        if (beforeHtml.trim()) {
          segments.push({ type: 'html', content: beforeHtml })
        }
      }

      // Determine callout type
      const marker = match[1].toLowerCase()
      const content = match[2].trim()

      if (marker.includes('pro') || marker.includes('tip')) {
        segments.push({ type: 'pro_tip', content })
      } else if (marker.includes('warning') || marker.includes('heads') || marker.includes('real')) {
        segments.push({ type: 'warning', content })
      }

      lastIndex = match.index + match[0].length
    }

    // Add any remaining HTML
    if (lastIndex < sanitized.length) {
      const afterHtml = sanitized.slice(lastIndex)
      if (afterHtml.trim()) {
        segments.push({ type: 'html', content: afterHtml })
      }
    }

    // If no callouts found, return original
    if (segments.length === 0) {
      return [{ type: 'html' as const, content: sanitized }]
    }

    return segments
  }, [html])

  return (
    <div className={className}>
      {parsedContent.map((segment, index) => {
        if (segment.type === 'pro_tip') {
          return (
            <ProTipCallout key={index}>
              <span dangerouslySetInnerHTML={{ __html: segment.content }} />
            </ProTipCallout>
          )
        }

        if (segment.type === 'warning') {
          return (
            <WarningCallout key={index}>
              <span dangerouslySetInnerHTML={{ __html: segment.content }} />
            </WarningCallout>
          )
        }

        return (
          <div key={index} dangerouslySetInnerHTML={{ __html: segment.content }} />
        )
      })}
    </div>
  )
}
