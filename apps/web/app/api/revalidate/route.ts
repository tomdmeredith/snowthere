import { revalidatePath } from 'next/cache'
import { NextRequest, NextResponse } from 'next/server'

/**
 * ISR Revalidation Endpoint
 *
 * Called by the agents pipeline after updating resort content.
 * Triggers Next.js to regenerate the specified page.
 *
 * Usage:
 *   POST /api/revalidate
 *   Body: { "path": "/resorts/switzerland/zermatt", "secret": "your-secret" }
 *
 * Or with query params:
 *   POST /api/revalidate?path=/resorts/switzerland/zermatt&secret=your-secret
 */
export async function POST(request: NextRequest) {
  try {
    // Get secret and path from body or query params
    let secret: string | null = null
    let path: string | null = null

    const { searchParams } = new URL(request.url)

    // Try query params first
    secret = searchParams.get('secret')
    path = searchParams.get('path')

    // Try body if not in query params
    if (!secret || !path) {
      try {
        const body = await request.json()
        secret = secret || body.secret
        path = path || body.path
      } catch {
        // Body might be empty
      }
    }

    // Validate secret
    const revalidateSecret = process.env.REVALIDATE_SECRET
    if (!revalidateSecret) {
      console.error('REVALIDATE_SECRET not configured')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    if (secret !== revalidateSecret) {
      return NextResponse.json(
        { error: 'Invalid secret' },
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

    // Revalidate the path
    revalidatePath(path)

    console.log(`Revalidated: ${path}`)

    return NextResponse.json({
      revalidated: true,
      path,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Revalidation error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

// Also support GET for simple testing
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const secret = searchParams.get('secret')
  const path = searchParams.get('path')

  if (!secret || !path) {
    return NextResponse.json({
      error: 'Usage: GET /api/revalidate?secret=YOUR_SECRET&path=/your/page',
      example: '/api/revalidate?secret=abc123&path=/resorts/switzerland/zermatt',
    }, { status: 400 })
  }

  // Forward to POST handler
  return POST(request)
}
