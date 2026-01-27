import { Map, CheckSquare, CreditCard, Snowflake, Calendar, BookOpen } from 'lucide-react'
import type { GuideType } from '@/lib/guides'

const TYPE_ICONS: Record<GuideType, React.ElementType> = {
  comparison: Map,
  'how-to': CheckSquare,
  regional: Map,
  pass: CreditCard,
  seasonal: Calendar,
  gear: Snowflake,
}

const TYPE_LABELS: Record<GuideType, string> = {
  comparison: 'Resort Comparison',
  'how-to': 'How-To Guide',
  regional: 'Regional Guide',
  pass: 'Pass Guide',
  seasonal: 'Seasonal Guide',
  gear: 'Gear Guide',
}

interface GuideHeroProps {
  title: string
  excerpt: string | null
  guideType: GuideType
  category: string | null
  featuredImageUrl: string | null
  author: string
  publishedAt: string | null
}

export function GuideHero({
  title,
  excerpt,
  guideType,
  category,
  featuredImageUrl,
  author,
  publishedAt,
}: GuideHeroProps) {
  const Icon = TYPE_ICONS[guideType] || BookOpen
  const typeLabel = TYPE_LABELS[guideType] || 'Guide'

  const formattedDate = publishedAt
    ? new Date(publishedAt).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  return (
    <section className="relative py-12 md:py-20">
      {/* Background image or gradient */}
      {featuredImageUrl ? (
        <div className="absolute inset-0">
          <img
            src={featuredImageUrl}
            alt=""
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/70" />
        </div>
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-coral-500 via-coral-400 to-teal-400" />
      )}

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-3xl">
          {/* Type badge */}
          <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-white mb-6">
            <Icon className="w-4 h-4" />
            <span>{typeLabel}</span>
            {category && (
              <>
                <span className="text-white/60">|</span>
                <span className="text-white/90">{category}</span>
              </>
            )}
          </div>

          {/* Title */}
          <h1 className="font-display text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 leading-tight">
            {title}
          </h1>

          {/* Excerpt */}
          {excerpt && (
            <p className="text-lg md:text-xl text-white/90 mb-6 leading-relaxed">
              {excerpt}
            </p>
          )}

          {/* Meta */}
          <div className="flex items-center gap-4 text-sm text-white/80">
            <span>By {author}</span>
            {formattedDate && (
              <>
                <span className="text-white/40">|</span>
                <span>{formattedDate}</span>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
