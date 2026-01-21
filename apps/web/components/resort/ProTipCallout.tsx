'use client'

import { motion } from 'framer-motion'

interface ProTipCalloutProps {
  children: React.ReactNode
}

export function ProTipCallout({ children }: ProTipCalloutProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-gold-100/50 border-2 border-gold-300 rounded-2xl p-5 my-6"
    >
      <div className="flex items-start gap-3">
        <span className="text-xl flex-shrink-0">💡</span>
        <div>
          <span className="font-bold text-gold-800 block mb-1">PRO TIP</span>
          <div className="text-dark-700 leading-relaxed">{children}</div>
        </div>
      </div>
    </motion.div>
  )
}
