'use client'

import { motion } from 'framer-motion'

interface WarningCalloutProps {
  children: React.ReactNode
  title?: string
}

export function WarningCallout({ children, title = 'HEADS UP' }: WarningCalloutProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-coral-50 border-2 border-coral-200 rounded-2xl p-5 my-6"
    >
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">⚠️</span>
        <div>
          <span className="font-bold text-coral-700 block mb-1">{title}</span>
          <div className="text-dark-700 leading-relaxed">{children}</div>
        </div>
      </div>
    </motion.div>
  )
}
