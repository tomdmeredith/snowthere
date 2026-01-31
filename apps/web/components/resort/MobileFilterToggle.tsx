'use client'

import { useState, useEffect, type ReactNode } from 'react'
import { useSearchParams } from 'next/navigation'
import { SlidersHorizontal, ChevronDown } from 'lucide-react'

interface MobileFilterToggleProps {
  activeCount: number
  children: ReactNode
}

export function MobileFilterToggle({ activeCount, children }: MobileFilterToggleProps) {
  const [isOpen, setIsOpen] = useState(false)
  const searchParams = useSearchParams()

  // Auto-close when filters change (user clicked a pill)
  useEffect(() => {
    setIsOpen(false)
  }, [searchParams])

  return (
    <div className="md:hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-controls="mobile-filter-panel"
        className="flex items-center gap-2 w-full py-1"
      >
        <SlidersHorizontal className="w-4 h-4 text-dark-500" />
        <span className="text-sm font-semibold text-dark-700">Filters</span>
        {activeCount > 0 && (
          <span className="px-1.5 py-0.5 text-xs font-bold bg-coral-100 text-coral-700 rounded-full">
            {activeCount}
          </span>
        )}
        <ChevronDown
          className={`w-4 h-4 text-dark-400 ml-auto transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>
      <div
        id="mobile-filter-panel"
        className={`grid transition-all duration-300 ease-out ${
          isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
        }`}
      >
        <div className="overflow-hidden">
          <div className="pt-3 pb-1 space-y-3">
            {children}
          </div>
        </div>
      </div>
    </div>
  )
}
