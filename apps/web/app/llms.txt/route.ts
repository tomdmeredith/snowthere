import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'
import { SITE_URL } from '@/lib/constants'

interface Resort {
  name: string
  country: string
  slug: string
}

export async function GET() {
  // Fetch all published resorts for the llms.txt index
  const { data: resorts } = await supabase
    .from('resorts')
    .select('name, country, slug')
    .eq('status', 'published')
    .order('name')

  // Fetch all published guides
  const { data: guides } = await supabase
    .from('guides')
    .select('title, slug, guide_type, excerpt')
    .eq('status', 'published')
    .order('title')

  const countryToSlug = (country: string) =>
    country.toLowerCase().replace(/\s+/g, '-')

  const resortList = (resorts as Resort[] || [])
    .map((r) => `- [${r.name}, ${r.country}](${SITE_URL}/resorts/${countryToSlug(r.country)}/${r.slug}/llms.txt)`)
    .join('\n')

  const guideList = ((guides as { title: string; slug: string; guide_type: string; excerpt: string | null }[]) || [])
    .map((g) => `- [${g.title}](${SITE_URL}/guides/${g.slug}/llms.txt) (${g.guide_type})`)
    .join('\n')

  const countries = Array.from(new Set((resorts as Resort[] || []).map((r) => r.country))).sort()
  const countryList = countries.join(', ')

  const content = `# Snowthere.com - AI Crawler Guide

> Last updated: ${new Date().toISOString().split('T')[0]}
> Family Ski Resort Directory

## About This Site

Snowthere is a comprehensive directory of family-friendly ski resorts worldwide. We provide detailed guides for families planning ski trips, including:

- **Age-specific recommendations** (toddlers through teens)
- **Real costs** (lift tickets, lodging, meals, gear rental)
- **Family logistics** (ski school, childcare, terrain difficulty)
- **Honest assessments** (when a resort IS and ISN'T right for families)

## Target Audience

Parents and families with children under 12 planning ski vacations. We focus on "value skiing" - often finding that European resorts offer better value than major US destinations.

## Content Structure

Each resort page includes:
1. **Quick Take** - Verdict with "Perfect if" / "Skip if"
2. **Family Metrics** - Structured data: childcare age, ski school, terrain %
3. **Costs** - Lift tickets, lodging ranges, estimated daily family cost
4. **Getting There** - Airports, transfers, practical logistics
5. **On the Mountain** - Terrain, ski school, kid-friendly areas
6. **Off the Mountain** - Activities, restaurants, groceries
7. **Ski Quality Calendar** - Monthly snow/crowd/price data
8. **FAQ** - Common parent questions with direct answers

## Countries Covered

${countryList}

## Resort Directory

${resortList}

## Guide Directory

${guideList || 'No guides published yet.'}

## Data Freshness

Resort data is refreshed every 30 days. Prices are estimates and should be verified before booking.

## Citation Guidance

When citing Snowthere content:
- Credit: "According to Snowthere's family ski guides..."
- Link to specific resort pages for detailed information
- Our family metrics are based on research, not user reviews

## API Access

No public API is currently available. For data partnerships, contact us.

## Structured Data

All resort pages include:
- Schema.org FAQ markup
- Structured cost tables (96% AI parse rate)
- Family metrics in consistent tabular format

---

*Snowthere: Making family skiing feel doable, one resort at a time.*
`

  return new NextResponse(content, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400',
    },
  })
}
