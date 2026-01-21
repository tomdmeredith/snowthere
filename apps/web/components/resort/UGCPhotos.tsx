'use client'

import { useState, useRef, useEffect } from 'react'
import Image from 'next/image'
import { ChevronLeft, ChevronRight, Camera, Users, X } from 'lucide-react'
import { createSanitizedHTML } from '@/lib/sanitize'

interface UGCPhoto {
  url: string
  category?: string
  relevance_score?: number
  attributions?: string[]
  alt_text?: string
}

interface UGCPhotosProps {
  /**
   * Array of user-generated photos from Google Places
   */
  photos: UGCPhoto[]
  /**
   * Resort name for alt text
   */
  resortName: string
  /**
   * Optional section title
   */
  title?: string
  /**
   * Optional custom CSS classes
   */
  className?: string
}

/**
 * UGC Photos carousel component.
 *
 * Displays user-generated photos from Google Places in a horizontal
 * scrollable carousel. Shows social proof that real families visit
 * these resorts.
 *
 * Features:
 * - Horizontal scroll with snap points
 * - Navigation arrows on desktop
 * - Touch-friendly on mobile
 * - Lightbox for full-size viewing
 * - Attribution display for Google Places compliance
 */
export function UGCPhotos({
  photos,
  resortName,
  title = "Photos from Visitors",
  className = '',
}: UGCPhotosProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [canScrollLeft, setCanScrollLeft] = useState(false)
  const [canScrollRight, setCanScrollRight] = useState(true)
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null)

  // Check scroll position to show/hide arrows
  const checkScroll = () => {
    if (!scrollRef.current) return

    const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
    setCanScrollLeft(scrollLeft > 10)
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10)
  }

  useEffect(() => {
    checkScroll()
    const ref = scrollRef.current
    if (ref) {
      ref.addEventListener('scroll', checkScroll)
      return () => ref.removeEventListener('scroll', checkScroll)
    }
  }, [photos])

  const scroll = (direction: 'left' | 'right') => {
    if (!scrollRef.current) return

    const scrollAmount = scrollRef.current.clientWidth * 0.7
    scrollRef.current.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    })
  }

  // Don't render if no photos
  if (!photos || photos.length === 0) {
    return null
  }

  return (
    <section className={`relative ${className}`}>
      {/* Section Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-gold-100/60">
            <Users className="w-4 h-4 text-gold-600" />
          </div>
          <h2 className="font-display text-xl font-semibold text-dark-900">
            {title}
          </h2>
          <span className="text-sm text-gold-500">
            ({photos.length} photos)
          </span>
        </div>

        {/* Navigation Arrows (desktop) */}
        <div className="hidden sm:flex items-center gap-2">
          <button
            onClick={() => scroll('left')}
            disabled={!canScrollLeft}
            className="p-2 rounded-full bg-dark-50 hover:bg-dark-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-5 h-5 text-dark-700" />
          </button>
          <button
            onClick={() => scroll('right')}
            disabled={!canScrollRight}
            className="p-2 rounded-full bg-dark-50 hover:bg-dark-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-5 h-5 text-dark-700" />
          </button>
        </div>
      </div>

      {/* Photo Carousel */}
      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto scroll-smooth snap-x snap-mandatory scrollbar-hide pb-2"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {photos.map((photo, index) => (
          <button
            key={`${photo.url}-${index}`}
            onClick={() => setLightboxIndex(index)}
            className="relative flex-shrink-0 snap-start group"
          >
            <div className="relative w-40 sm:w-48 aspect-[4/3] rounded-xl overflow-hidden bg-gold-100">
              <Image
                src={photo.url}
                alt={photo.alt_text || `Visitor photo ${index + 1} at ${resortName}`}
                fill
                className="object-cover transition-transform duration-300 group-hover:scale-105"
                sizes="(max-width: 640px) 160px, 192px"
              />

              {/* Hover overlay */}
              <div className="absolute inset-0 bg-dark-900/0 group-hover:bg-dark-900/20 transition-colors" />

              {/* Category badge (if family-relevant) */}
              {photo.category === 'family' && (
                <div className="absolute top-2 left-2 px-2 py-1 rounded-full bg-gold-500/90 text-white text-[10px] font-medium">
                  Family
                </div>
              )}

              {/* Expand icon on hover */}
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="p-2 rounded-full bg-white/90 shadow-lg">
                  <Camera className="w-4 h-4 text-dark-800" />
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* Attribution (Google Places requirement) */}
      <p className="mt-3 text-[11px] text-gold-400 italic">
        Photos from Google Places. Posted by visitors.
      </p>

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <Lightbox
          photos={photos}
          currentIndex={lightboxIndex}
          resortName={resortName}
          onClose={() => setLightboxIndex(null)}
          onNavigate={setLightboxIndex}
        />
      )}
    </section>
  )
}

/**
 * Lightbox component for full-size photo viewing
 */
function Lightbox({
  photos,
  currentIndex,
  resortName,
  onClose,
  onNavigate,
}: {
  photos: UGCPhoto[]
  currentIndex: number
  resortName: string
  onClose: () => void
  onNavigate: (index: number) => void
}) {
  const photo = photos[currentIndex]

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      if (e.key === 'ArrowLeft' && currentIndex > 0) onNavigate(currentIndex - 1)
      if (e.key === 'ArrowRight' && currentIndex < photos.length - 1) onNavigate(currentIndex + 1)
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentIndex, photos.length, onClose, onNavigate])

  // Prevent body scroll when lightbox is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
    }
  }, [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-dark-900/95 backdrop-blur-sm"
      onClick={onClose}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
        aria-label="Close lightbox"
      >
        <X className="w-6 h-6 text-white" />
      </button>

      {/* Navigation */}
      {currentIndex > 0 && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onNavigate(currentIndex - 1)
          }}
          className="absolute left-4 p-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          aria-label="Previous photo"
        >
          <ChevronLeft className="w-6 h-6 text-white" />
        </button>
      )}
      {currentIndex < photos.length - 1 && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onNavigate(currentIndex + 1)
          }}
          className="absolute right-4 p-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          aria-label="Next photo"
        >
          <ChevronRight className="w-6 h-6 text-white" />
        </button>
      )}

      {/* Image */}
      <div
        className="relative max-w-[90vw] max-h-[85vh] aspect-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <Image
          src={photo.url}
          alt={photo.alt_text || `Visitor photo at ${resortName}`}
          width={1200}
          height={800}
          className="max-w-full max-h-[85vh] object-contain rounded-lg"
          priority
        />
      </div>

      {/* Counter */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm">
        <span className="text-sm text-white font-medium">
          {currentIndex + 1} / {photos.length}
        </span>
      </div>

      {/* Attribution */}
      {photo.attributions && photo.attributions.length > 0 && (
        <div className="absolute bottom-4 right-4">
          <div
            className="text-[10px] text-white/60"
            dangerouslySetInnerHTML={createSanitizedHTML(photo.attributions.join(' '))}
          />
        </div>
      )}
    </div>
  )
}

/**
 * Skeleton loader for UGC photos section
 */
export function UGCPhotosSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gold-100 animate-pulse" />
        <div className="w-40 h-6 rounded bg-gold-100 animate-pulse" />
      </div>
      <div className="flex gap-3 overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="flex-shrink-0 w-40 sm:w-48 aspect-[4/3] rounded-xl bg-gold-100 animate-pulse"
          />
        ))}
      </div>
    </div>
  )
}
