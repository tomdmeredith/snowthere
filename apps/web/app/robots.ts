import { MetadataRoute } from 'next'
import { SITE_URL } from '@/lib/constants'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/admin/'],
      },
      // Specific rules for AI crawlers
      {
        userAgent: 'GPTBot',
        allow: '/',
      },
      {
        userAgent: 'ChatGPT-User',
        allow: '/',
      },
      {
        userAgent: 'Claude-Web',
        allow: '/',
      },
      {
        userAgent: 'Anthropic-AI',
        allow: '/',
      },
      {
        userAgent: 'PerplexityBot',
        allow: '/',
      },
      // Per https://platform.openai.com/docs/bots - OAI-SearchBot respects robots.txt
      {
        userAgent: 'OAI-SearchBot',
        allow: '/',
      },
      // Per https://docs.perplexity.ai/guides/bots - Perplexity-User for real-time queries
      {
        userAgent: 'Perplexity-User',
        allow: '/',
      },
      // Google Gemini/AI Overviews
      {
        userAgent: 'Google-Extended',
        allow: '/',
      },
      // Meta AI
      {
        userAgent: 'Meta-ExternalAgent',
        allow: '/',
      },
      // Cohere AI
      {
        userAgent: 'cohere-ai',
        allow: '/',
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  }
}
