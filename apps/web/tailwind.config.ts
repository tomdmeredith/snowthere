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
        // Alpine Cream - Primary background, warm not clinical
        cream: {
          50: 'rgb(var(--cream-50) / <alpha-value>)',
          100: 'rgb(var(--cream-100) / <alpha-value>)',
          200: 'rgb(var(--cream-200) / <alpha-value>)',
          300: 'rgb(var(--cream-300) / <alpha-value>)',
        },
        // Alpenglow - Hero accent color, sunset on snow
        glow: {
          50: 'rgb(var(--glow-50) / <alpha-value>)',
          100: 'rgb(var(--glow-100) / <alpha-value>)',
          200: 'rgb(var(--glow-200) / <alpha-value>)',
          300: 'rgb(var(--glow-300) / <alpha-value>)',
          400: 'rgb(var(--glow-400) / <alpha-value>)',
          500: 'rgb(var(--glow-500) / <alpha-value>)',
          600: 'rgb(var(--glow-600) / <alpha-value>)',
          700: 'rgb(var(--glow-700) / <alpha-value>)',
        },
        // Forest Lodge - Deep, grounding, trustworthy
        forest: {
          50: 'rgb(var(--forest-50) / <alpha-value>)',
          100: 'rgb(var(--forest-100) / <alpha-value>)',
          200: 'rgb(var(--forest-200) / <alpha-value>)',
          300: 'rgb(var(--forest-300) / <alpha-value>)',
          400: 'rgb(var(--forest-400) / <alpha-value>)',
          500: 'rgb(var(--forest-500) / <alpha-value>)',
          600: 'rgb(var(--forest-600) / <alpha-value>)',
          700: 'rgb(var(--forest-700) / <alpha-value>)',
          800: 'rgb(var(--forest-800) / <alpha-value>)',
          900: 'rgb(var(--forest-900) / <alpha-value>)',
        },
        // Powder Slate - Text and contrast
        slate: {
          50: 'rgb(var(--slate-50) / <alpha-value>)',
          100: 'rgb(var(--slate-100) / <alpha-value>)',
          200: 'rgb(var(--slate-200) / <alpha-value>)',
          300: 'rgb(var(--slate-300) / <alpha-value>)',
          400: 'rgb(var(--slate-400) / <alpha-value>)',
          500: 'rgb(var(--slate-500) / <alpha-value>)',
          600: 'rgb(var(--slate-600) / <alpha-value>)',
          700: 'rgb(var(--slate-700) / <alpha-value>)',
          800: 'rgb(var(--slate-800) / <alpha-value>)',
          900: 'rgb(var(--slate-900) / <alpha-value>)',
        },
        // Golden Hour - Warm accents
        gold: {
          50: 'rgb(var(--gold-50) / <alpha-value>)',
          100: 'rgb(var(--gold-100) / <alpha-value>)',
          200: 'rgb(var(--gold-200) / <alpha-value>)',
          300: 'rgb(var(--gold-300) / <alpha-value>)',
          400: 'rgb(var(--gold-400) / <alpha-value>)',
          500: 'rgb(var(--gold-500) / <alpha-value>)',
          600: 'rgb(var(--gold-600) / <alpha-value>)',
          700: 'rgb(var(--gold-700) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['var(--font-dm-sans)', 'system-ui', 'sans-serif'],
        display: ['var(--font-fraunces)', 'Georgia', 'serif'],
        accent: ['Caveat', 'cursive'],
      },
      boxShadow: {
        'soft': '0 4px 6px rgba(42, 50, 56, 0.04), 0 8px 16px rgba(42, 50, 56, 0.06)',
        'lifted': '0 8px 16px rgba(42, 50, 56, 0.06), 0 16px 32px rgba(42, 50, 56, 0.08)',
        'glow': '0 4px 14px rgba(255, 122, 92, 0.3)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [typography],
}

export default config
