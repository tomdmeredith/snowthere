'use client'

import { motion } from 'framer-motion'
import { Check } from 'lucide-react'

interface LovesCardProps {
  items: string[]
}

export function LovesCard({ items }: LovesCardProps) {
  if (!items || items.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-mint-100/50 border border-mint-300 rounded-2xl p-6"
    >
      <h4 className="font-display font-bold text-dark-800 mb-4 flex items-center gap-2">
        <span>❤️</span>
        <span>What Families Love</span>
      </h4>
      <ul className="space-y-3">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-3">
            <Check className="w-5 h-5 text-teal-500 flex-shrink-0 mt-0.5" />
            <span className="text-dark-700">{item}</span>
          </li>
        ))}
      </ul>
    </motion.div>
  )
}
