import { CheckCircle, AlertCircle } from 'lucide-react'

interface QuickTakeProps {
  content: string
  perfectIf: string[]
  skipIf: string[]
}

export function QuickTake({ content, perfectIf, skipIf }: QuickTakeProps) {
  return (
    <section id="quick-take" className="space-y-6">
      {/* Main Quick Take Card */}
      <div className="quick-take">
        <div className="relative z-10">
          <span className="font-accent text-2xl text-glow-300">
            The Quick Take
          </span>

          <div
            className="mt-4 text-lg leading-relaxed text-cream-100 [&>p]:mb-4 [&>p:last-child]:mb-0"
            dangerouslySetInnerHTML={{ __html: content }}
          />
        </div>
      </div>

      {/* Perfect If / Skip If Cards */}
      {(perfectIf.length > 0 || skipIf.length > 0) && (
        <div className="grid gap-4 sm:grid-cols-2">
          {perfectIf.length > 0 && (
            <div className="card bg-forest-50 border-forest-200">
              <h3 className="font-display font-semibold text-forest-800 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-forest-500" />
                Perfect if...
              </h3>
              <ul className="space-y-3">
                {perfectIf.map((item, i) => (
                  <li
                    key={i}
                    className="condition-item perfect"
                  >
                    <CheckCircle className="w-4 h-4 text-forest-500 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-700">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {skipIf.length > 0 && (
            <div className="card bg-glow-50 border-glow-200">
              <h3 className="font-display font-semibold text-glow-800 mb-4 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-glow-500" />
                Skip it if...
              </h3>
              <ul className="space-y-3">
                {skipIf.map((item, i) => (
                  <li
                    key={i}
                    className="condition-item skip"
                  >
                    <AlertCircle className="w-4 h-4 text-glow-500 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-700">{item}</span>
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
