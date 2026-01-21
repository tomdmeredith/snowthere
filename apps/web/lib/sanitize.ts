import DOMPurify from 'isomorphic-dompurify'

// Configure DOMPurify hook to add security attributes to links
// This runs once when the module is loaded
DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A') {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener noreferrer')
  }
})

/**
 * Sanitize HTML content to prevent XSS attacks.
 * Uses DOMPurify with strict configuration suitable for user-generated or AI-generated content.
 */
export function sanitizeHTML(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    // Allow common formatting tags
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'b', 'i', 'u',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li',
      'a', 'span', 'div',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
      'blockquote', 'code', 'pre',
    ],
    // Only allow safe attributes
    ALLOWED_ATTR: [
      'href', 'target', 'rel', 'class', 'id',
      'colspan', 'rowspan', 'scope',
    ],
    // Force all links to open in new tab with security attributes
    ADD_ATTR: ['target', 'rel'],
    // Enforce noopener noreferrer on links
    FORBID_ATTR: ['style', 'onclick', 'onerror', 'onload'],
    // Remove script and other dangerous tags completely
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input'],
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
