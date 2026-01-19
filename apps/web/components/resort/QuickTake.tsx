import { CheckCircle, AlertCircle, Sparkles } from 'lucide-react'

interface QuickTakeProps {
  content: string
  perfectIf: string[]
  skipIf: string[]
  familyScore?: number
}

export function QuickTake({ content, perfectIf, skipIf, familyScore }: QuickTakeProps) {
  return (
    <section id="quick-take" className="space-y-8">
      {/* Main Quick Take Card - CHALET editorial design */}
      <div className="relative overflow-hidden rounded-3xl p-8 sm:p-10 bg-gradient-to-br from-espresso-700 via-espresso-800 to-espresso-900">
        {/* Decorative gradient overlays */}
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-camel-400/10 to-transparent pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-1/3 h-1/2 bg-gradient-to-tr from-slate-400/8 to-transparent pointer-events-none" />

        <div className="relative z-10">
          {/* Header with score */}
          <div className="flex items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-2">
              <span className="h-px w-6 bg-crimson-400/60" />
              <span className="font-accent text-xl sm:text-2xl text-camel-200">
                The Quick Take
              </span>
            </div>

            {familyScore && (
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm border border-white/15">
                <Sparkles className="w-4 h-4 text-camel-200" />
                <span className="font-semibold text-ivory-100">
                  {familyScore}/10
                </span>
                <span className="text-sm text-ivory-200/70">family score</span>
              </div>
            )}
          </div>

          {/* Content */}
          <div
            className="text-lg leading-relaxed text-ivory-100/90 [&>p]:mb-4 [&>p:last-child]:mb-0 [&>strong]:text-ivory-50 [&>strong]:font-semibold"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        </div>
      </div>

      {/* Perfect If / Skip If Cards - CHALET pine/camel design */}
      {(perfectIf.length > 0 || skipIf.length > 0) && (
        <div className="grid gap-5 sm:grid-cols-2">
          {perfectIf.length > 0 && (
            <div className="card bg-pine-50/70 border-pine-100">
              <div className="flex items-center gap-2 mb-5">
                <div className="p-2 rounded-xl bg-pine-100">
                  <CheckCircle className="w-5 h-5 text-pine-600" />
                </div>
                <h3 className="font-display text-lg font-semibold text-pine-800">
                  Perfect if...
                </h3>
              </div>
              <ul className="space-y-3">
                {perfectIf.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-xl bg-white/60"
                  >
                    <CheckCircle className="w-4 h-4 text-pine-500 mt-0.5 flex-shrink-0" />
                    <span className="text-espresso-700 text-sm leading-relaxed">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {skipIf.length > 0 && (
            <div className="card bg-camel-50/70 border-camel-100">
              <div className="flex items-center gap-2 mb-5">
                <div className="p-2 rounded-xl bg-camel-100">
                  <AlertCircle className="w-5 h-5 text-camel-600" />
                </div>
                <h3 className="font-display text-lg font-semibold text-camel-700">
                  Maybe skip if...
                </h3>
              </div>
              <ul className="space-y-3">
                {skipIf.map((item, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-3 p-3 rounded-xl bg-white/60"
                  >
                    <AlertCircle className="w-4 h-4 text-camel-500 mt-0.5 flex-shrink-0" />
                    <span className="text-espresso-700 text-sm leading-relaxed">{item}</span>
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
