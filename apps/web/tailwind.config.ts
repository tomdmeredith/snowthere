import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // ============================================
        // CHALET Design System - "Swiss precision in cashmere"
        // ============================================

        // IVORY - The Foundation
        // Not pure white - cream paper, Italian stationery feel
        ivory: {
          50: 'rgb(var(--ivory-50) / <alpha-value>)',   // #FFFDFA - main background
          100: 'rgb(var(--ivory-100) / <alpha-value>)', // #FCF9F4 - card backgrounds
          200: 'rgb(var(--ivory-200) / <alpha-value>)', // #F5F0E8 - subtle borders
        },

        // CAMEL / VICUÑA - Primary Warm Neutral
        // References cashmere, leather, natural wool - the luxury layer
        camel: {
          100: 'rgb(var(--camel-100) / <alpha-value>)', // #F4EADC - light wash
          200: 'rgb(var(--camel-200) / <alpha-value>)', // #E1D2BC - subtle accent
          400: 'rgb(var(--camel-400) / <alpha-value>)', // #C2AA8A - medium
          500: 'rgb(var(--camel-500) / <alpha-value>)', // #A88E6E - primary warm
          600: 'rgb(var(--camel-600) / <alpha-value>)', // #8E7658 - hover
        },

        // ESPRESSO - Text & Anchoring
        // Warmer than black, more sophisticated - dark roast, leather
        espresso: {
          600: 'rgb(var(--espresso-600) / <alpha-value>)', // #594837 - body text
          700: 'rgb(var(--espresso-700) / <alpha-value>)', // #443628 - headings
          800: 'rgb(var(--espresso-800) / <alpha-value>)', // #30261C - emphasis
          900: 'rgb(var(--espresso-900) / <alpha-value>)', // #201912 - overlays
        },

        // CRIMSON - "The Fire" Accent
        // NOT bright red - burgundy-adjacent, fireside warmth
        // This is our Swiss "bold moment" executed warm
        crimson: {
          400: 'rgb(var(--crimson-400) / <alpha-value>)', // #B45F50 - light
          500: 'rgb(var(--crimson-500) / <alpha-value>)', // #9E483A - primary CTA
          600: 'rgb(var(--crimson-600) / <alpha-value>)', // #8A3A2D - hover
          700: 'rgb(var(--crimson-700) / <alpha-value>)', // #702D23 - active
        },

        // SLATE - Cool Counterpoint
        // Mountains, sky, stone - provides contrast to warmth
        slate: {
          200: 'rgb(var(--slate-200) / <alpha-value>)', // #DCE0E6 - borders
          400: 'rgb(var(--slate-400) / <alpha-value>)', // #9EA8B6 - muted text
          500: 'rgb(var(--slate-500) / <alpha-value>)', // #768294 - secondary
          600: 'rgb(var(--slate-600) / <alpha-value>)', // #586476 - emphasis
        },

        // PINE - Nature's Touch
        // Evergreens, forest - success states, "perfect if"
        pine: {
          100: 'rgb(var(--pine-100) / <alpha-value>)', // #E8F0EC - success bg
          400: 'rgb(var(--pine-400) / <alpha-value>)', // #6C8A76 - accent
          500: 'rgb(var(--pine-500) / <alpha-value>)', // #4E6E58 - primary
          600: 'rgb(var(--pine-600) / <alpha-value>)', // #3A5844 - emphasis
        },
      },

      fontFamily: {
        // Plus Jakarta Sans - Swiss-inspired geometry with rounded terminals
        sans: ['var(--font-plus-jakarta)', 'system-ui', 'sans-serif'],
        // Fraunces - Distinctive "wonky" serifs, editorial warmth
        display: ['var(--font-fraunces)', 'Georgia', 'serif'],
        // Caveat - Handwritten warmth for personal moments
        accent: ['var(--font-caveat)', 'cursive'],
      },

      boxShadow: {
        // Warm-tinted shadows using espresso tones
        'soft': '0 2px 8px rgba(48, 38, 28, 0.04), 0 4px 16px rgba(48, 38, 28, 0.06)',
        'lifted': '0 4px 12px rgba(48, 38, 28, 0.06), 0 8px 24px rgba(48, 38, 28, 0.08)',
        // Accent shadows
        'camel': '0 4px 14px rgba(168, 142, 110, 0.15)',
        'crimson': '0 4px 14px rgba(158, 72, 58, 0.2)',
      },

      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },

      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out forwards',
        'float': 'float 8s ease-in-out infinite',
        'shimmer': 'shimmer 2s ease-in-out infinite',
      },

      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
      },

      backgroundImage: {
        // Subtle texture patterns for luxury feel
        'grain': `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)'/%3E%3C/svg%3E")`,
      },
    },
  },
  plugins: [typography],
}

export default config
