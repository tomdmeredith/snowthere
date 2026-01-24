'use client'

import { Map, Mountain, ExternalLink, Layers, Info, TrendingDown, TrendingUp, BarChart3 } from 'lucide-react'

interface DifficultyBreakdown {
  novice?: number
  easy?: number
  intermediate?: number
  advanced?: number
  expert?: number
  unknown?: number
}

interface TrailMapData {
  quality: 'full' | 'partial' | 'minimal' | 'none'
  piste_count: number
  lift_count: number
  center_coords?: [number, number]
  bbox?: [number, number, number, number]
  official_map_url?: string
  osm_attribution?: string
  confidence: number
  difficulty_breakdown?: DifficultyBreakdown
}

interface TrailMapProps {
  resortName: string
  country: string
  data?: TrailMapData | null
  latitude?: number
  longitude?: number
}

// Difficulty colors matching ski slope conventions
const difficultyColors: Record<string, { bg: string; text: string; label: string; icon: string }> = {
  novice: { bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Beginner', icon: '🟢' },
  easy: { bg: 'bg-sky-100', text: 'text-sky-700', label: 'Easy', icon: '🔵' },
  intermediate: { bg: 'bg-red-100', text: 'text-red-700', label: 'Intermediate', icon: '🔴' },
  advanced: { bg: 'bg-zinc-200', text: 'text-zinc-800', label: 'Advanced', icon: '⬛' },
  expert: { bg: 'bg-zinc-800', text: 'text-white', label: 'Expert', icon: '⬛⬛' },
}

// Quality badge styles - Spielplatz colors
const qualityStyles: Record<string, { bg: string; text: string; label: string }> = {
  full: { bg: 'bg-teal-100', text: 'text-teal-700', label: 'Full Coverage' },
  partial: { bg: 'bg-dark-100', text: 'text-dark-700', label: 'Partial Data' },
  minimal: { bg: 'bg-gold-100', text: 'text-gold-700', label: 'Limited Data' },
  none: { bg: 'bg-stone-100', text: 'text-stone-600', label: 'No Map Data' },
}

function DifficultyBar({ breakdown }: { breakdown: DifficultyBreakdown }) {
  const total = Object.values(breakdown).reduce((sum, count) => sum + (count || 0), 0)
  if (total === 0) return null

  const segments = Object.entries(breakdown)
    .filter(([_, count]) => count && count > 0)
    .map(([difficulty, count]) => ({
      difficulty,
      count: count || 0,
      percentage: ((count || 0) / total) * 100,
      ...difficultyColors[difficulty] || { bg: 'bg-stone-200', text: 'text-stone-600', label: difficulty, icon: '❓' },
    }))
    .sort((a, b) => {
      const order = ['novice', 'easy', 'intermediate', 'advanced', 'expert', 'unknown']
      return order.indexOf(a.difficulty) - order.indexOf(b.difficulty)
    })

  return (
    <div className="space-y-4">
      {/* Visual bar */}
      <div className="h-4 rounded-full overflow-hidden flex bg-stone-100">
        {segments.map((seg, i) => (
          <div
            key={seg.difficulty}
            className={`${seg.bg} ${i === 0 ? 'rounded-l-full' : ''} ${i === segments.length - 1 ? 'rounded-r-full' : ''}`}
            style={{ width: `${seg.percentage}%` }}
            title={`${seg.label}: ${seg.count} runs (${Math.round(seg.percentage)}%)`}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-5 gap-y-2">
        {segments.map((seg) => (
          <div key={seg.difficulty} className="flex items-center gap-2">
            <span className="text-base">{seg.icon}</span>
            <span className="text-sm text-dark-600">
              {seg.label}: <span className="font-medium text-dark-800">{seg.count}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function TrailMap({ resortName, country, data, latitude, longitude }: TrailMapProps) {
  // Generate OpenSkiMap URL
  const openSkiMapUrl = latitude && longitude
    ? `https://openskimap.org/?#${longitude},${latitude},14`
    : `https://openskimap.org/?#search/${encodeURIComponent(resortName)}`

  // Generate OpenStreetMap URL for fallback
  const osmUrl = latitude && longitude
    ? `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}#map=14/${latitude}/${longitude}`
    : `https://www.openstreetmap.org/search?query=${encodeURIComponent(`${resortName} ski resort ${country}`)}`

  const hasData = data && data.quality !== 'none'
  const hasOsmData = hasData && data.piste_count > 0
  const hasOnlyOfficialLink = hasData && data.piste_count === 0 && data.official_map_url
  const qualityStyle = qualityStyles[data?.quality || 'none'] || qualityStyles['none']

  return (
    <section id="trail-map" className="space-y-6">
      {/* Section Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-gold-100">
          <Map className="w-5 h-5 text-gold-600" />
        </div>
        <h2 className="font-display text-2xl font-semibold text-dark-800">
          Trail Map
        </h2>
        {data && (
          <span className={`px-3 py-1 text-sm rounded-full ${qualityStyle.bg} ${qualityStyle.text}`}>
            {qualityStyle.label}
          </span>
        )}
      </div>

      {/* Main Content Card */}
      <div className="card bg-dark-50/80 border-dark-200">
        {hasOnlyOfficialLink ? (
          /* Official link only - no OSM data */
          <div className="text-center py-8 space-y-6">
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 rounded-2xl bg-teal-100">
                <Map className="w-8 h-8 text-teal-600" />
              </div>
              <div>
                <p className="font-medium text-dark-700 mb-1">
                  Official Trail Map Available
                </p>
                <p className="text-sm text-dark-500">
                  View the official trail map from {resortName}.
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <a
                href={data.official_map_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-coral-500 hover:bg-coral-600 text-white font-semibold transition-colors shadow-coral"
              >
                <Map className="w-5 h-5" />
                View Trail Map
                <ExternalLink className="w-4 h-4 ml-1 opacity-70" />
              </a>

              <a
                href={openSkiMapUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-dark-50 text-dark-700 font-medium border border-dark-200 transition-colors"
              >
                Search OpenSkiMap
                <ExternalLink className="w-4 h-4 ml-1 opacity-70" />
              </a>
            </div>
          </div>
        ) : hasOsmData ? (
          <div className="space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-2xl bg-white/60">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <TrendingDown className="w-5 h-5 text-dark-600" />
                </div>
                <div className="font-display text-2xl font-bold text-dark-800">
                  {data.piste_count}
                </div>
                <div className="text-sm text-dark-500">Marked Runs</div>
              </div>

              <div className="text-center p-4 rounded-2xl bg-white/60">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-gold-600" />
                </div>
                <div className="font-display text-2xl font-bold text-dark-800">
                  {data.lift_count}
                </div>
                <div className="text-sm text-dark-500">Lifts</div>
              </div>

              {data.difficulty_breakdown && (
                <>
                  <div className="text-center p-4 rounded-2xl bg-white/60">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <BarChart3 className="w-5 h-5 text-teal-600" />
                    </div>
                    <div className="font-display text-2xl font-bold text-dark-800">
                      {(data.difficulty_breakdown.novice || 0) + (data.difficulty_breakdown.easy || 0)}
                    </div>
                    <div className="text-sm text-dark-500">Beginner Runs</div>
                  </div>

                  <div className="text-center p-4 rounded-2xl bg-white/60">
                    <div className="flex items-center justify-center gap-2 mb-2">
                      <Mountain className="w-5 h-5 text-gold-600" />
                    </div>
                    <div className="font-display text-2xl font-bold text-dark-800">
                      {Math.round(
                        ((data.difficulty_breakdown.novice || 0) + (data.difficulty_breakdown.easy || 0)) /
                        data.piste_count * 100
                      ) || 0}%
                    </div>
                    <div className="text-sm text-dark-500">Family Terrain</div>
                  </div>
                </>
              )}
            </div>

            {/* Difficulty Breakdown */}
            {data.difficulty_breakdown && (
              <div className="p-5 rounded-2xl bg-white/60">
                <h3 className="font-semibold text-dark-800 mb-4 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-dark-500" />
                  Terrain by Difficulty
                </h3>
                <DifficultyBar breakdown={data.difficulty_breakdown} />
              </div>
            )}

            {/* Map Links */}
            <div className="flex flex-col sm:flex-row gap-3">
              <a
                href={openSkiMapUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-dark-700 hover:bg-dark-800 text-white font-medium transition-colors"
              >
                <Map className="w-5 h-5" />
                View Interactive Trail Map
                <ExternalLink className="w-4 h-4 ml-1 opacity-70" />
              </a>

              {data.official_map_url && (
                <a
                  href={data.official_map_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl bg-white hover:bg-dark-50 text-dark-700 font-medium border border-dark-200 transition-colors"
                >
                  Official Trail Map
                  <ExternalLink className="w-4 h-4 ml-1 opacity-70" />
                </a>
              )}
            </div>

            {/* Attribution */}
            <p className="text-xs text-dark-400 flex items-center gap-1">
              <Info className="w-3 h-3" />
              {data.osm_attribution || '© OpenStreetMap contributors, ODbL'}
            </p>
          </div>
        ) : (
          /* Fallback: No OSM data available */
          <div className="text-center py-8 space-y-6">
            <div className="flex flex-col items-center gap-4">
              <div className="p-4 rounded-2xl bg-stone-100">
                <Mountain className="w-8 h-8 text-stone-400" />
              </div>
              <div>
                <p className="font-medium text-dark-700 mb-1">
                  Trail map data not yet available
                </p>
                <p className="text-sm text-dark-500">
                  Check the official resort website or OpenSkiMap for trail information.
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <a
                href={openSkiMapUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-dark-700 hover:bg-dark-800 text-white font-medium transition-colors"
              >
                <Map className="w-5 h-5" />
                Search OpenSkiMap
                <ExternalLink className="w-4 h-4 ml-1 opacity-70" />
              </a>

              <a
                href={osmUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-dark-50 text-dark-700 font-medium border border-dark-200 transition-colors"
              >
                View on OpenStreetMap
                <ExternalLink className="w-4 h-4 ml-1 opacity-70" />
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Family Tip */}
      {hasOsmData && data.difficulty_breakdown && (
        <div className="p-4 rounded-2xl bg-teal-50/70 border border-teal-100">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-xl bg-teal-100 flex-shrink-0">
              <Info className="w-4 h-4 text-teal-600" />
            </div>
            <div className="text-sm text-teal-800">
              <span className="font-medium">Family Tip:</span>{' '}
              {(data.difficulty_breakdown.novice || 0) + (data.difficulty_breakdown.easy || 0) >= 10 ? (
                <>
                  {resortName} has plenty of beginner-friendly terrain with{' '}
                  {(data.difficulty_breakdown.novice || 0) + (data.difficulty_breakdown.easy || 0)} green and blue runs.
                  Great for families with young or beginner skiers!
                </>
              ) : (data.difficulty_breakdown.intermediate || 0) > (data.difficulty_breakdown.easy || 0) ? (
                <>
                  This resort leans toward intermediate terrain. Best suited for families with kids who have
                  some skiing experience under their belt.
                </>
              ) : (
                <>
                  Trail variety here means something for everyone in the family, from beginners to more
                  experienced skiers.
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
