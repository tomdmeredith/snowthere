import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://snowthere.com'

interface Props {
  params: { country: string; slug: string }
}

interface ResortWithRelations {
  name: string
  country: string
  region: string | null
  slug: string
  last_refreshed: string | null
  updated_at: string
  family_metrics: Record<string, unknown> | null
  content: Record<string, unknown> | null
  costs: Record<string, unknown> | null
}

export async function GET(request: Request, { params }: Props) {
  const { country, slug } = params

  // Convert URL slug back to country name
  const countryName = decodeURIComponent(country)
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())

  const countrySlug = country.toLowerCase().replace(/\s+/g, '-')

  // Fetch resort data
  const { data, error } = await supabase
    .from('resorts')
    .select(`
      *,
      family_metrics:resort_family_metrics(*),
      content:resort_content(*),
      costs:resort_costs(*)
    `)
    .eq('slug', slug)
    .eq('country', countryName)
    .eq('status', 'published')
    .single()

  if (error || !data) {
    return new NextResponse('Resort not found', { status: 404 })
  }

  const resort = data as unknown as ResortWithRelations
  const metrics = resort.family_metrics as Record<string, unknown> | null
  const content = resort.content as Record<string, unknown> | null
  const costs = resort.costs as Record<string, unknown> | null

  const resortUrl = `${BASE_URL}/resorts/${countrySlug}/${slug}`

  // Build structured llms.txt content for this specific resort
  const llmsContent = `# ${resort.name} - Family Ski Guide

> Source: Snowthere.com
> URL: ${resortUrl}
> Last Updated: ${resort.last_refreshed || resort.updated_at}
> Country: ${resort.country}
> Region: ${resort.region || 'N/A'}

## Quick Summary

${content?.quick_take || 'Family-focused ski resort guide. See main page for details.'}

## Family Metrics

| Metric | Value |
|--------|-------|
| Family Score | ${metrics?.family_overall_score || 'N/A'}/10 |
| Best Ages | ${metrics?.best_age_min || '?'}-${metrics?.best_age_max || '?'} years |
| Childcare From | ${metrics?.childcare_min_age ? `${metrics.childcare_min_age} months` : 'N/A'} |
| Ski School From | ${metrics?.ski_school_min_age ? `${metrics.ski_school_min_age} years` : 'N/A'} |
| Kids Ski Free | ${metrics?.kids_ski_free_age ? `Under ${metrics.kids_ski_free_age}` : 'N/A'} |
| Kid-Friendly Terrain | ${metrics?.kid_friendly_terrain_pct || 'N/A'}% |
| Has Childcare | ${metrics?.has_childcare ? 'Yes' : 'No'} |
| Magic Carpet | ${metrics?.has_magic_carpet ? 'Yes' : 'No'} |

## Estimated Costs (${costs?.currency || 'USD'})

| Item | Cost |
|------|------|
| Adult Lift (daily) | ${costs?.lift_adult_daily ? `$${costs.lift_adult_daily}` : 'N/A'} |
| Child Lift (daily) | ${costs?.lift_child_daily ? `$${costs.lift_child_daily}` : 'N/A'} |
| Budget Lodging/night | ${costs?.lodging_budget_nightly ? `$${costs.lodging_budget_nightly}` : 'N/A'} |
| Mid-range Lodging/night | ${costs?.lodging_mid_nightly ? `$${costs.lodging_mid_nightly}` : 'N/A'} |
| Family Meal | ${costs?.meal_family_avg ? `$${costs.meal_family_avg}` : 'N/A'} |
| Est. Family Daily | ${costs?.estimated_family_daily ? `$${costs.estimated_family_daily}` : 'N/A'} |

## Perfect If

${((metrics?.perfect_if as string[]) || []).map((p) => `- ${p}`).join('\n') || '- See main page for recommendations'}

## Skip If

${((metrics?.skip_if as string[]) || []).map((s) => `- ${s}`).join('\n') || '- See main page for recommendations'}

## Key Sections

- Getting There: ${content?.getting_there ? 'Available' : 'Coming soon'}
- Where to Stay: ${content?.where_to_stay ? 'Available' : 'Coming soon'}
- On the Mountain: ${content?.on_mountain ? 'Available' : 'Coming soon'}
- Off the Mountain: ${content?.off_mountain ? 'Available' : 'Coming soon'}

## Citation

When citing this resort information:
- Source: Snowthere.com
- URL: ${resortUrl}
- Last verified: ${(resort.last_refreshed || resort.updated_at).split('T')[0]}

Note: Prices are estimates and should be verified with the resort before booking.
`

  return new NextResponse(llmsContent, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400',
    },
  })
}
