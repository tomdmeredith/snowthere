'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'

interface AgeBubbleProps {
  emoji: string
  label: string
  ageRange: string
  description: string
  isSelected: boolean
  onToggle: () => void
  color: string
  delay?: number
}

export function AgeBubble({
  emoji,
  label,
  ageRange,
  description,
  isSelected,
  onToggle,
  color,
  delay = 0,
}: AgeBubbleProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.button
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        delay,
        duration: 0.4,
        type: 'spring',
        stiffness: 300,
        damping: 20
      }}
      whileHover={{ scale: 1.05, rotate: isSelected ? 0 : 2 }}
      whileTap={{ scale: 0.95 }}
      onClick={onToggle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      role="checkbox"
      aria-checked={isSelected}
      aria-label={`${label} (${ageRange}): ${description}`}
      className={`
        relative flex flex-col items-center justify-center
        w-full min-h-[140px] p-4 rounded-3xl
        border-4 transition-all duration-300 cursor-pointer
        ${isSelected
          ? 'border-current shadow-lg'
          : 'border-gray-200 hover:border-current/50'
        }
      `}
      style={{
        backgroundColor: isSelected ? `${color}15` : 'white',
        color: color,
        boxShadow: isSelected
          ? `0 8px 24px ${color}30, 0 4px 12px ${color}20`
          : isHovered
            ? `0 4px 16px ${color}15`
            : '0 2px 8px rgba(0,0,0,0.06)',
      }}
    >
      {/* Selection indicator */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-current flex items-center justify-center"
        >
          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </motion.div>
      )}

      {/* Emoji with bounce */}
      <motion.span
        className="text-4xl mb-2"
        animate={{
          y: isHovered ? [-2, 2, -2] : 0,
          rotate: isSelected ? [0, -5, 5, 0] : 0,
        }}
        transition={{
          y: { repeat: isHovered ? Infinity : 0, duration: 0.6 },
          rotate: { duration: 0.4 },
        }}
      >
        {emoji}
      </motion.span>

      {/* Age range */}
      <span className="font-bold text-lg text-dark-700">
        {ageRange}
      </span>

      {/* Label */}
      <span className="font-medium text-sm mt-1" style={{ color }}>
        {label}
      </span>

      {/* Description (shows on hover/select) */}
      <motion.span
        initial={false}
        animate={{
          opacity: isHovered || isSelected ? 1 : 0,
          height: isHovered || isSelected ? 'auto' : 0,
        }}
        className="text-xs text-dark-500 mt-2 text-center overflow-hidden"
      >
        {description}
      </motion.span>

      {/* Confetti burst on selection */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0, opacity: 1 }}
          animate={{ scale: 2, opacity: 0 }}
          transition={{ duration: 0.5 }}
          className="absolute inset-0 pointer-events-none"
        >
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              initial={{
                x: 0,
                y: 0,
                scale: 1,
                opacity: 1
              }}
              animate={{
                x: Math.cos(i * 45 * Math.PI / 180) * 50,
                y: Math.sin(i * 45 * Math.PI / 180) * 50,
                scale: 0,
                opacity: 0,
              }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="absolute top-1/2 left-1/2 w-2 h-2 rounded-full"
              style={{
                backgroundColor: i % 2 === 0 ? color : '#FFE066',
                transform: 'translate(-50%, -50%)',
              }}
            />
          ))}
        </motion.div>
      )}
    </motion.button>
  )
}
