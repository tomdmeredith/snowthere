'use client'

import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * CHALET Design System - Button Component
 *
 * Variants:
 * - primary: Crimson gradient - "the bold moment" for primary CTAs
 * - secondary: Camel tones - warm, inviting secondary actions
 * - ghost: Transparent with border - subtle, editorial feel
 * - outline: Espresso outlined - for neutral actions
 *
 * Sizes:
 * - sm: Compact for inline use
 * - md: Default size
 * - lg: Large with generous touch targets (48px+ height)
 */

const buttonVariants = cva(
  // Base styles - Swiss precision meets warmth
  [
    'inline-flex items-center justify-center gap-2',
    'font-sans font-semibold',
    'rounded-xl',
    'transition-all duration-200 ease-out',
    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-ivory-50',
    'disabled:opacity-50 disabled:pointer-events-none',
    'touch-target', // 48px+ touch area from globals.css
  ],
  {
    variants: {
      variant: {
        // Crimson primary - "The Fire" accent, bold CTAs
        primary: [
          'bg-gradient-to-b from-crimson-500 to-crimson-600',
          'text-ivory-50',
          'shadow-crimson',
          'hover:from-crimson-600 hover:to-crimson-700',
          'hover:shadow-lg hover:-translate-y-0.5',
          'active:translate-y-0',
          'focus:ring-crimson-400',
        ],
        // Camel secondary - warm, inviting
        secondary: [
          'bg-camel-500',
          'text-ivory-50',
          'shadow-camel',
          'hover:bg-camel-600',
          'hover:shadow-lg hover:-translate-y-0.5',
          'active:translate-y-0',
          'focus:ring-camel-400',
        ],
        // Ghost - transparent with subtle border
        ghost: [
          'bg-transparent',
          'text-espresso-700',
          'border border-espresso-700/20',
          'hover:bg-espresso-700/5',
          'hover:border-espresso-700/30',
          'focus:ring-espresso-600',
        ],
        // Outline - espresso outlined
        outline: [
          'bg-ivory-50',
          'text-espresso-700',
          'border-2 border-espresso-700',
          'hover:bg-espresso-700',
          'hover:text-ivory-50',
          'focus:ring-espresso-600',
        ],
        // Pine - for positive/success actions
        pine: [
          'bg-pine-500',
          'text-ivory-50',
          'hover:bg-pine-600',
          'hover:shadow-lg hover:-translate-y-0.5',
          'active:translate-y-0',
          'focus:ring-pine-400',
        ],
        // Light ghost - for dark backgrounds (hero overlays)
        'ghost-light': [
          'bg-transparent',
          'text-ivory-100',
          'border border-ivory-100/30',
          'hover:bg-ivory-100/10',
          'hover:border-ivory-100/50',
          'focus:ring-ivory-100',
        ],
      },
      size: {
        sm: 'px-4 py-2 text-sm min-h-[36px]',
        md: 'px-6 py-3 text-base min-h-[44px]',
        lg: 'px-8 py-4 text-lg min-h-[52px]', // Ultra touch-friendly
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
