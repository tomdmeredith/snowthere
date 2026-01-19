'use client'

import { forwardRef, type HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * CHALET Design System - Badge Component
 *
 * Used for:
 * - Family score badges (crimson gradient)
 * - Status indicators (pine for positive, camel for warning)
 * - Category labels (slate muted)
 * - Highlight tags (camel subtle)
 *
 * Variants follow the CHALET color philosophy:
 * - score: Crimson - bold accent for the key family score
 * - success/perfect: Pine - nature's touch for positive states
 * - warning/skip: Camel - warm neutral for caution
 * - muted: Slate - cool counterpoint for secondary info
 * - highlight: Camel subtle - category tags on resort cards
 */

const badgeVariants = cva(
  // Base styles
  [
    'inline-flex items-center justify-center',
    'font-sans font-medium',
    'whitespace-nowrap',
    'transition-colors duration-200',
  ],
  {
    variants: {
      variant: {
        // Crimson score badge - bold family score display
        score: [
          'bg-crimson-500',
          'text-ivory-50',
          'shadow-md',
        ],
        // Pine success/perfect - positive indicators
        success: [
          'bg-pine-100',
          'text-pine-600',
          'border border-pine-200/50',
        ],
        // Camel warning/skip - caution indicators
        warning: [
          'bg-camel-100',
          'text-camel-600',
          'border border-camel-200/50',
        ],
        // Slate muted - secondary/neutral info
        muted: [
          'bg-slate-200/60',
          'text-slate-600',
        ],
        // Camel highlight - subtle category tags
        highlight: [
          'bg-camel-100',
          'text-camel-600',
        ],
        // Outline - espresso outlined style
        outline: [
          'bg-transparent',
          'text-espresso-700',
          'border border-espresso-700/30',
        ],
        // Pine solid - for strong positive emphasis
        pine: [
          'bg-pine-500',
          'text-ivory-50',
        ],
        // Crimson outline - secondary CTA style
        'crimson-outline': [
          'bg-transparent',
          'text-crimson-600',
          'border border-crimson-500',
        ],
      },
      size: {
        xs: 'px-2 py-0.5 text-xs rounded',
        sm: 'px-2.5 py-1 text-xs rounded-md',
        md: 'px-3 py-1.5 text-sm rounded-lg',
        lg: 'px-4 py-2 text-base rounded-xl',
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
 */
interface ScoreBadgeProps extends Omit<BadgeProps, 'variant' | 'size' | 'children'> {
  score: number
  maxScore?: number
  showMax?: boolean
}

const ScoreBadge = forwardRef<HTMLSpanElement, ScoreBadgeProps>(
  ({ className, score, maxScore = 10, showMax = true, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center',
          'bg-crimson-500 text-ivory-50',
          'px-3 py-1.5 rounded-full',
          'font-sans font-semibold text-sm',
          'shadow-md',
          className
        )}
        {...props}
      >
        {score}
        {showMax && <span className="opacity-80">/{maxScore}</span>}
      </span>
    )
  }
)

ScoreBadge.displayName = 'ScoreBadge'

export { Badge, ScoreBadge, badgeVariants }
