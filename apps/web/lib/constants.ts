const raw = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.snowthere.com'
export const SITE_URL = raw.trim().replace(/\/+$/, '')
