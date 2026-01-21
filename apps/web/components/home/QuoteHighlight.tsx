'use client'

import { motion } from 'framer-motion'

interface HighlightedWord {
  text: string
  color: string
  rotate: number
}

const QUOTE_PARTS: (string | HighlightedWord)[] = [
  'The best family ski trips aren\'t about ',
  { text: 'perfect runs', color: '#4ECDC4', rotate: -1 },
  ' or ',
  { text: 'hot chocolate', color: '#FF6B6B', rotate: 1 },
  ' or even ',
  { text: 'silly photos', color: '#FFE066', rotate: -2 },
  '. They\'re about ',
  { text: 'being together', color: '#95E1D3', rotate: 1 },
  ' in the mountains.',
]

export function QuoteHighlight() {
  return (
    <section className="py-20 sm:py-28 bg-white">
      <div className="container-page">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center"
        >
          {/* Opening quote mark */}
          <span className="font-display text-8xl sm:text-9xl text-coral-200 leading-none block mb-4">
            &ldquo;
          </span>

          {/* Quote with highlighted words */}
          <p className="font-display text-2xl sm:text-3xl lg:text-4xl font-medium text-dark-700 leading-relaxed">
            {QUOTE_PARTS.map((part, index) => {
              if (typeof part === 'string') {
                return <span key={index}>{part}</span>
              }
              return (
                <motion.span
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.05 }}
                  className="inline-block px-3 py-1 mx-1 rounded-lg text-white"
                  style={{
                    backgroundColor: part.color,
                    transform: `rotate(${part.rotate}deg)`,
                  }}
                >
                  {part.text}
                </motion.span>
              )
            })}
          </p>

          {/* Closing quote mark */}
          <span className="font-display text-8xl sm:text-9xl text-coral-200 leading-none block mt-4 rotate-180">
            &rdquo;
          </span>
        </motion.div>
      </div>
    </section>
  )
}
