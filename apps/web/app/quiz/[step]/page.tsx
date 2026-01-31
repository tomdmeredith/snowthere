'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { Snowflake } from 'lucide-react'
import { QuizQuestion } from '@/components/quiz/QuizQuestion'
import { QUIZ_QUESTIONS, TOTAL_STEPS } from '@/lib/quiz/questions'
import { QuizAnswers } from '@/lib/quiz/types'
import { getInitialAnswers } from '@/lib/quiz/scoring'

const STORAGE_KEY = 'snowthere_quiz_answers'

export default function QuizStepPage() {
  const router = useRouter()
  const params = useParams()
  const step = parseInt(params.step as string, 10)

  const [answers, setAnswers] = useState<QuizAnswers>(getInitialAnswers())
  const [isLoaded, setIsLoaded] = useState(false)

  // Load answers from sessionStorage on mount
  useEffect(() => {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        setAnswers(JSON.parse(stored))
      } catch (e) {
        console.error('Failed to parse stored answers:', e)
      }
    } else {
      // Pre-populate ages from homepage AgeSelector if user hasn't started quiz yet
      const homepageAges = sessionStorage.getItem('snowthere_ages')
      if (homepageAges) {
        try {
          const parsed = JSON.parse(homepageAges)
          if (Array.isArray(parsed.selectedAges) && parsed.selectedAges.length > 0) {
            setAnswers((prev) => ({ ...prev, ages: parsed.selectedAges[0] }))
          }
        } catch (e) {
          // Ignore parsing errors
        }
      }
    }
    setIsLoaded(true)
  }, [])

  // Save answers to sessionStorage whenever they change
  useEffect(() => {
    if (isLoaded) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(answers))
    }
  }, [answers, isLoaded])

  // Validate step number
  if (step < 1 || step > TOTAL_STEPS || isNaN(step)) {
    router.replace('/quiz')
    return null
  }

  const question = QUIZ_QUESTIONS.find((q) => q.step === step)

  if (!question) {
    router.replace('/quiz')
    return null
  }

  const questionKey = question.id as keyof QuizAnswers
  const currentValue = answers[questionKey]

  const handleSelect = (optionId: string) => {
    if (question.type === 'multi') {
      // Multi-select logic
      const currentArray = (currentValue as string[]) || []
      const maxSelections = question.maxSelections || 3

      if (currentArray.includes(optionId)) {
        // Deselect
        setAnswers({
          ...answers,
          [questionKey]: currentArray.filter((id) => id !== optionId),
        })
      } else if (currentArray.length < maxSelections) {
        // Select (if under limit)
        setAnswers({
          ...answers,
          [questionKey]: [...currentArray, optionId],
        })
      }
    } else {
      // Single-select logic
      setAnswers({
        ...answers,
        [questionKey]: optionId,
      })
    }
  }

  const handleNext = () => {
    if (step === TOTAL_STEPS) {
      // Navigate to results
      router.push('/quiz/results')
    } else {
      // Navigate to next question
      router.push(`/quiz/${step + 1}`)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      router.push(`/quiz/${step - 1}`)
    } else {
      router.push('/quiz')
    }
  }

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF] flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <Snowflake className="w-12 h-12 text-coral-500" />
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]">
      {/* Decorative floating elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-10 left-[10%] text-3xl opacity-50"
          animate={{ y: [0, -15, 0] }}
          transition={{ duration: 4, repeat: Infinity }}
        >
          ❄️
        </motion.div>
        <motion.div
          className="absolute top-20 right-[15%] text-2xl opacity-50"
          animate={{ y: [0, 10, 0], rotate: [0, 10, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, delay: 0.5 }}
        >
          ⛷️
        </motion.div>
        <motion.div
          className="absolute bottom-20 left-[5%] text-2xl opacity-50"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 3, repeat: Infinity, delay: 1 }}
        >
          🏔️
        </motion.div>
        <motion.div
          className="absolute bottom-32 right-[8%] text-3xl opacity-50"
          animate={{ y: [0, 12, 0], rotate: [0, -5, 0] }}
          transition={{ duration: 4.5, repeat: Infinity, delay: 0.3 }}
        >
          🎿
        </motion.div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8 min-h-screen flex flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <Link
            href="/quiz"
            className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 group"
          >
            <Snowflake className="w-5 h-5 text-coral-500" />
            <span className="font-semibold">
              snow<span className="text-coral-500">there</span>
            </span>
          </Link>
        </motion.div>

        {/* Main content */}
        <div className="flex-1 flex items-center justify-center py-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
              className="w-full"
            >
              <QuizQuestion
                question={question}
                selectedValue={currentValue}
                onSelect={handleSelect}
                onNext={handleNext}
                onBack={handleBack}
                canGoBack={step > 1}
              />
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Footer hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center pb-8"
        >
          <p className="text-sm text-gray-400">
            Your answers help us find the perfect resort for your family ✨
          </p>
        </motion.div>
      </div>
    </div>
  )
}
