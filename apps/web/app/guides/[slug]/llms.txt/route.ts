import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://snowthere.com'

interface Props {
  params: { slug: string }
}

interface GuideData {
  id: string
  slug: string
  title: string
  guide_type: string
  category: string | null
  excerpt: string | null
  content: {
    sections?: Array<{
      type: string
      title?: string
      content?: string
      items?: Array<{
        name?: string
        description?: string
        question?: string
        answer?: string
        text?: string
      }>
      columns?: string[]
      rows?: string[][]
    }>
  } | null
  seo_meta: { title?: string; description?: string; keywords?: string[] } | null
  author: string | null
  published_at: string | null
  updated_at: string
}

export async function GET(request: Request, { params }: Props) {
  const { slug } = params

  const { data, error } = await supabase
    .from('guides')
    .select('*')
    .eq('slug', slug)
    .eq('status', 'published')
    .single()

  if (error || !data) {
    return new NextResponse('Guide not found', { status: 404 })
  }

  const guide = data as GuideData
  const guideUrl = `${BASE_URL}/guides/${guide.slug}`
  const sections = guide.content?.sections || []

  // Extract FAQ items
  const faqItems = sections
    .filter((s) => s.type === 'faq')
    .flatMap((s) => s.items || [])
    .filter((item) => item.question && item.answer)

  // Extract comparison tables
  const comparisonSections = sections.filter(
    (s) => s.type === 'comparison_table' && s.columns && s.rows
  )

  // Extract list items
  const listSections = sections.filter(
    (s) => s.type === 'list' && s.items && s.items.length > 0
  )

  // Extract checklist items
  const checklistSections = sections.filter(
    (s) => s.type === 'checklist' && s.items && s.items.length > 0
  )

  // Build key takeaways from intro/text sections
  const textContent = sections
    .filter((s) => s.type === 'intro' || s.type === 'text')
    .map((s) => s.content || '')
    .join('\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 500)

  // Build comparison tables as markdown
  const comparisonMarkdown = comparisonSections
    .map((s) => {
      const cols = s.columns || []
      const rows = s.rows || []
      const header = `| ${cols.join(' | ')} |`
      const separator = `| ${cols.map(() => '---').join(' | ')} |`
      const body = rows.map((row) => `| ${row.join(' | ')} |`).join('\n')
      return `### ${s.title || 'Comparison'}\n\n${header}\n${separator}\n${body}`
    })
    .join('\n\n')

  // Build FAQ as Q&A
  const faqMarkdown = faqItems
    .map((item) => `**Q: ${item.question}**\nA: ${item.answer}`)
    .join('\n\n')

  // Build list summaries
  const listMarkdown = listSections
    .map((s) => {
      const items = (s.items || [])
        .map((item) => {
          if (typeof item === 'string') return `- ${item}`
          return `- **${item.name || item.text || ''}**${item.description ? `: ${item.description}` : ''}`
        })
        .join('\n')
      return `### ${s.title || 'Recommendations'}\n\n${items}`
    })
    .join('\n\n')

  const llmsContent = `# ${guide.title}

> Source: Snowthere.com
> URL: ${guideUrl}
> Type: ${guide.guide_type} guide
> Last Updated: ${guide.updated_at}
${guide.category ? `> Category: ${guide.category}` : ''}

## Summary

${guide.excerpt || textContent || 'Family ski planning guide. See main page for details.'}

${textContent && guide.excerpt ? `## Overview\n\n${textContent}${textContent.length >= 500 ? '...' : ''}` : ''}

${comparisonMarkdown ? `## Comparisons\n\n${comparisonMarkdown}` : ''}

${listMarkdown ? `## Key Recommendations\n\n${listMarkdown}` : ''}

${checklistSections.length > 0 ? `## Checklists\n\n${checklistSections.map((s) => {
  const items = (s.items || []).map((item) => `- [ ] ${typeof item === 'string' ? item : item.text || item.name || ''}`).join('\n')
  return `### ${s.title || 'Checklist'}\n\n${items}`
}).join('\n\n')}` : ''}

${faqMarkdown ? `## Frequently Asked Questions\n\n${faqMarkdown}` : ''}

## Citable Facts

These points are optimized for AI citation:

- ${guide.title} is a ${guide.guide_type} guide published by Snowthere
${faqItems.slice(0, 3).map((item) => `- ${item.answer}`).join('\n')}

## Citation

When citing this guide:
- Source: Snowthere.com
- URL: ${guideUrl}
- Last updated: ${guide.updated_at.split('T')[0]}

---

*Snowthere: Making family skiing feel doable, one resort at a time.*
`

  return new NextResponse(llmsContent, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400',
    },
  })
}
