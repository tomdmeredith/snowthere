'use client'

import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * SPIELPLATZ Design System - Button Component
 * "Playful. Memorable. Fun."
 *
 * Variants:
 * - primary: Coral gradient - energetic, playful CTAs
 * - secondary: Teal tones - fresh, vibrant secondary actions
 * - ghost: Transparent with border - subtle, clean feel
 * - outline: Dark outlined - for neutral actions
 * - gold: Playful highlight buttons
 *
 * Sizes:
 * - sm: Compact for inline use
 * - md: Default size
 * - lg: Large with generous touch targets (48px+ height)
 */

const buttonVariants = cva(
  // Base styles - Spielplatz playful precision
  // Design-5: rounded-full (pill), scale on hover, bouncy transitions
  [
    'inline-flex items-center justify-center gap-2',
    'font-sans font-semibold',
    'rounded-full', // Design-5: Pill shape by default
    'transition-all duration-300',
    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-white',
    'disabled:opacity-50 disabled:pointer-events-none',
    'touch-target', // 48px+ touch area from globals.css
  ],
  {
    variants: {
      variant: {
        // Coral primary - playful, energetic CTAs
        // Design-5: Scale + lift + shadow escalation on hover
        primary: [
          'bg-gradient-to-b from-coral-500 to-coral-600',
          'text-white',
          'shadow-coral',
          'hover:from-coral-600 hover:to-coral-700',
          'hover:shadow-coral-lg hover:-translate-y-1 hover:scale-105',
          'active:scale-[0.98] active:translate-y-0',
          'focus:ring-coral-400',
        ],
        // Teal secondary - fresh, vibrant
        secondary: [
          'bg-teal-500',
          'text-white',
          'shadow-teal',
          'hover:bg-teal-600',
          'hover:shadow-teal-lg hover:-translate-y-1 hover:scale-105',
          'active:scale-[0.98] active:translate-y-0',
          'focus:ring-teal-400',
        ],
        // Ghost - transparent with subtle border
        ghost: [
          'bg-transparent',
          'text-dark-700',
          'border border-dark-700/20',
          'hover:bg-dark-700/5',
          'hover:border-dark-700/30',
          'hover:scale-105',
          'focus:ring-dark-600',
        ],
        // Outline - dark outlined
        outline: [
          'bg-white',
          'text-dark-700',
          'border-2 border-dark-700',
          'hover:bg-dark-700',
          'hover:text-white',
          'hover:scale-105',
          'focus:ring-dark-600',
        ],
        // Teal - for positive/success actions
        teal: [
          'bg-teal-500',
          'text-white',
          'shadow-teal',
          'hover:bg-teal-600',
          'hover:shadow-teal-lg hover:-translate-y-1 hover:scale-105',
          'active:scale-[0.98] active:translate-y-0',
          'focus:ring-teal-400',
        ],
        // Gold - playful highlight buttons
        gold: [
          'bg-gold-400',
          'text-dark-800',
          'shadow-gold',
          'hover:bg-gold-500',
          'hover:shadow-gold-lg hover:-translate-y-1 hover:scale-105',
          'active:scale-[0.98] active:translate-y-0',
          'focus:ring-gold-400',
        ],
        // Light ghost - for dark backgrounds (hero overlays)
        'ghost-light': [
          'bg-transparent',
          'text-white',
          'border border-white/30',
          'hover:bg-white/10',
          'hover:border-white/50',
          'hover:scale-105',
          'focus:ring-white',
        ],
      },
      size: {
        sm: 'px-5 py-2.5 text-sm min-h-[40px]',
        md: 'px-7 py-3.5 text-base min-h-[48px]',
        lg: 'px-9 py-4.5 text-lg min-h-[56px]', // Ultra touch-friendly
      },
      fullWidth: {
        true: 'w-full',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      fullWidth: false,
    },
  }
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /**
   * Show loading spinner and disable button
   */
  isLoading?: boolean
  /**
   * Icon to display before the label
   */
  leftIcon?: React.ReactNode
  /**
   * Icon to display after the label
   */
  rightIcon?: React.ReactNode
  /**
   * Render as child element (for Link wrapping)
   */
  asChild?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      isLoading,
      leftIcon,
      rightIcon,
      disabled,
      children,
      asChild = false,
      ...props
    },
    ref
  ) => {
    // When asChild is true, Slot expects exactly one child element
    // Icons should be placed inside the child component by the consumer
    if (asChild) {
      return (
        <Slot
          ref={ref}
          className={cn(buttonVariants({ variant, size, fullWidth }), className)}
          {...props}
        >
          {children}
        </Slot>
      )
    }

    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, fullWidth }), className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="animate-spin w-4 h-4 border-2 border-current border-t-transparent rounded-full" />
        ) : (
          leftIcon
        )}
        {children}
        {!isLoading && rightIcon}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button, buttonVariants }
