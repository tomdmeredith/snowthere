'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'

const NAV_LINKS = [
  { href: '/resorts', label: 'Resorts' },
  { href: '/guides', label: 'Guides' },
  { href: '/quiz', label: 'Quiz' },
  { href: '/about', label: 'About' },
]

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-dark-100">
      <div className="container-page">
        <div className="flex items-center justify-between h-16">
          {/* Logo with bouncing snowflake */}
          <Link href="/" className="flex items-center gap-2 group">
            <motion.span
              className="text-2xl"
              animate={{ y: [0, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            >
              ❄️
            </motion.span>
            <span className="font-display text-xl font-bold">
              <span className="text-dark-800">snow</span>
              <span className="text-coral-500">there</span>
            </span>
          </Link>

          {/* Desktop nav links with hover shapes */}
          <div className="hidden md:flex items-center gap-8">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="relative font-medium text-dark-600 hover:text-dark-800 transition-colors group"
              >
                {link.label}
                <motion.span
                  className="absolute -bottom-1 left-1/2 -translate-x-1/2 text-xs text-coral-400 opacity-0 group-hover:opacity-100 transition-opacity"
                  initial={{ scale: 0 }}
                  whileHover={{ scale: 1 }}
                >
                  ○
                </motion.span>
              </Link>
            ))}
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <Link
              href="/resorts"
              className="inline-flex items-center gap-2 bg-coral-500 hover:bg-coral-600 text-white px-6 py-2.5 rounded-full font-semibold shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all"
            >
              Let&apos;s Go!
              <motion.span
                animate={{ rotate: [0, 15, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                🎿
              </motion.span>
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 text-dark-600"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden py-4 border-t border-dark-100"
          >
            <div className="flex flex-col gap-4">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="font-medium text-dark-600 hover:text-coral-500 transition-colors px-2 py-2"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
              ))}
              <Link
                href="/resorts"
                className="inline-flex items-center justify-center gap-2 bg-coral-500 text-white px-6 py-3 rounded-full font-semibold mt-2"
                onClick={() => setMobileMenuOpen(false)}
              >
                Let&apos;s Go! 🎿
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </nav>
  )
}
