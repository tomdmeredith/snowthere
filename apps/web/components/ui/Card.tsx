'use client'

import { forwardRef, type HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * SPIELPLATZ Design System - Card Component
 * "Playful. Memorable. Fun."
 *
 * Cards are the primary content containers in SPIELPLATZ.
 * They feature:
 * - Clean white backgrounds
 * - Playful shadows with subtle color tints
 * - Generous rounded corners (16px+)
 * - Subtle borders in neutral tones
 *
 * Variants:
 * - default: White background with card shadow
 * - elevated: Lifted appearance with stronger shadow
 * - outlined: Subtle border, no shadow
 * - feature: For featured/highlighted content (gold accent)
 */

const cardVariants = cva(
  // Base styles - playful, clean, memorable
  // Design-5: rounded-3xl, shadow escalation on hover
  [
    'rounded-3xl', // Design-5: Bigger rounded corners
    'overflow-hidden',
    'transition-all duration-300',
  ],
  {
    variants: {
      variant: {
        // Default - white bg with card shadow
        default: [
          'bg-white',
          'shadow-card',
          'border border-dark-100',
        ],
        // Elevated - stronger lift effect
        elevated: [
          'bg-white',
          'shadow-card-hover',
          'border border-dark-100',
        ],
        // Outlined - subtle border, no shadow
        outlined: [
          'bg-white',
          'border border-dark-200',
        ],
        // Feature - coral accent border for highlights (Design-5)
        feature: [
          'bg-white',
          'shadow-card',
          'border-2 border-coral-300',
        ],
        // Glass - subtle transparency for overlays
        glass: [
          'bg-white/80',
          'backdrop-blur-sm',
          'border border-dark-100/50',
        ],
        // Warm - gradient background (Design-5 playful)
        warm: [
          'bg-gradient-to-br from-mint-50 to-coral-50/50',
          'border border-mint-200',
          'shadow-playful',
        ],
      },
      interactive: {
        // Design-5: Scale + lift + shadow escalation on hover
        true: [
          'cursor-pointer',
          'hover:shadow-card-active',
          'hover:-translate-y-2',
          'hover:scale-[1.02]',
          'hover:border-coral-200',
        ],
        false: '',
      },
      padding: {
        none: '',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8 md:p-10',
        xl: 'p-10 md:p-12', // Design-5: Extra generous padding
      },
    },
    defaultVariants: {
      variant: 'default',
      interactive: false,
      padding: 'none',
    },
  }
)

export interface CardProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, interactive, padding, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(cardVariants({ variant, interactive, padding }), className)}
        {...props}
      />
    )
  }
)

Card.displayName = 'Card'

/**
 * CardHeader - Top section of card with optional action area
 */
const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex flex-col space-y-1.5 p-6', className)}
        {...props}
      />
    )
  }
)

CardHeader.displayName = 'CardHeader'

/**
 * CardTitle - Card heading with Fraunces display font
 */
const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={cn(
          'font-display text-xl text-dark-700 leading-tight',
          className
        )}
        {...props}
      />
    )
  }
)

CardTitle.displayName = 'CardTitle'

/**
 * CardDescription - Subtitle/description text
 */
const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn('text-sm text-dark-400', className)}
        {...props}
      />
    )
  }
)

CardDescription.displayName = 'CardDescription'

/**
 * CardContent - Main content area
 */
const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('p-6 pt-0', className)}
        {...props}
      />
    )
  }
)

CardContent.displayName = 'CardContent'

/**
 * CardFooter - Bottom section, typically for actions
 */
const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-center p-6 pt-0', className)}
        {...props}
      />
    )
  }
)

CardFooter.displayName = 'CardFooter'

/**
 * CardImage - Image container with aspect ratio control
 */
interface CardImageProps extends HTMLAttributes<HTMLDivElement> {
  aspectRatio?: 'video' | 'square' | 'portrait' | 'wide'
}

const CardImage = forwardRef<HTMLDivElement, CardImageProps>(
  ({ className, aspectRatio = 'video', ...props }, ref) => {
    const aspectClasses = {
      video: 'aspect-video', // 16:9
      square: 'aspect-square', // 1:1
      portrait: 'aspect-[3/4]', // 3:4
      wide: 'aspect-[16/10]', // 16:10 (cards)
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative overflow-hidden',
          aspectClasses[aspectRatio],
          className
        )}
        {...props}
      />
    )
  }
)

CardImage.displayName = 'CardImage'

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  CardImage,
  cardVariants,
}
