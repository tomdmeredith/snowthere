'use client'

import { motion } from 'framer-motion'
import { ExternalLink } from 'lucide-react'

interface PassCardProps {
  name: string
  accessType?: string
  purchaseUrl?: string
  color?: 'coral' | 'teal' | 'gold' | 'mint'
}

const colorConfig = {
  coral: 'border-coral-400 hover:bg-coral-50',
  teal: 'border-teal-400 hover:bg-teal-50',
  gold: 'border-gold-400 hover:bg-gold-50',
  mint: 'border-mint-400 hover:bg-mint-50',
}

export function PassCard({ name, accessType, purchaseUrl, color = 'teal' }: PassCardProps) {
  const Content = (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={`bg-white border-2 ${colorConfig[color]} rounded-2xl p-5 transition-all cursor-pointer`}
    >
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-semibold text-dark-800">{name}</h4>
          {accessType && (
            <span className="text-sm text-dark-500 capitalize">{accessType} access</span>
          )}
        </div>
        {purchaseUrl && <ExternalLink className="w-4 h-4 text-dark-400" />}
      </div>
    </motion.div>
  )

  if (purchaseUrl) {
    return (
      <a
        href={purchaseUrl}
        target="_blank"
        rel="noopener noreferrer"
      >
        {Content}
      </a>
    )
  }

  return Content
}
