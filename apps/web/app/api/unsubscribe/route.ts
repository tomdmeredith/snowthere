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

/**
 * POST /api/unsubscribe
 *
 * Unsubscribes an email address from all marketing communications.
 * CAN-SPAM requires this to work within 10 business days.
 * We process immediately.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { email } = body

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      )
    }

    const supabase = getSupabaseAdmin()
    const emailNormalized = email.toLowerCase().trim()

    // Find subscriber
    const { data: subscriber, error: findError } = await supabase
      .from('subscribers')
      .select('id, status')
      .eq('email', emailNormalized)
      .single()

    if (findError || !subscriber) {
      // Don't reveal if email exists - just say success
      // This prevents email enumeration attacks
      return NextResponse.json({
        success: true,
        message: 'If that email was subscribed, it has been unsubscribed.',
      })
    }

    if (subscriber.status === 'unsubscribed') {
      return NextResponse.json({
        success: true,
        message: 'You were already unsubscribed.',
      })
    }

    // Unsubscribe
    const { error: updateError } = await supabase
      .from('subscribers')
      .update({
        status: 'unsubscribed',
        unsubscribed_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })
      .eq('id', subscriber.id)

    if (updateError) {
      console.error('Unsubscribe error:', updateError)
      return NextResponse.json(
        { error: 'Failed to unsubscribe. Please try again.' },
        { status: 500 }
      )
    }

    // Cancel any active sequences
    await supabase
      .from('subscriber_sequence_progress')
      .update({
        status: 'cancelled',
        updated_at: new Date().toISOString(),
      })
      .eq('subscriber_id', subscriber.id)
      .eq('status', 'active')

    return NextResponse.json({
      success: true,
      message: 'You have been unsubscribed from all Snowthere emails.',
    })
  } catch (error) {
    console.error('Unsubscribe error:', error)
    return NextResponse.json(
      { error: 'An unexpected error occurred' },
      { status: 500 }
    )
  }
}

/**
 * GET /api/unsubscribe?email=xxx
 *
 * Also supports GET for one-click unsubscribe (RFC 8058).
 * Some email clients use GET for List-Unsubscribe-Post fallback.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const email = searchParams.get('email')

  if (!email) {
    return NextResponse.json(
      { error: 'Email parameter is required' },
      { status: 400 }
    )
  }

  // Redirect to the unsubscribe page for user confirmation
  // The page will handle the actual unsubscribe via POST
  const unsubscribeUrl = new URL('/unsubscribe', request.url)
  unsubscribeUrl.searchParams.set('email', email)

  return NextResponse.redirect(unsubscribeUrl)
}
