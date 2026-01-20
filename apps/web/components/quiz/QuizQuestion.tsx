'use client'

import { motion } from 'framer-motion'
import { QuizQuestion as QuizQuestionType } from '@/lib/quiz/types'
import { QuizOption } from './QuizOption'
import { TOTAL_STEPS } from '@/lib/quiz/questions'

interface QuizQuestionProps {
  question: QuizQuestionType
  selectedValue: string | string[] | null
  onSelect: (value: string) => void
  onNext: () => void
  onBack: () => void
  canGoBack: boolean
}

export function QuizQuestion({
  question,
  selectedValue,
  onSelect,
  onNext,
  onBack,
  canGoBack,
}: QuizQuestionProps) {
  const isMultiSelect = question.type === 'multi'
  const maxSelections = question.maxSelections || 3

  const isOptionSelected = (optionId: string) => {
    if (isMultiSelect && Array.isArray(selectedValue)) {
      return selectedValue.includes(optionId)
    }
    return selectedValue === optionId
  }

  const handleOptionSelect = (optionId: string) => {
    onSelect(optionId)
  }

  const canProceed = isMultiSelect
    ? true // Multi-select questions are optional
    : selectedValue !== null

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-500">
            Question {question.step} of {TOTAL_STEPS}
          </span>
          <span className="text-sm font-medium text-coral-500">
            {Math.round((question.step / TOTAL_STEPS) * 100)}%
          </span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-coral-400 to-coral-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${(question.step / TOTAL_STEPS) * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Question Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="text-center mb-8"
      >
        <h2 className="font-display text-3xl md:text-4xl font-semibold text-gray-900 mb-2">
          {question.title}
        </h2>
        <p className="text-gray-500 text-lg">
          {question.subtitle}
          {isMultiSelect && (
            <span className="text-coral-500 ml-1">(pick up to {maxSelections})</span>
          )}
        </p>
      </motion.div>

      {/* Options Grid */}
      <div className="grid gap-4 mb-8">
        {question.options.map((option, index) => (
          <QuizOption
            key={option.id}
            option={option}
            isSelected={isOptionSelected(option.id)}
            onSelect={() => handleOptionSelect(option.id)}
            delay={index * 0.08}
            isMultiSelect={isMultiSelect}
          />
        ))}
      </div>

      {/* Navigation Buttons */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex items-center justify-between"
      >
        {canGoBack ? (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onBack}
            className="px-6 py-3 text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            ← Back
          </motion.button>
        ) : (
          <div />
        )}

        <motion.button
          whileHover={canProceed ? { scale: 1.05 } : {}}
          whileTap={canProceed ? { scale: 0.95 } : {}}
          onClick={onNext}
          disabled={!canProceed && !isMultiSelect}
          className={`
            px-8 py-4 rounded-xl font-semibold text-lg
            transition-all duration-200 shadow-lg
            ${
              canProceed
                ? 'bg-gradient-to-r from-coral-500 to-coral-600 text-white hover:shadow-xl hover:shadow-coral-500/25'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }
          `}
        >
          {question.step === TOTAL_STEPS ? 'See My Results!' : 'Next →'}
        </motion.button>
      </motion.div>

      {/* Skip hint for multi-select */}
      {isMultiSelect && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center text-sm text-gray-400 mt-4"
        >
          {Array.isArray(selectedValue) && selectedValue.length === 0
            ? "You can skip this one if nothing's a must-have"
            : `${(selectedValue as string[])?.length || 0} selected`}
        </motion.p>
      )}
    </div>
  )
}
