import { CheckCircle, AlertCircle, Sparkles } from 'lucide-react'
import { createSanitizedHTML } from '@/lib/sanitize'

interface QuickTakeProps {
  content: string
  perfectIf: string[]
  skipIf: string[]
  familyScore?: number
}

export function QuickTake({ content, perfectIf, skipIf, familyScore }: QuickTakeProps) {
  return (
    <section id="quick-take" className="space-y-8">
      {/* Main Quick Take Card - Design-5 playful editorial */}
      <div className="relative overflow-hidden p-8 sm:p-12 bg-gradient-to-br from-dark-700 via-dark-800 to-dark-900 shadow-2xl" style={{ borderRadius: '40px' }}>
        {/* Decorative gradient overlays - Design-5 playful accents */}
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-coral-400/15 to-transparent pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-1/3 h-1/2 bg-gradient-to-tr from-teal-400/10 to-transparent pointer-events-none" />
        <div className="absolute top-8 right-8 w-20 h-20 bg-coral-400/20 rounded-full blur-2xl" />
        <div className="absolute bottom-8 left-8 w-16 h-16 bg-teal-400/15 rounded-full blur-2xl" />

        <div className="relative z-10">
          {/* Header with score - Design-5 pill badge */}
          <div className="flex items-center justify-between gap-4 mb-8">
            <div className="flex items-center gap-3">
              <span className="h-1 w-8 bg-gradient-to-r from-coral-400 to-coral-500 rounded-full" />
              <span className="font-accent text-2xl sm:text-3xl text-gold-200">
                The Quick Take
              </span>
            </div>

            {familyScore && (
              <div className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-coral-500/20 to-coral-600/20 backdrop-blur-sm border border-coral-300/30 shadow-coral">
                <Sparkles className="w-5 h-5 text-gold-200" />
                <span className="font-bold text-lg text-white">
                  {familyScore}/10
                </span>
                <span className="text-sm text-white/70 font-medium">family score</span>
              </div>
            )}
          </div>

          {/* Content - Design-5 better typography */}
          <div
            className="text-lg sm:text-xl leading-relaxed text-white/90 [&>p]:mb-5 [&>p:last-child]:mb-0 [&>strong]:text-white [&>strong]:font-semibold"
            dangerouslySetInnerHTML={createSanitizedHTML(content)}
          />
        </div>
      </div>

      {/* Perfect If / Skip If Cards - Design-5 playful cards with shadows */}
      {(perfectIf.length > 0 || skipIf.length > 0) && (
        <div className="grid gap-6 sm:grid-cols-2">
          {perfectIf.length > 0 && (
            <div className="rounded-3xl p-6 sm:p-8 bg-gradient-to-br from-teal-50 to-mint-50/70 border border-teal-200 shadow-teal">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-teal-400 to-teal-500 shadow-teal">
                  <CheckCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-display text-xl font-bold text-teal-800">
                  Perfect if...
                </h3>
              </div>
              <ul className="space-y-3">
                {perfectIf.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-3 p-4 rounded-2xl bg-white/80 border border-teal-100 hover:bg-white hover:shadow-card transition-all duration-300"
                  >
                    <CheckCircle className="w-5 h-5 text-teal-500 mt-0.5 flex-shrink-0" />
                    <span className="text-dark-700 leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {skipIf.length > 0 && (
            <div className="rounded-3xl p-6 sm:p-8 bg-gradient-to-br from-gold-50 to-gold-100/50 border border-gold-200 shadow-gold">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-gold-400 to-gold-500 shadow-gold">
                  <AlertCircle className="w-5 h-5 text-dark-700" />
                </div>
                <h3 className="font-display text-xl font-bold text-gold-700">
                  Maybe skip if...
                </h3>
              </div>
              <ul className="space-y-3">
                {skipIf.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-3 p-4 rounded-2xl bg-white/80 border border-gold-100 hover:bg-white hover:shadow-card transition-all duration-300"
                  >
                    <AlertCircle className="w-5 h-5 text-gold-500 mt-0.5 flex-shrink-0" />
                    <span className="text-dark-700 leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
