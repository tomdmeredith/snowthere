import sanitizeHtml from 'sanitize-html'

/**
 * Sanitize HTML content to prevent XSS attacks.
 * Uses sanitize-html with strict configuration suitable for user-generated or AI-generated content.
 */
export function sanitizeHTML(dirty: string): string {
  return sanitizeHtml(dirty, {
    // Allow common formatting tags
    allowedTags: [
      'p', 'br', 'strong', 'em', 'b', 'i', 'u',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li',
      'a', 'span', 'div',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'blockquote', 'code', 'pre',
    ],
    // Only allow safe attributes
    allowedAttributes: {
      'a': ['href', 'target', 'rel', 'class'],
      '*': ['class', 'id'],
      'th': ['colspan', 'rowspan', 'scope'],
      'td': ['colspan', 'rowspan'],
    },
    // Internal links navigate in-place; external links open in new tab
    // Preserves existing rel attributes (e.g., rel="sponsored", rel="nofollow noopener")
    // injected during content generation by external_links.py
    transformTags: {
      'a': (tagName, attribs) => {
        const href = attribs.href || ''
        const isInternal = href.startsWith('/') || href.startsWith('#') || href.includes('snowthere.com')
        if (isInternal) {
          return {
            tagName,
            attribs: { href: attribs.href, ...(attribs.class && { class: attribs.class }) },
          }
        }
        // For external links: preserve existing rel if present, otherwise default
        const existingRel = attribs.rel || ''
        const rel = existingRel
          ? (existingRel.includes('noopener') ? existingRel : `${existingRel} noopener`)
          : 'noopener noreferrer'
        return {
          tagName,
          attribs: { ...attribs, target: '_blank', rel },
        }
      },
    },
    // Don't allow any protocols except http, https, mailto
    allowedSchemes: ['http', 'https', 'mailto'],
    // Remove empty or whitespace-only tags
    exclusiveFilter: (frame) => {
      return !frame.text.trim() && !['br', 'hr'].includes(frame.tag)
    },
  })
}

/**
 * Sanitize content for use in dangerouslySetInnerHTML.
 * Returns an object with __html property.
 */
export function createSanitizedHTML(dirty: string): { __html: string } {
  return { __html: sanitizeHTML(dirty) }
}

/**
 * Sanitize JSON for safe embedding in script tags (Schema.org, etc.)
 * Prevents script injection via JSON content.
 */
export function sanitizeJSON(data: unknown): string {
  return JSON.stringify(data)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026')
}
