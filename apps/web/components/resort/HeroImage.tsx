'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Mountain, ImageOff, Sparkles, MapPin } from 'lucide-react'

interface HeroImageProps {
  /**
   * Primary hero image URL (AI-generated or official)
   */
  imageUrl?: string | null
  /**
   * Alt text for accessibility
   */
  altText?: string
  /**
   * Resort name for fallback display
   */
  resortName: string
  /**
   * Country for fallback display
   */
  country: string
  /**
   * Optional family score badge
   */
  familyScore?: number
  /**
   * Optional atmosphere image for secondary display
   */
  atmosphereUrl?: string | null
  /**
   * Image source for attribution
   */
  source?: 'gemini' | 'glif' | 'replicate' | 'official' | null
  /**
   * Custom CSS classes
   */
  className?: string
}

/**
 * Hero Image component for resort pages.
 *
 * Displays the main hero image with fallback to a stylized placeholder
 * when no image is available. Matches the SPIELPLATZ aesthetic with
 * soft gradients and playful feel.
 */
export function HeroImage({
  imageUrl,
  altText,
  resortName,
  country,
  familyScore,
  atmosphereUrl,
  source,
  className = '',
}: HeroImageProps) {
  const [imageError, setImageError] = useState(false)
  const [atmosphereError, setAtmosphereError] = useState(false)

  const hasValidImage = imageUrl && !imageError
  const hasAtmosphere = atmosphereUrl && !atmosphereError

  return (
    <div className={`relative ${className}`}>
      {/* Main Hero Image - Design-5 */}
      <div className="relative aspect-[16/9] sm:aspect-[2.4/1] w-full overflow-hidden shadow-2xl" style={{ borderRadius: '32px' }}>
        {hasValidImage ? (
          <>
            <Image
              src={imageUrl}
              alt={altText || `${resortName} ski resort in ${country}`}
              fill
              priority
              className="object-cover"
              onError={() => setImageError(true)}
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 90vw, 1200px"
            />
            {/* Design-5: Warm gradient overlays */}
            <div className="absolute inset-0 bg-gradient-to-t from-dark-900/80 via-dark-900/30 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-r from-dark-900/40 via-transparent to-coral-900/10" />
            {/* Decorative warm glow */}
            <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-gradient-to-tr from-coral-500/10 to-transparent pointer-events-none" />
          </>
        ) : (
          <HeroPlaceholder resortName={resortName} country={country} />
        )}

        {/* Content overlay - Design-5 */}
        <div className="absolute inset-0 flex flex-col justify-end p-8 sm:p-10 md:p-12">
          {/* Resort name and location */}
          <div className="space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-white/20 backdrop-blur-sm">
                <MapPin className="w-4 h-4 text-white" />
              </div>
              <span className="text-sm font-semibold tracking-wider uppercase text-white/90">
                {country}
              </span>
            </div>
            <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-white leading-[0.95] tracking-tight">
              {resortName}
            </h1>
          </div>

          {/* Family score badge - Design-5 coral gradient */}
          {familyScore && (
            <div className="absolute top-8 right-8 sm:top-10 sm:right-10">
              <div className="flex items-center gap-2 px-5 py-3 rounded-full bg-gradient-to-r from-coral-500/90 to-coral-600/90 backdrop-blur-md border border-white/20 shadow-coral">
                <Sparkles className="w-5 h-5 text-white" />
                <span className="font-display font-black text-2xl text-white">
                  {familyScore}
                </span>
              </div>
            </div>
          )}

          {/* Image source attribution (subtle) */}
          {source && hasValidImage && (
            <div className="absolute bottom-4 right-4 sm:bottom-5 sm:right-5">
              <span className="text-[10px] text-white/50 font-medium px-2.5 py-1 rounded-full bg-white/10 backdrop-blur-sm">
                {source === 'official' ? 'Resort photo' : 'AI-generated'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Optional atmosphere thumbnail - Design-5 */}
      {hasAtmosphere && (
        <div className="absolute -bottom-5 right-6 sm:-bottom-8 sm:right-10 w-28 sm:w-36 aspect-square rounded-2xl overflow-hidden border-4 border-white shadow-2xl hover:scale-105 transition-transform duration-300">
          <Image
            src={atmosphereUrl}
            alt={`Atmosphere at ${resortName}`}
            fill
            className="object-cover"
            onError={() => setAtmosphereError(true)}
            sizes="144px"
          />
        </div>
      )}
    </div>
  )
}

/**
 * Stylized placeholder when no hero image is available.
 * Uses Design-5 gradients and icons to create visual interest.
 */
function HeroPlaceholder({
  resortName,
  country,
}: {
  resortName: string
  country: string
}) {
  // Design-5: Warm gradient based on country/region
  const getGradientClass = () => {
    const europeanCountries = ['austria', 'switzerland', 'france', 'italy', 'germany', 'norway', 'sweden']
    const isEuropean = europeanCountries.some(c =>
      country.toLowerCase().includes(c)
    )

    if (isEuropean) {
      // European: warmer, golden hour feel
      return 'from-coral-500 via-gold-600 to-dark-800'
    }
    // Americas/Other: cool with warm accent
    return 'from-teal-600 via-dark-600 to-dark-800'
  }

  return (
    <div
      className={`absolute inset-0 bg-gradient-to-br ${getGradientClass()}`}
    >
      {/* Design-5: Decorative gradient orbs */}
      <div className="absolute top-10 right-10 w-40 h-40 bg-coral-400/20 rounded-full blur-3xl" />
      <div className="absolute bottom-20 left-10 w-32 h-32 bg-gold-400/15 rounded-full blur-3xl" />

      {/* Decorative mountain shapes */}
      <svg
        className="absolute bottom-0 left-0 right-0 h-1/2 text-dark-900/20"
        viewBox="0 0 1200 400"
        preserveAspectRatio="xMidYMax slice"
      >
        <path
          d="M0,400 L0,300 L200,200 L400,280 L600,150 L800,250 L1000,180 L1200,260 L1200,400 Z"
          fill="currentColor"
        />
        <path
          d="M0,400 L0,350 L300,250 L500,320 L700,220 L900,300 L1200,220 L1200,400 Z"
          fill="currentColor"
          opacity="0.5"
        />
      </svg>

      {/* Subtle texture overlay */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Mountain icon - Design-5 playful styling */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="p-10 rounded-full bg-white/10 backdrop-blur-sm border border-white/10">
          <Mountain className="w-20 h-20 sm:w-24 sm:h-24 text-white/30" />
        </div>
      </div>

      {/* "Photo coming soon" indicator - Design-5 pill */}
      <div className="absolute top-6 left-6 sm:top-8 sm:left-8 flex items-center gap-2.5 px-4 py-2 rounded-full bg-white/15 backdrop-blur-md border border-white/10">
        <ImageOff className="w-4 h-4 text-white/70" />
        <span className="text-xs text-white/70 font-semibold">
          Photo coming soon
        </span>
      </div>
    </div>
  )
}

/**
 * Skeleton loader for hero image - Design-5
 */
export function HeroImageSkeleton() {
  return (
    <div className="relative aspect-[16/9] sm:aspect-[2.4/1] w-full overflow-hidden bg-gradient-to-br from-coral-100 via-gold-50 to-mint-100 animate-pulse shadow-xl" style={{ borderRadius: '32px' }}>
      {/* Decorative shimmer elements */}
      <div className="absolute top-10 right-10 w-32 h-32 bg-coral-200/50 rounded-full blur-2xl" />
      <div className="absolute bottom-10 left-10 w-24 h-24 bg-teal-200/40 rounded-full blur-2xl" />

      <div className="absolute inset-0 flex flex-col justify-end p-8 sm:p-10 md:p-12">
        <div className="space-y-4">
          <div className="h-5 w-28 bg-coral-200/60 rounded-full" />
          <div className="h-12 w-72 bg-coral-200/60 rounded-2xl" />
        </div>
      </div>

      {/* Score badge skeleton */}
      <div className="absolute top-8 right-8 sm:top-10 sm:right-10">
        <div className="h-12 w-28 bg-coral-200/60 rounded-full" />
      </div>
    </div>
  )
}
