import { supabase } from '@/lib/supabase'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://snowthere.com'

interface Resort {
  slug: string
  country: string
  updated_at: string
  last_refreshed: string | null
}

function formatDate(date: Date): string {
  return date.toISOString().split('T')[0]
}

function countryToSlug(country: string): string {
  return country.toLowerCase().replace(/\s+/g, '-')
}

export async function GET() {
  // Fetch all published resorts
  const { data: resortsData } = await supabase
    .from('resorts')
    .select('slug, country, updated_at, last_refreshed')
    .eq('status', 'published')
    .order('updated_at', { ascending: false })

  const resorts = (resortsData as Resort[] | null) || []

  // Get unique countries
  const countries = Array.from(new Set(resorts.map((r) => r.country)))

  // Build XML parts
  const staticUrls = `  <url>
    <loc>${BASE_URL}</loc>
    <lastmod>${formatDate(new Date())}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${BASE_URL}/resorts</loc>
    <lastmod>${formatDate(new Date())}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>`

  const countryUrls = countries
    .map((country) => `  <url>
    <loc>${BASE_URL}/resorts/${countryToSlug(country)}</loc>
    <lastmod>${formatDate(new Date())}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>`)
    .join('\n')

  const resortUrls = resorts
    .map((resort) => `  <url>
    <loc>${BASE_URL}/resorts/${countryToSlug(resort.country)}/${resort.slug}</loc>
    <lastmod>${formatDate(new Date(resort.last_refreshed || resort.updated_at))}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`)
    .join('\n')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${staticUrls}
${countryUrls}
${resortUrls}
</urlset>`

  return new Response(xml, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600, s-maxage=3600',
    },
  })
}
