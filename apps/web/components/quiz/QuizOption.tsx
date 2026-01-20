'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { Check } from 'lucide-react'
import { QuizOption as QuizOptionType } from '@/lib/quiz/types'

interface QuizOptionProps {
  option: QuizOptionType
  isSelected: boolean
  onSelect: () => void
  delay?: number
  isMultiSelect?: boolean
}

export function QuizOption({
  option,
  isSelected,
  onSelect,
  delay = 0,
  isMultiSelect = false,
}: QuizOptionProps) {
  const [hasClicked, setHasClicked] = useState(false)

  const handleClick = () => {
    if (!hasClicked) {
      setHasClicked(true)
    }
    onSelect()
  }

  return (
    <motion.button
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        delay,
        duration: 0.4,
        type: 'spring',
        stiffness: 300,
        damping: 20,
      }}
      whileHover={{ scale: 1.03, rotate: isSelected ? 0 : 1 }}
      whileTap={{ scale: 0.97 }}
      onClick={handleClick}
      className={`
        relative w-full p-5 rounded-2xl border-2 text-left
        transition-all duration-200 cursor-pointer
        ${
          isSelected
            ? 'border-[var(--option-color)] bg-[var(--option-color)]/10 shadow-lg shadow-[var(--option-color)]/20'
            : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md'
        }
      `}
      style={
        {
          '--option-color': option.color,
        } as React.CSSProperties
      }
    >
      {/* Selection indicator */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{
            type: 'spring',
            stiffness: 500,
            damping: 25,
          }}
          className="absolute -top-2 -right-2 w-7 h-7 rounded-full flex items-center justify-center shadow-md"
          style={{ backgroundColor: option.color }}
        >
          <Check className="w-4 h-4 text-white" strokeWidth={3} />
        </motion.div>
      )}

      {/* Confetti burst on first selection */}
      {isSelected && hasClicked && (
        <>
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 rounded-full"
              style={{
                backgroundColor: option.color,
                left: '50%',
                top: '50%',
              }}
              initial={{ scale: 0, x: 0, y: 0, opacity: 1 }}
              animate={{
                scale: [0, 1.5, 0],
                x: Math.cos((i * Math.PI * 2) / 6) * 60,
                y: Math.sin((i * Math.PI * 2) / 6) * 60,
                opacity: [1, 1, 0],
              }}
              transition={{
                duration: 0.6,
                ease: 'easeOut',
              }}
            />
          ))}
        </>
      )}

      {/* Content */}
      <div className="flex items-start gap-4">
        {/* Emoji */}
        <motion.span
          className="text-3xl"
          animate={isSelected ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 0.3 }}
        >
          {option.emoji}
        </motion.span>

        {/* Text */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3
              className={`font-semibold text-lg ${
                isSelected ? 'text-gray-900' : 'text-gray-700'
              }`}
            >
              {option.label}
            </h3>
            {isMultiSelect && (
              <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
                optional
              </span>
            )}
          </div>
          {option.description && (
            <p className="text-sm text-gray-500 mt-1">{option.description}</p>
          )}
        </div>
      </div>

      {/* Hover glow effect */}
      <motion.div
        className="absolute inset-0 rounded-2xl opacity-0 pointer-events-none"
        style={{
          background: `radial-gradient(circle at center, ${option.color}20 0%, transparent 70%)`,
        }}
        whileHover={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      />
    </motion.button>
  )
}
