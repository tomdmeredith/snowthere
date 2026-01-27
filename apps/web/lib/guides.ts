// Guide utilities for fetching and types
import { supabase } from '@/lib/supabase'

// =============================================================================
// TYPES
// =============================================================================

export type GuideType = 'comparison' | 'how-to' | 'regional' | 'pass' | 'seasonal' | 'gear'

export interface GuideSection {
  type: 'intro' | 'list' | 'checklist' | 'comparison_table' | 'faq' | 'cta' | 'text'
  title?: string
  content?: string // For intro/text sections
  items?: GuideListItem[] | GuideChecklistItem[] | GuideFAQItem[]
  columns?: string[] // For comparison tables
  rows?: string[][] // For comparison tables
  cta?: GuideCTA // For CTA sections
}

export interface GuideListItem {
  name: string
  description?: string
  resort_slug?: string
  resort_id?: string
}

export interface GuideChecklistItem {
  text: string
  checked?: boolean
}

export interface GuideFAQItem {
  question: string
  answer: string
}

export interface GuideCTA {
  text: string
  href: string
  variant?: 'primary' | 'secondary'
}

export interface GuideContent {
  sections: GuideSection[]
}

export interface Guide {
  id: string
  slug: string
  title: string
  guide_type: GuideType
  category: string | null
  excerpt: string | null
  content: GuideContent
  featured_image_url: string | null
  seo_meta: {
    title?: string
    description?: string
    keywords?: string[]
  } | null
  featured_resort_ids: string[]
  status: 'draft' | 'published' | 'archived'
  author: string
  created_at: string
  updated_at: string
  published_at: string | null
}

export interface GuideResort {
  guide_id: string
  resort_id: string
  display_order: number
  highlight_reason: string | null
  resort?: {
    id: string
    name: string
    slug: string
    country: string
    family_metrics?: {
      family_overall_score: number | null
    }
  }
}

export interface GuideWithResorts extends Guide {
  guide_resorts: GuideResort[]
}

// =============================================================================
// FETCH FUNCTIONS
// =============================================================================

/**
 * Get a guide by slug with its featured resorts
 */
export async function getGuideBySlug(slug: string): Promise<GuideWithResorts | null> {
  const { data, error } = await supabase
    .from('guides')
    .select(`
      *,
      guide_resorts (
        guide_id,
        resort_id,
        display_order,
        highlight_reason,
        resort:resorts (
          id,
          name,
          slug,
          country,
          family_metrics:resort_family_metrics (
            family_overall_score
          )
        )
      )
    `)
    .eq('slug', slug)
    .eq('status', 'published')
    .single()

  if (error) {
    console.error('Error fetching guide:', error)
    return null
  }

  return data as GuideWithResorts
}

/**
 * Get all published guide slugs for static generation
 */
export async function getAllGuideSlugs(): Promise<string[]> {
  const { data, error } = await supabase
    .from('guides')
    .select('slug')
    .eq('status', 'published')

  if (error) {
    console.error('Error fetching guide slugs:', error)
    return []
  }

  return data.map(g => g.slug)
}

/**
 * Get related guides by type or category
 */
export async function getRelatedGuides(
  currentSlug: string,
  guideType: GuideType,
  limit: number = 3
): Promise<Pick<Guide, 'slug' | 'title' | 'guide_type' | 'excerpt'>[]> {
  const { data, error } = await supabase
    .from('guides')
    .select('slug, title, guide_type, excerpt')
    .eq('status', 'published')
    .eq('guide_type', guideType)
    .neq('slug', currentSlug)
    .limit(limit)

  if (error) {
    console.error('Error fetching related guides:', error)
    return []
  }

  return data
}

// =============================================================================
// GUIDE TYPE CONFIG
// =============================================================================

export const GUIDE_TYPE_CONFIG: Record<
  GuideType,
  { label: string; color: string; description: string }
> = {
  comparison: {
    label: 'Resort Comparisons',
    color: 'coral',
    description: 'Side-by-side resort comparisons for families',
  },
  'how-to': {
    label: 'How-To Guides',
    color: 'teal',
    description: 'Step-by-step guides and practical checklists',
  },
  regional: {
    label: 'Regional Guides',
    color: 'mint',
    description: 'Explore family skiing by region',
  },
  pass: {
    label: 'Pass Guides',
    color: 'gold',
    description: 'Navigate ski pass options for your family',
  },
  seasonal: {
    label: 'Seasonal Guides',
    color: 'coral',
    description: 'Time your family ski trip perfectly',
  },
  gear: {
    label: 'Gear & Packing',
    color: 'teal',
    description: 'What to pack and what to rent',
  },
}
