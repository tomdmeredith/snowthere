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
    // Force all links to open in new tab with security attributes
    transformTags: {
      'a': (tagName, attribs) => ({
        tagName,
        attribs: {
          ...attribs,
          target: '_blank',
          rel: 'noopener noreferrer',
        },
      }),
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
