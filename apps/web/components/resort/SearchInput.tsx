'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useRef, useCallback, useEffect, useState } from 'react'
import { Search, X } from 'lucide-react'

export function SearchInput({ placeholder = 'Search resorts...' }: { placeholder?: string }) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const initialQ = searchParams.get('q') || ''
  const [value, setValue] = useState(initialQ)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Keep in sync with URL when searchParams change externally
  useEffect(() => {
    setValue(searchParams.get('q') || '')
  }, [searchParams])

  const updateUrl = useCallback(
    (q: string) => {
      const params = new URLSearchParams(searchParams.toString())
      if (q) {
        params.set('q', q)
      } else {
        params.delete('q')
      }
      const qs = params.toString()
      router.push(qs ? `${pathname}?${qs}` : pathname, { scroll: false })
    },
    [router, pathname, searchParams]
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setValue(newValue)
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => updateUrl(newValue), 300)
  }

  const handleClear = () => {
    setValue('')
    updateUrl('')
  }

  return (
    <div className="flex-1 relative">
      <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400 pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full pl-14 pr-10 py-4 rounded-full bg-white border-2 border-dark-200 text-dark-800 placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-coral-400 focus:border-transparent shadow-card transition-all"
      />
      {value && (
        <button
          onClick={handleClear}
          className="absolute right-4 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-dark-100 transition-colors"
          aria-label="Clear search"
        >
          <X className="w-4 h-4 text-dark-400" />
        </button>
      )}
    </div>
  )
}
