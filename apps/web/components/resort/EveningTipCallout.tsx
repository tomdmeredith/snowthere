'use client'

import { motion } from 'framer-motion'

interface EveningTipCalloutProps {
  children: React.ReactNode
}

export function EveningTipCallout({ children }: EveningTipCalloutProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-dark-800 rounded-2xl p-5 my-6"
    >
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">🌙</span>
        <div>
          <span className="font-bold text-gold-300 block mb-1">EVENING TIP</span>
          <div className="text-dark-200 leading-relaxed">{children}</div>
        </div>
      </div>
    </motion.div>
  )
}
