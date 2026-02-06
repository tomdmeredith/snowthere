import Image from 'next/image'
import { AgeSelector } from './AgeSelector'

const HEADLINE_WORDS = [
  { text: 'WHERE', color: '#FF6B6B', rotate: -2 },
  { text: 'SHOULD', color: '#4ECDC4', rotate: 1 },
  { text: 'WE', color: '#FFE066', rotate: -1 },
  { text: 'SKI?', color: '#95E1D3', rotate: 3, outlined: true },
]

export function HeroSpielplatz() {
  return (
    <section className="relative overflow-hidden py-16 sm:py-20 lg:py-24">
      {/* Warm gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#FFF5E6] via-[#FFE8E8] to-[#E8F4FF]" />

      {/* Decorative bouncing emojis */}
      <div className="absolute top-20 left-[8%] animate-bounce-emoji" style={{ animationDelay: '0s' }}>
        <span className="text-4xl">⛷️</span>
      </div>
      <div className="absolute bottom-32 right-[12%] animate-bounce-emoji" style={{ animationDelay: '0.5s' }}>
        <span className="text-3xl">🎿</span>
      </div>
      <div className="absolute top-1/3 right-[5%] animate-bounce-emoji" style={{ animationDelay: '1s' }}>
        <span className="text-2xl">🏔️</span>
      </div>

      <div className="container-page relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Tilted Hero Image — server-rendered with CSS animation */}
          <div className="relative order-2 lg:order-1 animate-in animate-in-1" style={{ transform: 'rotate(-3deg)' }}>
            <div
              className="relative overflow-hidden rounded-3xl"
              style={{
                border: '8px solid #FFE066',
                boxShadow: '0 20px 60px rgba(255, 107, 107, 0.2), 0 10px 30px rgba(45, 52, 54, 0.1)',
              }}
            >
              <Image
                src="/images/generated/hero-snowy-family.png"
                alt="Family enjoying a ski vacation together"
                width={600}
                height={450}
                className="w-full h-auto object-cover"
                priority
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />
            </div>

            <div className="absolute -bottom-4 -right-4 bg-coral-500 text-white px-4 py-2 rounded-full font-semibold shadow-coral-lg transform rotate-3 animate-in animate-in-3">
              Adventure awaits! ✨
            </div>
          </div>

          {/* Right: Stacked Rotated Headline — server-rendered for SEO */}
          <div className="order-1 lg:order-2 text-center lg:text-left">
            {/* H1 visible in server HTML for crawlers — animate-in on inner spans only */}
            <h1 className="mb-8 space-y-1" aria-label="Where should we ski?">
              {HEADLINE_WORDS.map((word, index) => (
                <span
                  key={word.text}
                  className={`block animate-in animate-in-${index + 1}`}
                >
                  <span
                    className={`
                      font-display font-black text-5xl sm:text-6xl md:text-7xl lg:text-8xl
                      inline-block leading-[0.85]
                      ${word.outlined ? 'text-stroke-dark' : ''}
                    `}
                    style={{
                      color: word.outlined ? 'transparent' : word.color,
                      transform: `rotate(${word.rotate}deg)`,
                      display: 'inline-block',
                      WebkitTextStroke: word.outlined ? '3px #2D3436' : undefined,
                    }}
                  >
                    {word.text}
                  </span>
                </span>
              ))}
            </h1>

            <p className="text-lg sm:text-xl text-dark-600 max-w-md mx-auto lg:mx-0 mb-10 animate-in animate-in-3">
              The fun way to find your next family ski adventure
            </p>

            <div className="animate-in animate-in-4">
              <AgeSelector />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
