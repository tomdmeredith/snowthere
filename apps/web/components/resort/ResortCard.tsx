import Link from 'next/link'
import Image from 'next/image'
import { Mountain, MapPin } from 'lucide-react'
import { ScoreBadge } from '@/components/ui'
import { type ResortListItem, getPriceTierInfo, countryToSlug } from '@/lib/resort-filters'

interface ResortCardProps {
  resort: ResortListItem
  /** Override the country slug (useful for country pages) */
  countrySlug?: string
}

export function ResortCard({ resort, countrySlug }: ResortCardProps) {
  const slug = countrySlug || countryToSlug(resort.country)
  const heroImage =
    resort.images?.find((img) => img.image_type === 'hero')?.image_url ||
    resort.images?.find((img) => img.image_type === 'atmosphere')?.image_url ||
    resort.images?.[0]?.image_url

  const priceTier = getPriceTierInfo(resort.costs?.estimated_family_daily ?? null)

  return (
    <Link href={`/resorts/${slug}/${resort.slug}`} className="group">
      <div className="resort-card">
        {/* Hero image */}
        <div className="resort-card-image aspect-[16/9] bg-gradient-to-br from-teal-100 via-mint-100 to-teal-50 relative overflow-hidden">
          {heroImage ? (
            <Image
              src={heroImage}
              alt={`${resort.name} ski resort`}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Mountain className="w-14 h-14 text-teal-300 transition-transform duration-500" />
            </div>
          )}
        </div>

        <div className="p-6">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="font-display text-xl font-semibold text-dark-800 group-hover:text-coral-500 transition-colors">
                {resort.name}
              </h3>
              <p className="mt-1.5 text-dark-500 flex items-center gap-1.5">
                <MapPin className="w-4 h-4" />
                {resort.region ? `${resort.region}, ${resort.country}` : resort.country}
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${priceTier.isEstimated ? 'bg-gray-100 text-gray-500' : 'bg-gold-100 text-gold-700'}`}>
                {priceTier.tier}
              </span>
              {resort.family_metrics?.family_overall_score && (
                <ScoreBadge
                  score={resort.family_metrics.family_overall_score}
                  badgeSize="sm"
                  showMax={false}
                />
              )}
            </div>
          </div>

          {resort.content?.tagline && (
            <p className="mt-4 text-sm text-dark-500 italic">
              &ldquo;{resort.content.tagline}&rdquo;
            </p>
          )}
        </div>
      </div>
    </Link>
  )
}
