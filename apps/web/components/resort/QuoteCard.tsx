'use client'

import { motion } from 'framer-motion'

interface QuoteCardProps {
  quote: string
  familyType?: string
  rotation?: number
}

export function QuoteCard({ quote, familyType, rotation = 0 }: QuoteCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      whileHover={{ scale: 1.02 }}
      className="relative bg-cream rounded-3xl p-6 sm:p-8 transition-transform"
      style={{
        transform: `rotate(${rotation}deg)`,
        background: 'linear-gradient(145deg, #FFF5E6, #FFFAF3)',
      }}
    >
      {/* Quote marks */}
      <span className="absolute top-4 left-6 font-display text-6xl text-coral-300 leading-none select-none">
        &ldquo;
      </span>

      {/* Quote text */}
      <blockquote className="relative z-10 pt-8 text-lg text-dark-700 leading-relaxed italic">
        {quote}
      </blockquote>

      {/* Attribution */}
      {familyType && (
        <div className="mt-4 flex items-center gap-2">
          <span className="text-dark-400">—</span>
          <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-teal-100 text-teal-700">
            {familyType}
          </span>
        </div>
      )}

      {/* Closing quote */}
      <span className="absolute bottom-4 right-6 font-display text-6xl text-coral-300 leading-none rotate-180 select-none">
        &rdquo;
      </span>
    </motion.div>
  )
}
