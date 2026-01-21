'use client'

import { motion } from 'framer-motion'

interface TerrainBreakdownProps {
  beginner: number
  intermediate: number
  advanced: number
}

export function TerrainBreakdown({ beginner, intermediate, advanced }: TerrainBreakdownProps) {
  const terrainData = [
    { label: 'Beginner', emoji: '🟢', percentage: beginner, color: '#22C55E' },
    { label: 'Intermediate', emoji: '🔵', percentage: intermediate, color: '#3B82F6' },
    { label: 'Advanced', emoji: '⚫', percentage: advanced, color: '#2D3436' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-cream rounded-2xl p-6"
      style={{ background: 'linear-gradient(145deg, #FFF5E6, #FFFAF3)' }}
    >
      <h4 className="font-display font-bold text-dark-800 mb-5">
        Terrain Breakdown
      </h4>
      <div className="space-y-4">
        {terrainData.map((terrain, index) => (
          <div key={terrain.label}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-dark-600 flex items-center gap-2">
                <span>{terrain.emoji}</span>
                <span>{terrain.label}</span>
              </span>
              <span className="font-semibold text-dark-800">{terrain.percentage}%</span>
            </div>
            <div className="h-3 bg-dark-100 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: `${terrain.percentage}%` }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.8, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ backgroundColor: terrain.color }}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
