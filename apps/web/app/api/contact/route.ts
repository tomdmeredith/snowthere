import { NextRequest, NextResponse } from 'next/server'
import { createClient, SupabaseClient } from '@supabase/supabase-js'

// Lazy initialization to avoid build-time errors
let _supabaseAdmin: SupabaseClient | null = null

function getSupabaseAdmin(): SupabaseClient {
  if (!_supabaseAdmin) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY

    if (!url || !key) {
      throw new Error('Missing Supabase configuration')
    }

    _supabaseAdmin = createClient(url, key)
  }
  return _supabaseAdmin
}

interface ContactRequest {
  name: string
  email: string
  subject: string
  message: string
}

// Rate limiting: simple in-memory store (resets on deploy)
const rateLimitStore = new Map<string, { count: number; resetAt: number }>()
const RATE_LIMIT_WINDOW_MS = 60 * 1000 // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 3 // Stricter for contact form

function isRateLimited(ip: string): boolean {
  const now = Date.now()
  const record = rateLimitStore.get(ip)

  if (!record || now > record.resetAt) {
    rateLimitStore.set(ip, { count: 1, resetAt: now + RATE_LIMIT_WINDOW_MS })
    return false
  }

  if (record.count >= RATE_LIMIT_MAX_REQUESTS) {
    return true
  }

  record.count++
  return false
}

// Basic input sanitization
function sanitizeInput(input: string): string {
  return input
    .trim()
    .slice(0, 5000) // Max length
    .replace(/<[^>]*>/g, '') // Strip HTML tags
}

export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0] || 'unknown'
    if (isRateLimited(ip)) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.' },
        { status: 429 }
      )
    }

    // Parse request body
    const body: ContactRequest = await request.json()
    const { name, email, subject, message } = body

    // Validate required fields
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
      return NextResponse.json(
        { error: 'Name is required' },
        { status: 400 }
      )
    }

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      )
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      )
    }

    if (!subject || typeof subject !== 'string' || subject.trim().length === 0) {
      return NextResponse.json(
        { error: 'Subject is required' },
        { status: 400 }
      )
    }

    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    // Check for minimum message length
    if (message.trim().length < 10) {
      return NextResponse.json(
        { error: 'Message must be at least 10 characters' },
        { status: 400 }
      )
    }

    const supabase = getSupabaseAdmin()

    // Insert contact submission
    const { data, error: insertError } = await supabase
      .from('contact_submissions')
      .insert({
        name: sanitizeInput(name),
        email: email.toLowerCase().trim(),
        subject: sanitizeInput(subject),
        message: sanitizeInput(message),
        ip_address: ip,
        user_agent: request.headers.get('user-agent')?.slice(0, 500),
        referrer: request.headers.get('referer')?.slice(0, 500),
        status: 'new',
      })
      .select('id')
      .single()

    if (insertError) {
      console.error('Contact submission error:', insertError)
      return NextResponse.json(
        { error: 'Failed to submit message. Please try again.' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message: 'Message received! We\'ll get back to you soon.',
      submission_id: data.id,
    })
  } catch (error) {
    console.error('Contact error:', error)
    return NextResponse.json(
      { error: 'An unexpected error occurred' },
      { status: 500 }
    )
  }
}

// Health check / preflight
export async function GET() {
  return NextResponse.json({ status: 'ok', endpoint: 'contact' })
}
