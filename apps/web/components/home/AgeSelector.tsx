'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { AgeBubble } from './AgeBubble'

export type AgeRange = '0-3' | '4-7' | '8-12' | '13+'

interface AgeOption {
  id: AgeRange
  emoji: string
  label: string
  ageRange: string
  description: string
  color: string
}

const AGE_OPTIONS: AgeOption[] = [
  {
    id: '0-3',
    emoji: '👶',
    label: 'Tots',
    ageRange: '0-3 years',
    description: 'Daycare & first snow play',
    color: '#FF6B6B', // coral
  },
  {
    id: '4-7',
    emoji: '🧒',
    label: 'Minis',
    ageRange: '4-7 years',
    description: 'Ski school & magic carpets',
    color: '#4ECDC4', // teal
  },
  {
    id: '8-12',
    emoji: '🧑',
    label: 'Riders',
    ageRange: '8-12 years',
    description: 'Building confidence & skills',
    color: '#FFE066', // gold
  },
  {
    id: '13+',
    emoji: '🧑‍🦱',
    label: 'Teens',
    ageRange: '13+ years',
    description: 'Independent explorers',
    color: '#95E1D3', // mint
  },
]

// Feedback messages based on selection
const FEEDBACK_MESSAGES: Record<string, string> = {
  'none': 'Tap the ages above to get started! 👆',
  '0-3': 'Tiny shredders! We\'ll find the coziest resorts 🍼',
  '4-7': 'Perfect for ski school adventures! ⛷️',
  '8-12': 'Time to explore the whole mountain! 🏔️',
  '13+': 'Ready for some serious terrain! 🎿',
  '0-3,4-7': 'A mix of little ones - we\'ve got you! 👨‍👩‍👧‍👦',
  '0-3,8-12': 'Quite the age range - we\'ll find balance! 🎯',
  '0-3,13+': 'From tots to teens - variety is key! 🌈',
  '4-7,8-12': 'Growing families unite! Perfect combo 🌟',
  '4-7,13+': 'Minis and teens? No problem! 💪',
  '8-12,13+': 'The active crew! Let\'s find some terrain 🏂',
  '0-3,4-7,8-12': 'Full house of young ones! 🏠',
  '0-3,4-7,13+': 'From babies to big kids! 👶➡️🧑‍🦱',
  '0-3,8-12,13+': 'Quite the spread! Challenge accepted 🎯',
  '4-7,8-12,13+': 'Growing family on the go! 🚀',
  'all': 'The whole gang! Let\'s find your perfect resort 🎉',
}

function getFeedbackMessage(selectedAges: AgeRange[]): string {
  if (selectedAges.length === 0) return FEEDBACK_MESSAGES['none']
  if (selectedAges.length === 4) return FEEDBACK_MESSAGES['all']

  const key = selectedAges.sort().join(',')
  return FEEDBACK_MESSAGES[key] || 'Great choices! Let\'s find your resort 🏔️'
}

interface AgeSelectorProps {
  initialSelection?: AgeRange[]
  onSelectionChange?: (ages: AgeRange[]) => void
  showCTA?: boolean
}

export function AgeSelector({
  initialSelection = [],
  onSelectionChange,
  showCTA = true
}: AgeSelectorProps) {
  const router = useRouter()
  const [selectedAges, setSelectedAges] = useState<AgeRange[]>(initialSelection)
  const [hasInteracted, setHasInteracted] = useState(false)

  // Load from session storage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = sessionStorage.getItem('snowthere_ages')
      if (stored) {
        try {
          const parsed = JSON.parse(stored)
          if (Array.isArray(parsed.selectedAges)) {
            setSelectedAges(parsed.selectedAges)
          }
        } catch (e) {
          // Ignore parsing errors
        }
      }
    }
  }, [])

  // Save to session storage on change
  useEffect(() => {
    if (typeof window !== 'undefined' && hasInteracted) {
      sessionStorage.setItem('snowthere_ages', JSON.stringify({
        selectedAges,
        timestamp: Date.now(),
      }))
      onSelectionChange?.(selectedAges)
    }
  }, [selectedAges, hasInteracted, onSelectionChange])

  const toggleAge = (ageId: AgeRange) => {
    setHasInteracted(true)
    setSelectedAges(prev => {
      if (prev.includes(ageId)) {
        return prev.filter(a => a !== ageId)
      }
      return [...prev, ageId]
    })
  }

  const handleFindResorts = () => {
    if (selectedAges.length === 0) {
      // Prompt to select at least one age
      return
    }

    // Navigate with query params
    const params = new URLSearchParams()
    if (selectedAges.length < 4) {
      params.set('ages', selectedAges.join(','))
    }

    router.push(`/resorts${params.toString() ? `?${params.toString()}` : ''}`)
  }

  const feedbackMessage = getFeedbackMessage(selectedAges)

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Title */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-6"
      >
        <h2 id="age-selector-title" className="font-display text-2xl md:text-3xl text-dark-700 mb-2">
          How old are your little shredders?
        </h2>
        <p id="age-selector-desc" className="text-dark-500 text-sm">
          Select all that apply - we&apos;ll find the perfect fit!
        </p>
      </motion.div>

      {/* Age Bubbles Grid */}
      <div
        role="group"
        aria-labelledby="age-selector-title"
        aria-describedby="age-selector-desc"
        className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
      >
        {AGE_OPTIONS.map((option, index) => (
          <AgeBubble
            key={option.id}
            emoji={option.emoji}
            label={option.label}
            ageRange={option.ageRange}
            description={option.description}
            color={option.color}
            isSelected={selectedAges.includes(option.id)}
            onToggle={() => toggleAge(option.id)}
            delay={index * 0.1}
          />
        ))}
      </div>

      {/* Feedback Message */}
      <motion.div
        key={feedbackMessage}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="text-center mb-6"
      >
        <p className="text-dark-600 font-medium text-lg">
          {feedbackMessage}
        </p>
      </motion.div>

      {/* CTA Button */}
      {showCTA && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-center"
        >
          <motion.button
            whileHover={{ scale: selectedAges.length > 0 ? 1.05 : 1 }}
            whileTap={{ scale: selectedAges.length > 0 ? 0.95 : 1 }}
            onClick={handleFindResorts}
            disabled={selectedAges.length === 0}
            className={`
              px-8 py-4 rounded-full font-bold text-lg
              transition-all duration-300
              ${selectedAges.length > 0
                ? 'bg-coral-500 text-white shadow-coral hover:shadow-coral-lg cursor-pointer'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }
            `}
          >
            <span className="flex items-center gap-2">
              {selectedAges.length > 0 ? (
                <>
                  Find Our Perfect Resort
                  <motion.span
                    animate={{ x: [0, 4, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  >
                    →
                  </motion.span>
                </>
              ) : (
                'Select ages to continue'
              )}
            </span>
          </motion.button>

          {/* Selection Summary */}
          {selectedAges.length > 0 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 text-sm text-dark-400"
            >
              Selected: {selectedAges.map(age => {
                const option = AGE_OPTIONS.find(o => o.id === age)
                return option?.ageRange
              }).join(', ')}
            </motion.p>
          )}
        </motion.div>
      )}
    </div>
  )
}
