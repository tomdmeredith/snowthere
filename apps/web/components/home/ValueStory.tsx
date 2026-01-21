'use client'

import { motion } from 'framer-motion'
import { MapPin, Globe, Check } from 'lucide-react'

export function ValueStory() {
  return (
    <section className="py-20 sm:py-28 bg-white border-y border-dark-100">
      <div className="container-page">
        <div className="mx-auto max-w-4xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-14"
          >
            <span className="font-accent text-2xl text-teal-500 block mb-4">
              The open secret
            </span>
            <h2 className="font-display text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-dark-800 leading-tight">
              A week in the Alps often costs less than
              <span className="relative inline-block mx-2">
                <span className="relative z-10">a weekend at Vail</span>
                <span className="absolute bottom-1 left-0 right-0 h-4 bg-coral-200/60 -z-10 rounded" />
              </span>
            </h2>
          </motion.div>

          {/* Comparison cards */}
          <div className="grid md:grid-cols-2 gap-8 mb-14">
            {/* Colorado card */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              whileHover={{ y: -4 }}
              className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-gold-50 to-gold-100/50 border-2 border-gold-200 p-8 transition-all duration-300 hover:shadow-gold"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 rounded-2xl bg-gold-200">
                  <MapPin className="w-6 h-6 text-gold-700" />
                </div>
                <span className="font-display text-xl font-bold text-dark-800">
                  Colorado Weekend
                </span>
              </div>
              <div className="space-y-3 text-dark-600">
                <div className="flex justify-between items-center">
                  <span>Lift tickets (2 days)</span>
                  <span className="font-semibold text-dark-700">$1,000</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Lodging (2 nights)</span>
                  <span className="font-semibold text-dark-700">$800</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Meals</span>
                  <span className="font-semibold text-dark-700">$400</span>
                </div>
                <div className="flex justify-between items-center pt-4 mt-4 border-t-2 border-gold-300">
                  <span className="font-semibold text-dark-800">Family of 4 total</span>
                  <span className="font-bold text-xl text-dark-800">$2,200+</span>
                </div>
              </div>
            </motion.div>

            {/* Alps card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              whileHover={{ y: -4 }}
              className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-teal-50 to-mint-100/50 border-2 border-teal-200 p-8 transition-all duration-300 hover:shadow-teal"
            >
              {/* Better value badge */}
              <div className="absolute top-4 right-4">
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-teal-500 text-white">
                  <Check className="w-3.5 h-3.5" />
                  Better value
                </span>
              </div>
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 rounded-2xl bg-teal-200">
                  <Globe className="w-6 h-6 text-teal-700" />
                </div>
                <span className="font-display text-xl font-bold text-dark-800">
                  Austrian Alps Week
                </span>
              </div>
              <div className="space-y-3 text-dark-600">
                <div className="flex justify-between items-center">
                  <span>Lift tickets (6 days)</span>
                  <span className="font-semibold text-teal-700">$450</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Lodging (6 nights)</span>
                  <span className="font-semibold text-teal-700">$900</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Meals</span>
                  <span className="font-semibold text-teal-700">$600</span>
                </div>
                <div className="flex justify-between items-center pt-4 mt-4 border-t-2 border-teal-300">
                  <span className="font-semibold text-dark-800">Family of 4 total</span>
                  <span className="font-bold text-xl text-teal-600">$1,950</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Conclusion */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center text-lg text-dark-600 max-w-2xl mx-auto leading-relaxed"
          >
            The tricky part? Knowing which European resorts actually work for families.
            That&apos;s what we spent <span className="font-semibold text-dark-800">hundreds of hours</span> researching.
          </motion.p>
        </div>
      </div>
    </section>
  )
}
