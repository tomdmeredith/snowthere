import { revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'
import { timingSafeEqual } from 'crypto'
import { getClientIp } from '@/lib/request-ip'

/**
 * ISR Revalidation Endpoint
 *
 * Called by the agents pipeline after updating resort content.
 * Triggers Next.js to regenerate the specified page.
 *
 * Security improvements:
 * - POST only (no GET to prevent secret in logs)
 * - Rate limiting (10 requests/minute)
 * - Timing-safe secret comparison
 *
 * Usage:
 *   POST /api/revalidate
 *   Body: { "path": "/resorts/switzerland/zermatt", "secret": "your-secret" }
 */

// Simple in-memory rate limiting
// In production, use Redis or a proper rate limiting service
const rateLimitMap = new Map<string, { count: number; resetTime: number }>()
const RATE_LIMIT_WINDOW_MS = 60 * 1000 // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 10

function checkRateLimit(ip: string): { allowed: boolean; remaining: number } {
  const now = Date.now()
  const record = rateLimitMap.get(ip)

  if (!record || now > record.resetTime) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW_MS })
    return { allowed: true, remaining: RATE_LIMIT_MAX_REQUESTS - 1 }
  }

  if (record.count >= RATE_LIMIT_MAX_REQUESTS) {
    return { allowed: false, remaining: 0 }
  }

  record.count++
  return { allowed: true, remaining: RATE_LIMIT_MAX_REQUESTS - record.count }
}

/**
 * Timing-safe comparison of secrets to prevent timing attacks.
 * Uses Node.js crypto.timingSafeEqual for constant-time comparison.
 */
function secureCompare(a: string, b: string): boolean {
  if (!a || !b) return false

  const bufferA = Buffer.from(a, 'utf8')
  const bufferB = Buffer.from(b, 'utf8')

  // If lengths don't match, still do a comparison to avoid timing leaks
  if (bufferA.length !== bufferB.length) {
    // Compare with a same-length dummy to maintain constant time
    const dummy = Buffer.alloc(bufferA.length)
    timingSafeEqual(bufferA, dummy)
    return false
  }

  return timingSafeEqual(bufferA, bufferB)
}

/**
 * Validate the path parameter for security
 */
function isValidPath(path: string): boolean {
  // Must start with /
  if (!path.startsWith('/')) return false

  // Must not contain path traversal attempts
  if (path.includes('..') || path.includes('//')) return false

  // Must only contain allowed characters (alphanumeric, /, -, _)
  const validPathRegex = /^\/[a-zA-Z0-9\-_\/]*$/
  if (!validPathRegex.test(path)) return false

  // Must not be too long
  if (path.length > 200) return false

  return true
}

export async function POST(request: NextRequest) {
  try {
    // Get client IP for rate limiting
    const ip = getClientIp(request)

    // Check rate limit
    const { allowed, remaining } = checkRateLimit(ip)
    if (!allowed) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Try again later.' },
        {
          status: 429,
          headers: {
            'Retry-After': '60',
            'X-RateLimit-Remaining': '0',
          },
        }
      )
    }

    // Parse body - only accept JSON in body, not query params
    let secret: string | null = null
    let path: string | null = null

    try {
      const body = await request.json()
      secret = body.secret
      path = body.path
    } catch {
      return NextResponse.json(
        { error: 'Invalid JSON body' },
        { status: 400 }
      )
    }

    // Validate secret exists in environment
    const revalidateSecret = process.env.REVALIDATE_SECRET
    if (!revalidateSecret) {
      console.error('REVALIDATE_SECRET not configured')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    // Validate secret - use timing-safe comparison
    if (!secret || !secureCompare(secret, revalidateSecret)) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Validate path
    if (!path) {
      return NextResponse.json(
        { error: 'Missing path parameter' },
        { status: 400 }
      )
    }

    // Ensure path starts with /
    if (!path.startsWith('/')) {
      path = '/' + path
    }

    // Validate path format
    if (!isValidPath(path)) {
      return NextResponse.json(
        { error: 'Invalid path format' },
        { status: 400 }
      )
    }

    // Revalidate the path
    revalidatePath(path)

    console.log(`Revalidated: ${path}`)

    return NextResponse.json(
      {
        revalidated: true,
        path,
        timestamp: new Date().toISOString(),
      },
      {
        headers: {
          'X-RateLimit-Remaining': remaining.toString(),
        },
      }
    )
  } catch (error) {
    console.error('Revalidation error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Explicitly do not export GET to prevent secret exposure in URLs/logs
// GET requests will return 405 Method Not Allowed
