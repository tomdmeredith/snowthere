'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Snowflake, ArrowRight, RefreshCw, Home } from 'lucide-react'
import { trackQuizComplete } from '@/lib/analytics'
import { Navbar } from '@/components/layout/Navbar'
import { PersonalityCard } from '@/components/quiz/PersonalityCard'
import { ResortMatchCard } from '@/components/quiz/ResortMatch'
import { QuizAnswers, QuizResult } from '@/lib/quiz/types'
import { computeQuizResults, getInitialAnswers } from '@/lib/quiz/scoring'
import { supabase } from '@/lib/supabase'

const STORAGE_KEY = 'snowthere_quiz_answers'

// Resort data shape needed for scoring
interface ResortForScoring {
  id: string
  name: string
  country: string
  region: string
  familyScore: number
  bestAgeMin: number
  bestAgeMax: number
  priceLevel: string
  hasSkiSchool?: boolean
  hasSkiInOut?: boolean
  nightlifeScore?: number
  nonSkiActivities?: number
  englishFriendly?: boolean
  snowReliability?: number
  beginnerTerrain?: number
  advancedTerrain?: number
  villageCharm?: number
  slug: string
}

// Type for Supabase query response with joins
interface ResortWithMetrics {
  id: string
  name: string
  slug: string
  country: string
  region: string | null
  resort_family_metrics: Array<{
    family_overall_score: number | null
    best_age_min: number | null
    best_age_max: number | null
    has_childcare: boolean | null
    kid_friendly_terrain_pct: number | null
  }> | null
  resort_costs: Array<{
    lodging_mid_nightly: number | null
    price_level: string | null
  }> | null
}

export default function QuizResultsPage() {
  const router = useRouter()
  const [answers, setAnswers] = useState<QuizAnswers | null>(null)
  const [result, setResult] = useState<QuizResult | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadResults() {
      // Get answers from sessionStorage
      const stored = sessionStorage.getItem(STORAGE_KEY)

      if (!stored) {
        // No answers stored, redirect to quiz start
        router.replace('/quiz')
        return
      }

      let parsedAnswers: QuizAnswers
      try {
        parsedAnswers = JSON.parse(stored)
      } catch (e) {
        console.error('Failed to parse stored answers:', e)
        router.replace('/quiz')
        return
      }

      // Validate that answers are complete
      if (!parsedAnswers.ages || !parsedAnswers.skill || !parsedAnswers.budget) {
        router.replace('/quiz')
        return
      }

      setAnswers(parsedAnswers)

      // Fetch published resorts with family metrics
      try {
        // Query resorts with their related metrics and costs
        const { data: resorts, error: fetchError } = await supabase
          .from('resorts')
          .select(`
            id,
            name,
            slug,
            country,
            region,
            resort_family_metrics (
              family_overall_score,
              best_age_min,
              best_age_max,
              has_childcare,
              kid_friendly_terrain_pct
            ),
            resort_costs (
              lodging_mid_nightly,
              price_level
            )
          `)
          .eq('status', 'published')

        if (fetchError) {
          throw fetchError
        }

        if (!resorts || resorts.length === 0) {
          setError('No resorts available yet. Check back soon!')
          setIsLoading(false)
          return
        }

        // Cast to our expected type
        const typedResorts = resorts as unknown as ResortWithMetrics[]

        // Transform to scoring format
        const resortsForScoring: ResortForScoring[] = typedResorts.map((resort) => {
          const metrics = resort.resort_family_metrics?.[0]
          const costs = resort.resort_costs?.[0]

          // Use database price_level if available, otherwise compute from lodging cost
          let priceLevel = costs?.price_level || null
          if (!priceLevel && costs?.lodging_mid_nightly) {
            const lodgingCost = costs.lodging_mid_nightly
            if (lodgingCost < 150) priceLevel = '$'
            else if (lodgingCost < 300) priceLevel = '$$'
            else if (lodgingCost < 500) priceLevel = '$$$'
            else priceLevel = '$$$$'
          }
          // Default to mid-range only if we have no data at all
          if (!priceLevel) priceLevel = '$$'

          return {
            id: resort.id,
            name: resort.name,
            slug: resort.slug,
            country: resort.country,
            region: resort.region || '',
            familyScore: metrics?.family_overall_score ?? 7,
            bestAgeMin: metrics?.best_age_min ?? 4,
            bestAgeMax: metrics?.best_age_max ?? 12,
            priceLevel,
            hasSkiSchool: metrics?.has_childcare ?? true,
            beginnerTerrain: metrics?.kid_friendly_terrain_pct ?? 25,
            advancedTerrain: 100 - (metrics?.kid_friendly_terrain_pct ?? 25) - 50,
          }
        })

        // Compute results
        const quizResult = computeQuizResults(parsedAnswers, resortsForScoring)
        setResult(quizResult)
      } catch (e) {
        console.error('Failed to fetch resorts:', e)
        setError('Something went wrong. Please try again.')
      }

      setIsLoading(false)
    }

    loadResults()
  }, [router])

  // Fire GA4 quiz_complete event when results are ready
  useEffect(() => {
    if (!result || result.topMatches.length === 0) return
    trackQuizComplete(result.topMatches.length, result.topMatches[0].slug)
  }, [result])

  const handleRetakeQuiz = () => {
    sessionStorage.removeItem(STORAGE_KEY)
    router.push('/quiz')
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF] flex items-center justify-center">
        <div className="text-center">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            className="inline-block mb-4"
          >
            <Snowflake className="w-16 h-16 text-coral-500" />
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-lg text-gray-600"
          >
            Finding your perfect matches...
          </motion.p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF] flex items-center justify-center px-4">
        <div className="bg-white rounded-3xl shadow-xl p-8 max-w-md text-center">
          <div className="text-4xl mb-4">😅</div>
          <h2 className="font-display text-2xl font-bold text-gray-900 mb-4">
            Oops!
          </h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={handleRetakeQuiz}
              className="inline-flex items-center justify-center gap-2 bg-coral-500 text-white px-6 py-3 rounded-full font-semibold hover:bg-coral-600 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Try Again
            </button>
            <Link
              href="/"
              className="inline-flex items-center justify-center gap-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-full font-semibold hover:bg-gray-200 transition-colors"
            >
              <Home className="w-4 h-4" />
              Go Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // No results state (shouldn&apos;t happen but just in case)
  if (!result) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]">
      {/* Navigation */}
      <Navbar />

      {/* Decorative floating elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-24 left-[10%] text-4xl opacity-50"
          animate={{ y: [0, -15, 0] }}
          transition={{ duration: 4, repeat: Infinity }}
        >
          🎉
        </motion.div>
        <motion.div
          className="absolute top-32 right-[15%] text-3xl opacity-50"
          animate={{ y: [0, 10, 0], rotate: [0, 10, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, delay: 0.5 }}
        >
          ⛷️
        </motion.div>
        <motion.div
          className="absolute bottom-40 left-[5%] text-3xl opacity-50"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 3, repeat: Infinity, delay: 1 }}
        >
          🏔️
        </motion.div>
        <motion.div
          className="absolute bottom-20 right-[8%] text-4xl opacity-50"
          animate={{ y: [0, 12, 0], rotate: [0, -5, 0] }}
          transition={{ duration: 4.5, repeat: Infinity, delay: 0.3 }}
        >
          ❄️
        </motion.div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">

        {/* Results Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-center mb-10"
        >
          <h1 className="font-display text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            Your Results Are In! 🎿
          </h1>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Based on your answers, here&apos;s your snow personality and the resorts that match your family best.
          </p>
        </motion.div>

        {/* Personality Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-2xl mx-auto mb-12"
        >
          <PersonalityCard personality={result.personality} />
        </motion.div>

        {/* Top Matches Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-12"
        >
          <h2 className="font-display text-2xl md:text-3xl font-bold text-gray-900 text-center mb-8">
            Your Top Resort Matches
          </h2>

          {result.topMatches.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {result.topMatches.map((match, index) => (
                <ResortMatchCard
                  key={match.id}
                  match={match}
                  rank={index + 1}
                  delay={0.5 + index * 0.15}
                  userAges={result.answers.ages}
                />
              ))}
            </div>
          ) : (
            <div className="text-center bg-white rounded-2xl shadow-lg p-8 max-w-md mx-auto">
              <p className="text-gray-600 mb-4">
                We&apos;re still adding resorts to our database. Check back soon for personalized matches!
              </p>
              <Link
                href="/resorts"
                className="inline-flex items-center gap-2 text-coral-500 font-semibold hover:text-coral-600"
              >
                Browse All Resorts
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center bg-white rounded-3xl shadow-xl p-8 md:p-10 max-w-2xl mx-auto"
        >
          <h3 className="font-display text-xl md:text-2xl font-bold text-gray-900 mb-4">
            Ready to Plan Your Trip?
          </h3>
          <p className="text-gray-600 mb-6">
            Dive deeper into your matched resorts with our complete family guides - everything you need to book the perfect ski vacation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/resorts">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="inline-flex items-center gap-2 bg-gradient-to-r from-coral-500 to-coral-600 text-white px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl hover:shadow-coral-500/25 transition-all duration-200"
              >
                Explore All Resorts
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            <button
              onClick={handleRetakeQuiz}
              className="inline-flex items-center gap-2 bg-gray-100 text-gray-700 px-8 py-4 rounded-xl font-semibold hover:bg-gray-200 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Retake Quiz
            </button>
          </div>
        </motion.div>

        {/* Share Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center mt-10 pb-8"
        >
          <p className="text-sm text-gray-500">
            Share your snow personality with friends! 🎿❄️
          </p>
        </motion.div>
      </div>
    </div>
  )
}
