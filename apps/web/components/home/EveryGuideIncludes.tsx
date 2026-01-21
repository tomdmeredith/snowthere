'use client'

import { motion } from 'framer-motion'
import { Heart, Ticket, CheckCircle, MapPin } from 'lucide-react'

const FEATURES = [
  {
    icon: Heart,
    title: 'Age-by-Age',
    description: 'Ski school minimums, childcare ages, teen terrain parks',
  },
  {
    icon: Ticket,
    title: 'Real Costs',
    description: 'Lift tickets, lodging tiers, family daily totals',
  },
  {
    icon: CheckCircle,
    title: 'Perfect If / Skip If',
    description: 'Quick verdict on who this resort is for',
  },
  {
    icon: MapPin,
    title: 'Getting There',
    description: 'Nearest airports, transfers, car vs shuttle',
  },
]

export function EveryGuideIncludes() {
  return (
    <section className="py-20 sm:py-28 bg-dark-800 text-white relative overflow-hidden">
      {/* Decorative gradient orbs */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-coral-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-20 right-10 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl" />

      <div className="container-page relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <span className="font-accent text-2xl text-gold-300 block mb-2">
            Every guide includes
          </span>
          <h2 className="font-display text-4xl sm:text-5xl font-bold tracking-tight">
            The Details That Matter
          </h2>
        </motion.div>

        {/* Feature grid */}
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4 max-w-5xl mx-auto">
          {FEATURES.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="text-center group"
            >
              <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-dark-700/80 border border-dark-600 group-hover:bg-dark-700 group-hover:border-gold-400/50 group-hover:scale-110 transition-all duration-300">
                <feature.icon className="w-8 h-8 text-gold-300" />
              </div>
              <h3 className="font-display font-semibold text-xl text-white">
                {feature.title}
              </h3>
              <p className="mt-3 text-dark-300 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
