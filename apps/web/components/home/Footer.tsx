'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'

const FOOTER_LINKS = [
  { href: '/about', label: 'About' },
  { href: '/methodology', label: 'Methodology' },
  { href: '/contact', label: 'Contact' },
  { href: '/privacy', label: 'Privacy' },
  { href: '/terms', label: 'Terms' },
]

// Social links hidden until accounts are created
// TODO: Add real social account URLs when ready
// const SOCIAL_LINKS = [
//   { href: 'https://instagram.com/snowthere', label: 'Instagram', emoji: '📸' },
//   { href: 'https://twitter.com/snowthere', label: 'Twitter', emoji: '🐦' },
//   { href: 'https://facebook.com/snowthere', label: 'Facebook', emoji: '📘' },
// ]

export function Footer() {
  return (
    <footer className="bg-dark-800 text-white py-16">
      <div className="container-page">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2">
            <motion.span
              className="text-2xl"
              animate={{ y: [0, -3, 0] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            >
              ❄️
            </motion.span>
            <span className="font-display text-2xl font-bold">
              <span className="text-white">snow</span>
              <span className="text-coral-400">there</span>
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <div className="flex flex-wrap justify-center gap-6 mb-8">
          {FOOTER_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-dark-300 hover:text-white transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Social icons - hidden until accounts are created */}
        {/* TODO: Uncomment when social accounts exist
        <div className="flex justify-center gap-6 mb-10">
          {SOCIAL_LINKS.map((link) => (
            <Link
              key={link.label}
              href={link.href}
              className="text-2xl hover:scale-125 transition-transform"
              aria-label={link.label}
            >
              {link.emoji}
            </Link>
          ))}
        </div>
        */}

        {/* Copyright */}
        <div className="text-center space-y-2">
          <p className="text-dark-400 text-sm">
            © {new Date().getFullYear()} snowthere. Made with ❄️
          </p>
          <p className="text-dark-500 text-xs">
            All ski pass and resort names are trademarks of their respective owners.{' '}
            <Link href="/terms#trademark-notice" className="underline hover:text-dark-300 transition-colors">
              Trademark notice
            </Link>
          </p>
        </div>
      </div>
    </footer>
  )
}
