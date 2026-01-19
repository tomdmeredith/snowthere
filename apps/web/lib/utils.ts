import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge class names with tailwind-merge to handle conflicts
 * Commonly used with class-variance-authority
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
