import { NextRequest, NextResponse } from 'next/server'
import { createClient, SupabaseClient } from '@supabase/supabase-js'
import { getClientIp } from '@/lib/request-ip'

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

// Rate limiting: 1 request per IP per minute
const rateLimitStore = new Map<string, { count: number; resetAt: number }>()

function isRateLimited(ip: string): boolean {
  const now = Date.now()
  const record = rateLimitStore.get(ip)

  if (!record || now > record.resetAt) {
    rateLimitStore.set(ip, { count: 1, resetAt: now + 60_000 })
    return false
  }

  if (record.count >= 2) return true
  record.count++
  return false
}

export async function POST(request: NextRequest) {
  try {
    const ip = getClientIp(request)
    if (isRateLimited(ip)) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.' },
        { status: 429 }
      )
    }

    const body = await request.json()
    const { email, request_type } = body

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      )
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      )
    }

    if (!request_type || !['deletion', 'access'].includes(request_type)) {
      return NextResponse.json(
        { error: 'Invalid request type. Must be "deletion" or "access".' },
        { status: 400 }
      )
    }

    const supabase = getSupabaseAdmin()

    const { error: insertError } = await supabase
      .from('data_requests')
      .insert({
        email: email.toLowerCase().trim(),
        request_type,
      })

    if (insertError) {
      // Unique constraint violation = duplicate request same day
      if (insertError.code === '23505') {
        return NextResponse.json({
          success: true,
          message:
            'We already received your request today. We will process it within 30 days.',
        })
      }
      console.error('Data request error:', insertError)
      return NextResponse.json(
        { error: 'Failed to submit request. Please try again.' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message:
        'Your request has been received. We will process it within 30 days as required by GDPR/CCPA.',
    })
  } catch (error) {
    console.error('Data request error:', error)
    return NextResponse.json(
      { error: 'An unexpected error occurred' },
      { status: 500 }
    )
  }
}
