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
        // SPIELPLATZ Design System - "Playful. Memorable. Fun."
        // Inspired by Memphis design, Bauhaus, playground aesthetics
        // ============================================

        // CORAL - Primary Brand Color
        // Warm, energetic, the "there" in snowthere logo
        coral: {
          50: '#FFF0F0',
          100: '#FFE0E0',
          200: '#FFBDBD',
          300: '#FF9A9A',
          400: '#FF8080',
          500: '#FF6B6B',  // PRIMARY - Logo, CTAs, emphasis
          600: '#E85555',
          700: '#CC4040',
          800: '#A63333',
          900: '#802626',
        },

        // TEAL - Secondary Accent
        // Fresh, vibrant, success states
        teal: {
          50: '#E6FAF8',
          100: '#CCF5F1',
          200: '#99EBE3',
          300: '#66E1D5',
          400: '#4ECDC4',  // PRIMARY - Success, highlights
          500: '#3DB8AF',
          600: '#2D9A93',
          700: '#1E7B76',
          800: '#145C59',
          900: '#0A3D3B',
        },

        // GOLD - Playful Highlight
        // Warm yellow, badges, stars, playful accents
        gold: {
          50: '#FFFBEB',
          100: '#FFF7D6',
          200: '#FFEFAD',
          300: '#FFE785',
          400: '#FFE066',  // PRIMARY - Badges, highlights
          500: '#E6C84D',
          600: '#CCB033',
          700: '#A6901A',
          800: '#806F00',
          900: '#594D00',
        },

        // MINT - Soft Accent
        // Gentle, calming, backgrounds
        mint: {
          50: '#F0FBF8',
          100: '#E1F7F1',
          200: '#C3EFE3',
          300: '#A5E7D5',
          400: '#95E1D3',  // PRIMARY - Soft backgrounds
          500: '#7DD4C4',
          600: '#65C7B5',
          700: '#4DB9A6',
          800: '#359B8A',
          900: '#1D7D6E',
        },

        // DARK - Text & Anchoring
        // Deep charcoal, "snow" in logo
        dark: {
          50: '#F5F5F5',
          100: '#E0E0E0',
          200: '#B8B8B8',
          300: '#909090',
          400: '#686868',
          500: '#454545',
          600: '#363636',
          700: '#2D3436',  // PRIMARY - Body text, logo
          800: '#1E2324',
          900: '#0F1112',
        },

        // ============================================
        // CHALET Design System (Legacy - for reference)
        // "Swiss precision in cashmere"
        // ============================================

        // IVORY - The Foundation
        ivory: {
          50: 'rgb(var(--ivory-50) / <alpha-value>)',   // #FFFDFA
          100: 'rgb(var(--ivory-100) / <alpha-value>)', // #FCF9F4
          200: 'rgb(var(--ivory-200) / <alpha-value>)', // #F5F0E8
        },

        // CAMEL / VICUÑA - Primary Warm Neutral
        camel: {
          100: 'rgb(var(--camel-100) / <alpha-value>)', // #F4EADC
          200: 'rgb(var(--camel-200) / <alpha-value>)', // #E1D2BC
          400: 'rgb(var(--camel-400) / <alpha-value>)', // #C2AA8A
          500: 'rgb(var(--camel-500) / <alpha-value>)', // #A88E6E
          600: 'rgb(var(--camel-600) / <alpha-value>)', // #8E7658
        },

        // ESPRESSO - Text & Anchoring
        espresso: {
          600: 'rgb(var(--espresso-600) / <alpha-value>)', // #594837
          700: 'rgb(var(--espresso-700) / <alpha-value>)', // #443628
          800: 'rgb(var(--espresso-800) / <alpha-value>)', // #30261C
          900: 'rgb(var(--espresso-900) / <alpha-value>)', // #201912
        },

        // CRIMSON - "The Fire" Accent
        crimson: {
          400: 'rgb(var(--crimson-400) / <alpha-value>)', // #B45F50
          500: 'rgb(var(--crimson-500) / <alpha-value>)', // #9E483A
          600: 'rgb(var(--crimson-600) / <alpha-value>)', // #8A3A2D
          700: 'rgb(var(--crimson-700) / <alpha-value>)', // #702D23
        },

        // SLATE - Cool Counterpoint
        slate: {
          200: 'rgb(var(--slate-200) / <alpha-value>)', // #DCE0E6
          400: 'rgb(var(--slate-400) / <alpha-value>)', // #9EA8B6
          500: 'rgb(var(--slate-500) / <alpha-value>)', // #768294
          600: 'rgb(var(--slate-600) / <alpha-value>)', // #586476
        },

        // PINE - Nature's Touch
        pine: {
          100: 'rgb(var(--pine-100) / <alpha-value>)', // #E8F0EC
          400: 'rgb(var(--pine-400) / <alpha-value>)', // #6C8A76
          500: 'rgb(var(--pine-500) / <alpha-value>)', // #4E6E58
          600: 'rgb(var(--pine-600) / <alpha-value>)', // #3A5844
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
        // ============================================
        // SPIELPLATZ Shadows - Playful, colorful (Design-5 Reference)
        // "Sunset on snow" - warm, inviting, multi-tonal
        // ============================================

        // Coral shadows - energetic primary accent
        'coral': '0 4px 14px rgba(255, 107, 107, 0.25)',
        'coral-lg': '0 8px 24px rgba(255, 107, 107, 0.3)',
        'coral-glow': '0 0 24px rgba(255, 107, 107, 0.35), 0 8px 32px rgba(255, 107, 107, 0.2)',

        // Teal shadows - fresh secondary accent
        'teal': '0 4px 14px rgba(78, 205, 196, 0.25)',
        'teal-lg': '0 8px 24px rgba(78, 205, 196, 0.3)',
        'teal-glow': '0 0 24px rgba(78, 205, 196, 0.35), 0 8px 32px rgba(78, 205, 196, 0.2)',

        // Gold shadows - playful highlight
        'gold': '0 4px 14px rgba(255, 224, 102, 0.3)',
        'gold-lg': '0 8px 24px rgba(255, 224, 102, 0.4)',

        // Multi-color playful shadows - coral + teal combination (Design-5 signature)
        'playful': '0 4px 20px rgba(255, 107, 107, 0.15), 0 8px 32px rgba(78, 205, 196, 0.1)',
        'playful-lg': '0 10px 40px rgba(255, 107, 107, 0.2), 0 15px 50px rgba(78, 205, 196, 0.15)',
        'playful-xl': '0 15px 60px rgba(255, 107, 107, 0.25), 0 20px 70px rgba(78, 205, 196, 0.18)',

        // Card shadows - escalating on hover (Design-5 pattern)
        'card': '0 2px 8px rgba(45, 52, 54, 0.08), 0 4px 16px rgba(45, 52, 54, 0.06)',
        'card-hover': '0 8px 24px rgba(45, 52, 54, 0.12), 0 16px 48px rgba(45, 52, 54, 0.08)',
        'card-active': '0 12px 40px rgba(255, 107, 107, 0.15), 0 20px 60px rgba(45, 52, 54, 0.1)',

        // xl and 2xl shadows for design-5 escalation patterns
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

        // ============================================
        // CHALET Shadows (Legacy)
        // ============================================
        'soft': '0 2px 8px rgba(48, 38, 28, 0.04), 0 4px 16px rgba(48, 38, 28, 0.06)',
        'lifted': '0 4px 12px rgba(48, 38, 28, 0.06), 0 8px 24px rgba(48, 38, 28, 0.08)',
        'camel': '0 4px 14px rgba(168, 142, 110, 0.15)',
        'crimson': '0 4px 14px rgba(158, 72, 58, 0.2)',
      },

      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },

      animation: {
        // ============================================
        // SPIELPLATZ Animations - Playful, bouncy, fun
        // ============================================
        'bounce-in': 'bounceIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'bounce-subtle': 'bounceSubtle 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'wiggle': 'wiggle 0.5s ease-in-out',
        'wiggle-slow': 'wiggle 1s ease-in-out infinite',
        'card-tilt': 'cardTilt 0.3s ease-out forwards',
        'card-tilt-reverse': 'cardTiltReverse 0.3s ease-out forwards',
        'pop': 'pop 0.2s ease-out',
        'snowfall': 'snowfall 10s linear infinite',
        'confetti': 'confetti 2s ease-out forwards',
        'pulse-coral': 'pulseCoral 2s ease-in-out infinite',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        'slide-down': 'slideDown 0.3s ease-out forwards',

        // ============================================
        // Legacy Animations
        // ============================================
        'fade-in-up': 'fadeInUp 0.6s ease-out forwards',
        'float': 'float 8s ease-in-out infinite',
        'shimmer': 'shimmer 2s ease-in-out infinite',
      },

      keyframes: {
        // ============================================
        // SPIELPLATZ Keyframes
        // ============================================
        bounceIn: {
          '0%': { opacity: '0', transform: 'scale(0.3)' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        bounceSubtle: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(-3deg)' },
          '75%': { transform: 'rotate(3deg)' },
        },
        cardTilt: {
          '0%': { transform: 'rotate(0deg) translateY(0)' },
          '100%': { transform: 'rotate(2deg) translateY(-4px)' },
        },
        cardTiltReverse: {
          '0%': { transform: 'rotate(0deg) translateY(0)' },
          '100%': { transform: 'rotate(-2deg) translateY(-4px)' },
        },
        pop: {
          '0%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
          '100%': { transform: 'scale(1)' },
        },
        snowfall: {
          '0%': { transform: 'translateY(-100%) rotate(0deg)', opacity: '1' },
          '100%': { transform: 'translateY(100vh) rotate(360deg)', opacity: '0.3' },
        },
        confetti: {
          '0%': { transform: 'translateY(0) rotate(0deg)', opacity: '1' },
          '100%': { transform: 'translateY(-200px) rotate(720deg)', opacity: '0' },
        },
        pulseCoral: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(255, 107, 107, 0.4)' },
          '50%': { boxShadow: '0 0 0 10px rgba(255, 107, 107, 0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },

        // ============================================
        // Legacy Keyframes
        // ============================================
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
