'use client'

import { motion } from 'framer-motion'
import { Coffee, Ticket, Users } from 'lucide-react'

const FEATURES = [
  {
    icon: Coffee,
    title: 'Print & Go Ready',
    description: 'Everything in one place: ski school ages, lunch spots with high chairs, where to grab groceries. Print it and you\'re set.',
    color: '#FFE066', // gold
    bgColor: 'bg-gold-100',
    hoverBg: 'group-hover:bg-gold-200',
    iconColor: 'text-gold-600',
  },
  {
    icon: Ticket,
    title: 'Honest Cost Breakdowns',
    description: 'Real lift ticket prices, lodging ranges by budget, and a family of four daily estimate. No surprises.',
    color: '#2D3436', // dark
    bgColor: 'bg-dark-100',
    hoverBg: 'group-hover:bg-dark-200',
    iconColor: 'text-dark-600',
  },
  {
    icon: Users,
    title: 'Age-Specific Details',
    description: 'Ski school from age 3, childcare from 18 months, magic carpets, "kids ski free" policies. The details that matter.',
    color: '#4ECDC4', // teal
    bgColor: 'bg-teal-100',
    hoverBg: 'group-hover:bg-teal-200',
    iconColor: 'text-teal-600',
  },
]

export function WhatMakesUsDifferent() {
  return (
    <section className="py-20 sm:py-28 bg-gradient-to-br from-mint-50/50 via-white to-coral-50/30">
      <div className="container-page">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-14"
        >
          <span className="font-accent text-2xl text-teal-500 block mb-2">
            What makes us different
          </span>
          <h2 className="font-display text-4xl sm:text-5xl font-bold tracking-tight text-dark-800">
            Trip Guides That Feel Like a Friend&apos;s Advice
          </h2>
        </motion.div>

        {/* Feature cards */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto">
          {FEATURES.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="card card-lift group p-8"
            >
              <div
                className={`mb-5 flex h-14 w-14 items-center justify-center rounded-2xl ${feature.bgColor} ${feature.hoverBg} group-hover:scale-110 transition-all duration-300`}
              >
                <feature.icon className={`w-7 h-7 ${feature.iconColor}`} />
              </div>
              <h3 className="font-display text-xl font-semibold text-dark-800 mb-3">
                {feature.title}
              </h3>
              <p className="text-dark-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
