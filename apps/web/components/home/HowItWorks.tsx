'use client'

import { motion } from 'framer-motion'

const STEPS = [
  {
    number: 1,
    emoji: '👶',
    title: 'Pick Your',
    highlight: 'Kids Ages',
    color: '#FFE066', // gold
    description: 'Select the ages of your little shredders',
  },
  {
    number: 2,
    emoji: '💰',
    title: 'Set Your',
    highlight: 'Budget',
    color: '#4ECDC4', // teal
    description: 'From budget-friendly to splurge-worthy',
  },
  {
    number: 3,
    emoji: '✈️',
    title: 'Plan &',
    highlight: 'Go!',
    color: '#FF6B6B', // coral
    description: 'Get your complete trip guide',
  },
]

export function HowItWorks() {
  return (
    <section className="py-20 sm:py-28 bg-gradient-to-br from-mint-50/50 via-white to-coral-50/30">
      <div className="container-page">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="font-display text-4xl sm:text-5xl font-bold tracking-tight text-dark-800">
            Easy as <span className="text-2xl sm:text-3xl">1️⃣</span>{' '}
            <span className="text-2xl sm:text-3xl">2️⃣</span>{' '}
            <span className="text-2xl sm:text-3xl">3️⃣</span>!{' '}
            <span className="text-3xl sm:text-4xl">🎉</span>
          </h2>
        </motion.div>

        {/* Steps */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12 lg:gap-16">
          {STEPS.map((step, index) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className="text-center group"
            >
              {/* Circle with number */}
              <motion.div
                whileHover={{ scale: 1.1, rotate: 5 }}
                className="relative mx-auto mb-6 w-24 h-24 sm:w-28 sm:h-28 rounded-full flex items-center justify-center transition-all duration-300"
                style={{
                  backgroundColor: step.color,
                  boxShadow: `0 8px 32px ${step.color}50`,
                }}
              >
                <span className="font-display text-4xl sm:text-5xl font-black text-white">
                  {step.number}
                </span>
              </motion.div>

              {/* Emoji */}
              <div className="text-4xl mb-4 group-hover:animate-bounce-emoji">
                {step.emoji}
              </div>

              {/* Text */}
              <h3 className="font-display text-xl font-semibold text-dark-700 mb-1">
                {step.title}
              </h3>
              <p
                className="font-display text-2xl font-bold mb-3"
                style={{ color: step.color }}
              >
                {step.highlight}
              </p>
              <p className="text-dark-500 text-sm max-w-[200px] mx-auto">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Connecting lines (visible on md+) */}
        <div className="hidden md:flex justify-center mt-[-200px] mb-[150px] relative z-0">
          <div className="flex items-center gap-[180px] lg:gap-[240px]">
            <div className="w-20 h-1 bg-gradient-to-r from-gold-400 to-teal-400 rounded-full" />
            <div className="w-20 h-1 bg-gradient-to-r from-teal-400 to-coral-400 rounded-full" />
          </div>
        </div>
      </div>
    </section>
  )
}
