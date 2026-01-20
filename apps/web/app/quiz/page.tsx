'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Snowflake, ArrowRight, Clock, Sparkles } from 'lucide-react'

export default function QuizPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-20 left-10 text-4xl"
          animate={{ y: [0, -10, 0], rotate: [0, 10, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          ❄️
        </motion.div>
        <motion.div
          className="absolute top-40 right-20 text-3xl"
          animate={{ y: [0, 10, 0], rotate: [0, -10, 0] }}
          transition={{ duration: 4, repeat: Infinity, delay: 0.5 }}
        >
          ⛷️
        </motion.div>
        <motion.div
          className="absolute bottom-40 left-20 text-3xl"
          animate={{ y: [0, -15, 0] }}
          transition={{ duration: 3.5, repeat: Infinity, delay: 1 }}
        >
          🏔️
        </motion.div>
        <motion.div
          className="absolute bottom-20 right-10 text-4xl"
          animate={{ y: [0, 8, 0], rotate: [0, 5, 0] }}
          transition={{ duration: 2.5, repeat: Infinity, delay: 0.3 }}
        >
          🎿
        </motion.div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-16 flex flex-col items-center justify-center min-h-screen">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <Link href="/" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-8 group">
            <Snowflake className="w-5 h-5 text-coral-500" />
            <span className="font-semibold">
              snow<span className="text-coral-500">there</span>
            </span>
          </Link>
        </motion.div>

        {/* Main Content Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-white rounded-3xl shadow-xl p-8 md:p-12 max-w-xl w-full text-center relative overflow-hidden"
        >
          {/* Decorative corner shapes */}
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-coral-100 rounded-full opacity-50" />
          <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-teal-100 rounded-full opacity-50" />

          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.4 }}
            className="relative z-10"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-coral-400 to-coral-500 rounded-full mb-6 shadow-lg">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="font-display text-3xl md:text-4xl font-bold text-gray-900 mb-4 relative z-10"
          >
            Snow Match Quiz
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="text-gray-600 text-lg mb-8 relative z-10"
          >
            Find your family&apos;s perfect ski resort match in under 2 minutes! Answer 7 quick questions and discover your snow personality.
          </motion.p>

          {/* Features */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="flex flex-wrap justify-center gap-4 mb-8 relative z-10"
          >
            <div className="flex items-center gap-2 bg-teal-50 text-teal-700 px-4 py-2 rounded-full text-sm">
              <Clock className="w-4 h-4" />
              <span>2 minutes</span>
            </div>
            <div className="flex items-center gap-2 bg-gold-50 text-gold-700 px-4 py-2 rounded-full text-sm">
              <span>🎯</span>
              <span>7 questions</span>
            </div>
            <div className="flex items-center gap-2 bg-coral-50 text-coral-700 px-4 py-2 rounded-full text-sm">
              <span>❤️</span>
              <span>Personalized results</span>
            </div>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="relative z-10"
          >
            <Link href="/quiz/1">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-coral-500 to-coral-600 text-white px-8 py-4 rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl hover:shadow-coral-500/25 transition-all duration-200"
              >
                Start the Quiz
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
          </motion.div>

          {/* Social proof */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="text-gray-400 text-sm mt-6 relative z-10"
          >
            Join 2,000+ families who found their perfect slope
          </motion.p>
        </motion.div>

        {/* What you'll discover */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="mt-12 text-center max-w-lg"
        >
          <h2 className="font-semibold text-gray-700 mb-4">What you&apos;ll discover:</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 shadow-sm">
              <div className="text-2xl mb-2">🎭</div>
              <p className="text-sm text-gray-600">Your snow personality type</p>
            </div>
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 shadow-sm">
              <div className="text-2xl mb-2">🏔️</div>
              <p className="text-sm text-gray-600">Top 3 resort matches</p>
            </div>
            <div className="bg-white/70 backdrop-blur-sm rounded-xl p-4 shadow-sm">
              <div className="text-2xl mb-2">💡</div>
              <p className="text-sm text-gray-600">Personalized tips</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
