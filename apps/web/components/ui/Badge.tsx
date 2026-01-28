'use client'

import { forwardRef, type HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * SPIELPLATZ Design System - Badge Component
 * "Playful. Memorable. Fun."
 *
 * Used for:
 * - Family score badges (coral gradient)
 * - Status indicators (teal for positive, gold for warning)
 * - Category labels (dark muted)
 * - Highlight tags (gold subtle)
 *
 * Variants follow the SPIELPLATZ color philosophy:
 * - score: Coral - bold accent for the key family score
 * - success/perfect: Teal - fresh, vibrant positive states
 * - warning/skip: Gold - playful warm caution
 * - muted: Dark - neutral for secondary info
 * - highlight: Gold subtle - category tags on resort cards
 */

const badgeVariants = cva(
  // Base styles - Spielplatz playful precision
  // Design-5: Pill shapes (rounded-full) for all badges
  [
    'inline-flex items-center justify-center',
    'font-sans font-semibold',
    'whitespace-nowrap',
    'rounded-full', // Design-5: Pill shape by default
    'transition-all duration-300',
  ],
  {
    variants: {
      variant: {
        // Coral score badge - gradient for bold family score display (Design-5)
        score: [
          'bg-gradient-to-br from-coral-500 to-coral-600',
          'text-white',
          'shadow-coral',
          'hover:shadow-coral-lg hover:scale-105',
        ],
        // Large score - extra prominent for hero displays
        'score-lg': [
          'bg-gradient-to-br from-coral-500 via-coral-500 to-coral-600',
          'text-white',
          'shadow-coral-lg',
          'hover:shadow-coral-glow hover:scale-105',
        ],
        // Teal success/perfect - fresh positive indicators
        success: [
          'bg-teal-100',
          'text-teal-700',
          'border border-teal-200',
          'hover:bg-teal-200/70 hover:scale-105',
        ],
        // Perfect - stronger teal for "Perfect if" sections
        perfect: [
          'bg-gradient-to-br from-teal-400 to-teal-500',
          'text-white',
          'shadow-teal',
          'hover:shadow-teal-lg hover:scale-105',
        ],
        // Gold warning/skip - playful caution indicators
        warning: [
          'bg-gold-100',
          'text-gold-700',
          'border border-gold-200',
          'hover:bg-gold-200/70 hover:scale-105',
        ],
        // Skip - stronger gold for "Skip if" sections
        skip: [
          'bg-gradient-to-br from-gold-300 to-gold-400',
          'text-dark-700',
          'shadow-gold',
          'hover:shadow-gold-lg hover:scale-105',
        ],
        // Dark muted - secondary/neutral info
        muted: [
          'bg-dark-100',
          'text-dark-600',
          'hover:bg-dark-200/70 hover:scale-105',
        ],
        // Gold highlight - subtle category tags
        highlight: [
          'bg-gold-100',
          'text-gold-700',
          'hover:bg-gold-200/70 hover:scale-105',
        ],
        // Outline - dark outlined style
        outline: [
          'bg-transparent',
          'text-dark-700',
          'border border-dark-300',
          'hover:bg-dark-100 hover:border-dark-400 hover:scale-105',
        ],
        // Teal solid - for strong positive emphasis
        teal: [
          'bg-teal-500',
          'text-white',
          'shadow-teal',
          'hover:bg-teal-600 hover:shadow-teal-lg hover:scale-105',
        ],
        // Coral outline - secondary CTA style
        'coral-outline': [
          'bg-transparent',
          'text-coral-600',
          'border-2 border-coral-500',
          'hover:bg-coral-50 hover:scale-105',
        ],
        // Mint - soft accent for gentle highlights
        mint: [
          'bg-mint-100',
          'text-mint-700',
          'border border-mint-200',
          'hover:bg-mint-200/70 hover:scale-105',
        ],
      },
      size: {
        xs: 'px-2.5 py-0.5 text-xs',
        sm: 'px-3 py-1 text-xs',
        md: 'px-4 py-1.5 text-sm',
        lg: 'px-5 py-2 text-base',
        xl: 'px-6 py-2.5 text-lg', // Design-5: Extra large for hero scores
      },
    },
    defaultVariants: {
      variant: 'muted',
      size: 'sm',
    },
  }
)

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  /**
   * Optional icon to display before the label
   */
  icon?: React.ReactNode
}

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, size, icon, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant, size }), className)}
        {...props}
      >
        {icon && <span className="mr-1">{icon}</span>}
        {children}
      </span>
    )
  }
)

Badge.displayName = 'Badge'

/**
 * ScoreBadge - Specialized badge for family scores (1-10)
 * Displays as larger, more prominent badge with score number
 * Design-5: Gradient background, glow shadow, scale on hover
 */
interface ScoreBadgeProps extends Omit<BadgeProps, 'variant' | 'size' | 'children'> {
  score: number
  maxScore?: number
  showMax?: boolean
  /** Size variant for different contexts */
  badgeSize?: 'sm' | 'md' | 'lg' | 'xl'
}

const scoreBadgeSizes = {
  sm: 'px-3 py-1 text-sm min-w-[48px]',
  md: 'px-4 py-1.5 text-base min-w-[56px]',
  lg: 'px-5 py-2 text-lg min-w-[64px]',
  xl: 'px-6 py-3 text-xl min-w-[80px]', // Hero displays
}

const ScoreBadge = forwardRef<HTMLSpanElement, ScoreBadgeProps>(
  ({ className, score, maxScore = 10, showMax = true, badgeSize = 'md', ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center gap-0.5',
          'bg-gradient-to-br from-coral-500 to-coral-600',
          'text-white rounded-full',
          'font-sans font-bold',
          'shadow-coral',
          'transition-all duration-300',
          'hover:shadow-coral-lg hover:scale-105',
          scoreBadgeSizes[badgeSize],
          className
        )}
        {...props}
      >
        <span className="tabular-nums">{score.toFixed(1)}</span>
        {showMax && (
          <span className="opacity-70 font-medium">/{maxScore}</span>
        )}
      </span>
    )
  }
)

ScoreBadge.displayName = 'ScoreBadge'

/**
 * CategoryBadge - For resort category tags (e.g., "Family-Friendly", "Advanced")
 * Design-5: Subtle gold background, playful hover
 */
interface CategoryBadgeProps extends Omit<BadgeProps, 'variant' | 'size'> {
  category: string
}

const CategoryBadge = forwardRef<HTMLSpanElement, CategoryBadgeProps>(
  ({ className, category, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center',
          'bg-gold-100 text-gold-700',
          'px-3 py-1 rounded-full',
          'font-sans font-medium text-xs',
          'transition-all duration-300',
          'hover:bg-gold-200/70 hover:scale-105',
          className
        )}
        {...props}
      >
        {category}
      </span>
    )
  }
)

CategoryBadge.displayName = 'CategoryBadge'

/**
 * PassBadge - For ski pass tags (e.g., "Epic Pass", "Ikon Pass")
 * Design-5: Teal accent, subtle hover
 */
interface PassBadgeProps extends Omit<BadgeProps, 'variant' | 'size'> {
  passName: string
}

const PassBadge = forwardRef<HTMLSpanElement, PassBadgeProps>(
  ({ className, passName, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center',
          'bg-teal-100 text-teal-700',
          'px-3 py-1 rounded-full',
          'font-sans font-medium text-xs',
          'border border-teal-200',
          'transition-all duration-300',
          'hover:bg-teal-200/70 hover:scale-105',
          className
        )}
        {...props}
      >
        {passName}
      </span>
    )
  }
)

PassBadge.displayName = 'PassBadge'

export { Badge, ScoreBadge, CategoryBadge, PassBadge, badgeVariants }
