import { MetadataRoute } from 'next'
import { supabase } from '@/lib/supabase'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://snowthere.com'

interface Resort {
  slug: string
  country: string
  updated_at: string
  last_refreshed: string | null
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Fetch all published resorts
  const { data: resortsData } = await supabase
    .from('resorts')
    .select('slug, country, updated_at, last_refreshed')
    .eq('status', 'published')
    .order('updated_at', { ascending: false })

  const resorts = (resortsData as Resort[] | null) || []

  // Convert country name to URL slug (e.g., "United States" -> "united-states")
  const countryToSlug = (country: string) =>
    country.toLowerCase().replace(/\s+/g, '-')

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: `${BASE_URL}/resorts`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
  ]

  // Resort pages
  const resortPages: MetadataRoute.Sitemap = resorts.map((resort) => ({
    url: `${BASE_URL}/resorts/${countryToSlug(resort.country)}/${resort.slug}`,
    lastModified: new Date(resort.last_refreshed || resort.updated_at),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }))

  // Get unique countries for country listing pages
  const countries = Array.from(new Set(resorts.map((r) => r.country)))
  const countryPages: MetadataRoute.Sitemap = countries.map((country) => ({
    url: `${BASE_URL}/resorts/${countryToSlug(country)}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }))

  return [...staticPages, ...countryPages, ...resortPages]
}
