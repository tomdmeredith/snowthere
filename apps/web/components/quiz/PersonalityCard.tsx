'use client'

import { motion } from 'framer-motion'
import { PersonalityProfile } from '@/lib/quiz/types'

interface PersonalityCardProps {
  personality: PersonalityProfile
}

export function PersonalityCard({ personality }: PersonalityCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
      className="relative bg-white rounded-3xl shadow-xl overflow-hidden"
    >
      {/* Decorative background gradient */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          background: `linear-gradient(135deg, ${personality.color}40, transparent)`,
        }}
      />

      {/* Decorative corner shapes */}
      <div
        className="absolute -top-8 -right-8 w-32 h-32 rounded-full opacity-20"
        style={{ backgroundColor: personality.color }}
      />
      <div
        className="absolute -bottom-12 -left-12 w-40 h-40 rounded-full opacity-10"
        style={{ backgroundColor: personality.color }}
      />

      <div className="relative z-10 p-8 md:p-10">
        {/* Emoji and Type Label */}
        <div className="flex items-center gap-4 mb-6">
          <motion.span
            className="text-6xl"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 15,
              delay: 0.2,
            }}
          >
            {personality.emoji}
          </motion.span>
          <div>
            <motion.p
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="text-sm font-medium text-gray-500 uppercase tracking-wide"
            >
              Your Snow Personality
            </motion.p>
            <motion.h2
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="font-display text-3xl md:text-4xl font-bold"
              style={{ color: personality.colorDark }}
            >
              {personality.title}
            </motion.h2>
          </div>
        </div>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-lg text-gray-600 leading-relaxed mb-6"
        >
          {personality.description}
        </motion.p>

        {/* Traits */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="flex flex-wrap gap-2"
        >
          {personality.traits.map((trait, index) => (
            <motion.span
              key={trait}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.7 + index * 0.1 }}
              className="px-4 py-2 rounded-full text-sm font-medium"
              style={{
                backgroundColor: `${personality.color}15`,
                color: personality.color,
              }}
            >
              {trait}
            </motion.span>
          ))}
        </motion.div>

        {/* Tagline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-6 pt-6 border-t border-gray-100"
        >
          <p className="text-sm text-gray-400 italic">&quot;{personality.tagline}&quot;</p>
        </motion.div>
      </div>

      {/* Confetti-like decorations */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full"
          style={{
            backgroundColor: personality.color,
            left: `${15 + i * 15}%`,
            top: `${10 + (i % 3) * 30}%`,
          }}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 0.3, scale: 1 }}
          transition={{ delay: 1.2 + i * 0.1 }}
        />
      ))}
    </motion.div>
  )
}
