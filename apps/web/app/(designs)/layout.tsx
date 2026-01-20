import type { Metadata } from 'next'
import { Plus_Jakarta_Sans, Fraunces, Caveat, Cormorant_Garamond, Space_Grotesk, Playfair_Display, Source_Serif_4, Archivo_Black } from 'next/font/google'
import '../globals.css'

// CHALET Typography
const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-plus-jakarta',
  weight: ['300', '400', '500', '600', '700'],
  display: 'swap',
})

const fraunces = Fraunces({
  subsets: ['latin'],
  variable: '--font-fraunces',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

const caveat = Caveat({
  subsets: ['latin'],
  variable: '--font-caveat',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

// Design 1: Obsidian Luxe Typography
const cormorant = Cormorant_Garamond({
  subsets: ['latin'],
  variable: '--font-cormorant',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

// Design 2: Papier Typography
const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

const sourceSerif = Source_Serif_4({
  subsets: ['latin'],
  variable: '--font-source-serif',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

// Design 3: Konstrukt Typography
const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
})

// Design 5: Spielplatz Typography
const archivoBlack = Archivo_Black({
  subsets: ['latin'],
  variable: '--font-archivo-black',
  weight: ['400'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Design Showcase | Snowthere',
  description: '5 avant-garde homepage design explorations',
}

export default function DesignsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className={`
      ${plusJakarta.variable}
      ${fraunces.variable}
      ${caveat.variable}
      ${cormorant.variable}
      ${playfair.variable}
      ${sourceSerif.variable}
      ${spaceGrotesk.variable}
      ${archivoBlack.variable}
    `}>
      {children}
    </div>
  )
}
