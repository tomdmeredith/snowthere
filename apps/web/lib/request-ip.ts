import { isIP } from 'node:net'
import { NextRequest } from 'next/server'

const IP_HEADERS = [
  'x-vercel-forwarded-for',
  'x-real-ip',
  'cf-connecting-ip',
  'x-forwarded-for',
]

function normalizeIpCandidate(raw: string): string | null {
  const first = raw.split(',')[0]?.trim()
  if (!first) return null

  // Strip Forwarded header wrapping and quotes, e.g. for="1.2.3.4:1234"
  const cleaned = first
    .replace(/^for=/i, '')
    .replace(/^"+|"+$/g, '')
    .replace(/^\[|\]$/g, '')

  // Strip port for IPv4 values like 1.2.3.4:1234
  const ipv4WithPort = cleaned.match(/^(\d{1,3}(?:\.\d{1,3}){3}):\d+$/)
  const candidate = ipv4WithPort ? ipv4WithPort[1] : cleaned

  return isIP(candidate) ? candidate : null
}

export function getClientIp(request: NextRequest): string {
  for (const header of IP_HEADERS) {
    const value = request.headers.get(header)
    if (!value) continue
    const parsed = normalizeIpCandidate(value)
    if (parsed) return parsed
  }

  const forwarded = request.headers.get('forwarded')
  if (forwarded) {
    for (const part of forwarded.split(';')) {
      const parsed = normalizeIpCandidate(part.trim())
      if (parsed) return parsed
    }
  }

  return 'unknown'
}
