'use client'

import { forwardRef, type HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * CHALET Design System - Card Component
 *
 * Cards are the primary content containers in the CHALET system.
 * They feature:
 * - Ivory backgrounds (not stark white)
 * - Warm-tinted shadows using espresso tones
 * - Generous rounded corners (24px+)
 * - Subtle borders in ivory/camel tones
 *
 * Variants:
 * - default: Ivory background with soft shadow
 * - elevated: Lifted appearance with stronger shadow
 * - outlined: Subtle border, no shadow
 * - feature: For featured/highlighted content (camel accent)
 */

const cardVariants = cva(
  // Base styles - warm, inviting, luxury feel
  [
    'rounded-2xl',
    'overflow-hidden',
    'transition-all duration-300 ease-out',
  ],
  {
    variants: {
      variant: {
        // Default - ivory bg with soft warm shadow
        default: [
          'bg-ivory-100',
          'shadow-soft',
          'border border-ivory-200',
        ],
        // Elevated - stronger lift effect
        elevated: [
          'bg-ivory-100',
          'shadow-lifted',
          'border border-ivory-200',
        ],
        // Outlined - subtle border, no shadow
        outlined: [
          'bg-ivory-50',
          'border border-camel-100',
        ],
        // Feature - camel accent border for highlights
        feature: [
          'bg-ivory-100',
          'shadow-soft',
          'border-2 border-camel-200',
        ],
        // Glass - subtle transparency for overlays
        glass: [
          'bg-ivory-100/80',
          'backdrop-blur-sm',
          'border border-ivory-200/50',
        ],
      },
      interactive: {
        true: [
          'cursor-pointer',
          'hover:shadow-lifted',
          'hover:-translate-y-1',
        ],
        false: '',
      },
      padding: {
        none: '',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8 md:p-10',
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
          'font-display text-xl text-espresso-700 leading-tight',
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
        className={cn('text-sm text-slate-500', className)}
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
