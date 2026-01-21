'use client'

import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface SectionHeaderProps {
  emoji: string
  title: string
  icon: LucideIcon
  color: 'coral' | 'teal' | 'gold' | 'mint' | 'dark'
}

const colorConfig = {
  coral: {
    bg: 'bg-gradient-to-br from-coral-100 to-coral-50',
    shadow: 'shadow-coral',
    icon: 'text-coral-600',
  },
  teal: {
    bg: 'bg-gradient-to-br from-teal-100 to-mint-100',
    shadow: 'shadow-teal',
    icon: 'text-teal-600',
  },
  gold: {
    bg: 'bg-gradient-to-br from-gold-100 to-gold-50',
    shadow: 'shadow-gold',
    icon: 'text-gold-600',
  },
  mint: {
    bg: 'bg-gradient-to-br from-mint-100 to-mint-50',
    shadow: 'shadow-teal',
    icon: 'text-teal-600',
  },
  dark: {
    bg: 'bg-gradient-to-br from-dark-100 to-dark-50',
    shadow: 'shadow-card',
    icon: 'text-dark-600',
  },
}

export function SectionHeader({ emoji, title, icon: Icon, color }: SectionHeaderProps) {
  const config = colorConfig[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="flex items-center gap-4 mb-8"
    >
      <div className={`p-3 rounded-2xl ${config.bg} ${config.shadow}`}>
        <Icon className={`w-6 h-6 ${config.icon}`} />
      </div>
      <h2 className="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
        <span>{emoji}</span>
        <span>{title}</span>
      </h2>
    </motion.div>
  )
}
