import { supabase } from '@/lib/supabase'
import { SITE_URL } from '@/lib/constants'

interface ResortImage {
  image_url: string
  image_type: string
  alt_text: string | null
}

interface Resort {
  slug: string
  name: string
  country: string
  updated_at: string
  last_refreshed: string | null
  images: ResortImage[] | null
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

function countryToSlug(country: string): string {
  return country.toLowerCase().replace(/\s+/g, '-')
}

function escapeXml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export async function GET() {
  // Fetch all published resorts with images
  const { data: resortsData } = await supabase
    .from('resorts')
    .select('slug, name, country, updated_at, last_refreshed, images:resort_images(image_url, image_type, alt_text)')
    .eq('status', 'published')
    .order('updated_at', { ascending: false })

  const resorts = (resortsData as Resort[] | null) || []

  // Fetch all published guides
  const { data: guidesData } = await supabase
    .from('guides')
    .select('slug, updated_at')
    .eq('status', 'published')
    .order('updated_at', { ascending: false })

  const guides = (guidesData as { slug: string; updated_at: string }[] | null) || []

  // Get unique countries
  const countries = Array.from(new Set(resorts.map((r) => r.country)))

  const today = formatDate(new Date())

  // Build XML parts
  const staticUrls = `  <url>
    <loc>${SITE_URL}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${SITE_URL}/resorts</loc>
    <lastmod>${today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>`

  // Collection (programmatic SEO) pages
  const collectionSlugs = [
    'best-for-toddlers',
    'best-for-beginners',
    'cheapest-family-resorts',
    'epic-pass-resorts',
    'ikon-pass-resorts',
    'with-childcare',
  ]

  const collectionUrls = collectionSlugs
    .map((slug) => `  <url>
    <loc>${SITE_URL}/collections/${slug}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`)
    .join('\n')

  // Legal and static pages
  const legalUrls = ['/about', '/methodology', '/contact', '/privacy', '/terms', '/quiz']
    .map((path) => `  <url>
    <loc>${SITE_URL}${path}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>`)
    .join('\n')

  const countryUrls = countries
    .map((country) => `  <url>
    <loc>${SITE_URL}/resorts/${countryToSlug(country)}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`)
    .join('\n')

  const resortUrls = resorts
    .map((resort) => {
      const loc = `${SITE_URL}/resorts/${countryToSlug(resort.country)}/${resort.slug}`
      const lastmod = formatDate(new Date(resort.last_refreshed || resort.updated_at))

      // Build image tags for this resort
      const images = resort.images || []
      const imageTags = images
        .filter((img) => img.image_url)
        .map((img) => {
          const title = escapeXml(img.alt_text || `${resort.name} ski resort`)
          return `    <image:image>
      <image:loc>${escapeXml(img.image_url)}</image:loc>
      <image:title>${title}</image:title>
    </image:image>`
        })
        .join('\n')

      return `  <url>
    <loc>${loc}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
${imageTags}
  </url>`
    })
    .join('\n')

  const guideIndexUrl = `  <url>
    <loc>${SITE_URL}/guides</loc>
    <lastmod>${today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`

  const guideUrls = guides
    .map((guide) => `  <url>
    <loc>${SITE_URL}/guides/${guide.slug}</loc>
    <lastmod>${formatDate(new Date(guide.updated_at))}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`)
    .join('\n')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
${staticUrls}
${collectionUrls}
${legalUrls}
${countryUrls}
${resortUrls}
${guideIndexUrl}
${guideUrls}
</urlset>`

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}
