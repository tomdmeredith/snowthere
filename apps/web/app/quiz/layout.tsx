import { Metadata } from 'next'
import { SITE_URL } from '@/lib/constants'
import { Footer } from '@/components/home/Footer'

export const metadata: Metadata = {
  title: 'Snow Match Quiz',
  description:
    "Find your family's perfect ski resort match in under 2 minutes. Answer 7 quick questions and discover your snow personality.",
  alternates: {
    canonical: `${SITE_URL}/quiz`,
  },
  openGraph: {
    url: `${SITE_URL}/quiz`,
    title: 'Snow Match Quiz | Snowthere',
    description:
      "Find your family's perfect ski resort match in under 2 minutes.",
  },
}

export default function QuizLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      {children}
      <Footer />
    </>
  )
}
