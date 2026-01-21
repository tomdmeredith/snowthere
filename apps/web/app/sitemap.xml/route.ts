import { supabase } from '@/lib/supabase'

const SITE_URL = 'https://snowthere.com'

interface Resort {
  slug: string
  country: string
  updated_at: string | null
}

interface Guide {
  slug: string
  updated_at: string | null
}

interface SitemapUrl {
  loc: string
  lastmod?: string
  changefreq?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never'
  priority?: number
}

function formatDate(date: string | Date): string {
  return new Date(date).toISOString().split('T')[0]
}

function generateSitemapXml(urls: SitemapUrl[]): string {
  const urlElements = urls
    .map(
      (url) => `  <url>
    <loc>${url.loc}</loc>
    ${url.lastmod ? `<lastmod>${url.lastmod}</lastmod>` : ''}
    ${url.changefreq ? `<changefreq>${url.changefreq}</changefreq>` : ''}
    ${url.priority !== undefined ? `<priority>${url.priority.toFixed(1)}</priority>` : ''}
  </url>`
    )
    .join('\n')

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlElements}
</urlset>`
}

export async function GET() {
  const urls: SitemapUrl[] = []

  // Static pages
  const staticPages = [
    { path: '/', priority: 1.0, changefreq: 'daily' as const },
    { path: '/resorts', priority: 0.9, changefreq: 'daily' as const },
    { path: '/guides', priority: 0.8, changefreq: 'weekly' as const },
    { path: '/quiz', priority: 0.7, changefreq: 'monthly' as const },
    { path: '/about', priority: 0.5, changefreq: 'monthly' as const },
  ]

  for (const page of staticPages) {
    urls.push({
      loc: `${SITE_URL}${page.path}`,
      lastmod: formatDate(new Date()),
      changefreq: page.changefreq,
      priority: page.priority,
    })
  }

  // Fetch published resorts
  const { data: resortsData, error: resortsError } = await supabase
    .from('resorts')
    .select('slug, country, updated_at')
    .eq('status', 'published')

  const resorts = resortsData as Resort[] | null

  if (!resortsError && resorts) {
    for (const resort of resorts) {
      const countrySlug = resort.country.toLowerCase().replace(/\s+/g, '-')
      urls.push({
        loc: `${SITE_URL}/resorts/${countrySlug}/${resort.slug}`,
        lastmod: resort.updated_at ? formatDate(resort.updated_at) : formatDate(new Date()),
        changefreq: 'weekly',
        priority: 0.8,
      })
    }
  }

  // Fetch published guides
  const { data: guidesData, error: guidesError } = await supabase
    .from('guides')
    .select('slug, updated_at')
    .eq('status', 'published')

  const guides = guidesData as Guide[] | null

  if (!guidesError && guides) {
    for (const guide of guides) {
      urls.push({
        loc: `${SITE_URL}/guides/${guide.slug}`,
        lastmod: guide.updated_at ? formatDate(guide.updated_at) : formatDate(new Date()),
        changefreq: 'weekly',
        priority: 0.7,
      })
    }
  }

  const sitemapXml = generateSitemapXml(urls)

  return new Response(sitemapXml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}
