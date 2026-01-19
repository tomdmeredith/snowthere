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
 * when no image is available. Matches the "Apres Ski" aesthetic with
 * soft gradients and editorial feel.
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
      {/* Main Hero Image */}
      <div className="relative aspect-[16/9] sm:aspect-[2.4/1] w-full overflow-hidden rounded-2xl sm:rounded-3xl">
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
            {/* Gradient overlay for text readability */}
            <div className="absolute inset-0 bg-gradient-to-t from-espresso-900/70 via-espresso-900/20 to-transparent" />
            <div className="absolute inset-0 bg-gradient-to-r from-espresso-900/30 to-transparent" />
          </>
        ) : (
          <HeroPlaceholder resortName={resortName} country={country} />
        )}

        {/* Content overlay */}
        <div className="absolute inset-0 flex flex-col justify-end p-6 sm:p-8 md:p-10">
          {/* Resort name and location */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-ivory-100/80">
              <MapPin className="w-4 h-4" />
              <span className="text-sm font-medium tracking-wide uppercase">
                {country}
              </span>
            </div>
            <h1 className="font-display text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight">
              {resortName}
            </h1>
          </div>

          {/* Family score badge */}
          {familyScore && (
            <div className="absolute top-6 right-6 sm:top-8 sm:right-8">
              <div className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-white/15 backdrop-blur-md border border-white/20 shadow-lg">
                <Sparkles className="w-4 h-4 text-camel-200" />
                <span className="font-display font-bold text-lg text-white">
                  {familyScore}
                </span>
                <span className="text-xs text-ivory-200/80 font-medium">
                  /10
                </span>
              </div>
            </div>
          )}

          {/* Image source attribution (subtle) */}
          {source && hasValidImage && (
            <div className="absolute bottom-3 right-3 sm:bottom-4 sm:right-4">
              <span className="text-[10px] text-ivory-100/40 font-medium">
                {source === 'official' ? 'Resort photo' : 'AI-generated'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Optional atmosphere thumbnail */}
      {hasAtmosphere && (
        <div className="absolute -bottom-4 right-4 sm:-bottom-6 sm:right-8 w-24 sm:w-32 aspect-square rounded-xl overflow-hidden border-4 border-ivory-50 shadow-xl">
          <Image
            src={atmosphereUrl}
            alt={`Atmosphere at ${resortName}`}
            fill
            className="object-cover"
            onError={() => setAtmosphereError(true)}
            sizes="128px"
          />
        </div>
      )}
    </div>
  )
}

/**
 * Stylized placeholder when no hero image is available.
 * Uses gradients and icons to create visual interest.
 */
function HeroPlaceholder({
  resortName,
  country,
}: {
  resortName: string
  country: string
}) {
  // Determine gradient based on country/region
  const getGradientClass = () => {
    const europeanCountries = ['austria', 'switzerland', 'france', 'italy', 'germany', 'norway', 'sweden']
    const isEuropean = europeanCountries.some(c =>
      country.toLowerCase().includes(c)
    )

    if (isEuropean) {
      // European: warmer, more traditional feel
      return 'from-camel-500 via-camel-600 to-espresso-800'
    }
    // Americas/Other: cooler, modern feel
    return 'from-slate-500 via-slate-600 to-espresso-800'
  }

  return (
    <div
      className={`absolute inset-0 bg-gradient-to-br ${getGradientClass()}`}
    >
      {/* Decorative mountain shapes */}
      <svg
        className="absolute bottom-0 left-0 right-0 h-1/2 text-espresso-900/20"
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
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Mountain icon */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="p-8 rounded-full bg-white/10 backdrop-blur-sm">
          <Mountain className="w-16 h-16 sm:w-20 sm:h-20 text-ivory-100/40" />
        </div>
      </div>

      {/* "Photo coming soon" indicator */}
      <div className="absolute top-4 left-4 sm:top-6 sm:left-6 flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/10 backdrop-blur-sm">
        <ImageOff className="w-3.5 h-3.5 text-ivory-100/60" />
        <span className="text-xs text-ivory-100/60 font-medium">
          Photo coming soon
        </span>
      </div>
    </div>
  )
}

/**
 * Skeleton loader for hero image
 */
export function HeroImageSkeleton() {
  return (
    <div className="relative aspect-[16/9] sm:aspect-[2.4/1] w-full overflow-hidden rounded-2xl sm:rounded-3xl bg-camel-100 animate-pulse">
      <div className="absolute inset-0 flex flex-col justify-end p-6 sm:p-8 md:p-10">
        <div className="space-y-3">
          <div className="h-4 w-24 bg-camel-200 rounded" />
          <div className="h-10 w-64 bg-camel-200 rounded" />
        </div>
      </div>
    </div>
  )
}
