'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { BookOpen, Map, CheckSquare, CreditCard, Snowflake, Calendar } from 'lucide-react'

// Guide type configuration
const GUIDE_TYPE_CONFIG: Record<
  string,
  { icon: React.ElementType; color: string; bgColor: string; textColor: string; label: string }
> = {
  comparison: {
    icon: Map,
    color: 'coral',
    bgColor: 'bg-coral-50',
    textColor: 'text-coral-600',
    label: 'Resort Comparison',
  },
  'how-to': {
    icon: CheckSquare,
    color: 'teal',
    bgColor: 'bg-teal-50',
    textColor: 'text-teal-600',
    label: 'How-To Guide',
  },
  regional: {
    icon: Map,
    color: 'mint',
    bgColor: 'bg-mint-50',
    textColor: 'text-mint-600',
    label: 'Regional Guide',
  },
  pass: {
    icon: CreditCard,
    color: 'gold',
    bgColor: 'bg-gold-50',
    textColor: 'text-gold-600',
    label: 'Pass Guide',
  },
  seasonal: {
    icon: Calendar,
    color: 'coral',
    bgColor: 'bg-coral-50',
    textColor: 'text-coral-600',
    label: 'Seasonal Guide',
  },
  gear: {
    icon: Snowflake,
    color: 'teal',
    bgColor: 'bg-teal-50',
    textColor: 'text-teal-600',
    label: 'Gear Guide',
  },
}

interface GuideCardProps {
  guide: {
    id: string
    slug: string
    title: string
    guide_type: string
    category?: string | null
    excerpt?: string | null
    featured_image_url?: string | null
  }
  delay?: number
}

export function GuideCard({ guide, delay = 0 }: GuideCardProps) {
  const config = GUIDE_TYPE_CONFIG[guide.guide_type] || GUIDE_TYPE_CONFIG.comparison
  const Icon = config.icon

  return (
    <Link href={`/guides/${guide.slug}`}>
      <motion.article
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay, duration: 0.3 }}
        whileHover={{ y: -4 }}
        className="group bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden h-full flex flex-col"
      >
        {/* Image or placeholder */}
        <div className={`h-40 ${config.bgColor} flex items-center justify-center relative overflow-hidden`}>
          {guide.featured_image_url ? (
            <img
              src={guide.featured_image_url}
              alt={guide.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
          ) : (
            <motion.div
              initial={{ scale: 1 }}
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ duration: 0.3 }}
            >
              <Icon className={`w-16 h-16 ${config.textColor} opacity-50`} />
            </motion.div>
          )}

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        </div>

        {/* Content */}
        <div className="p-5 flex-1 flex flex-col">
          {/* Type badge */}
          <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${config.textColor} ${config.bgColor} px-2.5 py-1 rounded-full w-fit mb-3`}>
            <Icon className="w-3 h-3" />
            {config.label}
          </span>

          {/* Title */}
          <h2 className="font-display text-lg font-bold text-gray-900 group-hover:text-coral-500 transition-colors mb-2 line-clamp-2">
            {guide.title}
          </h2>

          {/* Excerpt */}
          {guide.excerpt && (
            <p className="text-sm text-gray-600 line-clamp-3 flex-1">
              {guide.excerpt}
            </p>
          )}

          {/* Category tag */}
          {guide.category && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <span className="text-xs text-gray-400 capitalize">
                {guide.category}
              </span>
            </div>
          )}
        </div>
      </motion.article>
    </Link>
  )
}
