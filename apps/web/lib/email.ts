/**
 * Email utilities for Snowthere
 * Uses Resend API for sending transactional emails
 */

import { Resend } from 'resend'

// Initialize Resend (lazy - only when needed)
let _resend: Resend | null = null

function getResend(): Resend | null {
  if (!_resend) {
    const apiKey = process.env.RESEND_API_KEY
    if (!apiKey) {
      console.warn('RESEND_API_KEY not configured - emails will not be sent')
      return null
    }
    _resend = new Resend(apiKey)
  }
  return _resend
}

// Sender configuration
const FROM_EMAIL = 'Snowthere <hello@snowthere.com>'
const REPLY_TO = 'hello@snowthere.com'

interface SendEmailOptions {
  to: string
  subject: string
  html: string
  text?: string
}

interface SendEmailResult {
  success: boolean
  messageId?: string
  error?: string
}

/**
 * Send an email via Resend
 */
export async function sendEmail(options: SendEmailOptions): Promise<SendEmailResult> {
  const resend = getResend()

  if (!resend) {
    return {
      success: false,
      error: 'Email service not configured',
    }
  }

  try {
    const { data, error } = await resend.emails.send({
      from: FROM_EMAIL,
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
      replyTo: REPLY_TO,
    })

    if (error) {
      console.error('Resend error:', error)
      return {
        success: false,
        error: error.message,
      }
    }

    return {
      success: true,
      messageId: data?.id,
    }
  } catch (err) {
    console.error('Email send error:', err)
    return {
      success: false,
      error: err instanceof Error ? err.message : 'Unknown error',
    }
  }
}

/**
 * Send the welcome confirmation email immediately on signup
 */
export async function sendWelcomeEmail(
  email: string,
  name?: string | null
): Promise<SendEmailResult> {
  const displayName = name || 'there'

  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to Snowthere!</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
    <tr>
      <td align="center" style="padding: 40px 20px;">
        <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px;">

          <!-- Header -->
          <tr>
            <td style="text-align: center; padding-bottom: 30px;">
              <h1 style="margin: 0; color: #1a2f4f; font-size: 28px; font-weight: 700;">
                ⛷️ Snowthere
              </h1>
              <p style="margin: 5px 0 0 0; color: #64748b; font-size: 14px;">
                Family Ski Trip Guides
              </p>
            </td>
          </tr>

          <!-- Main Content -->
          <tr>
            <td style="background: white; border-radius: 16px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">

              <h2 style="margin: 0 0 20px 0; color: #1a2f4f; font-size: 24px;">
                Hey ${displayName}! 👋
              </h2>

              <p style="margin: 0 0 20px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                Welcome to Snowthere! You're now part of a community of parents planning unforgettable family ski trips.
              </p>

              <p style="margin: 0 0 20px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                Here's what you can expect from us:
              </p>

              <ul style="margin: 0 0 25px 0; padding-left: 20px; color: #475569; font-size: 16px; line-height: 1.8;">
                <li><strong>Resort guides</strong> written specifically for families with kids</li>
                <li><strong>Real costs</strong> – no hiding the numbers</li>
                <li><strong>Age-specific tips</strong> – because a 3-year-old and a 10-year-old need different things</li>
                <li><strong>Weekly deals</strong> on lift tickets, lodging, and gear</li>
              </ul>

              <p style="margin: 0 0 25px 0; color: #475569; font-size: 16px; line-height: 1.6;">
                <strong>Pro tip:</strong> Did you know it can be <em>cheaper</em> to fly to Austria than ski in Colorado? We'll show you how in our next email.
              </p>

              <!-- CTA Button -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="center" style="padding: 10px 0 25px 0;">
                    <a href="https://snowthere.com/resorts"
                       style="display: inline-block; background: linear-gradient(135deg, #ff6f61 0%, #ff8a7a 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">
                      Browse Family-Friendly Resorts →
                    </a>
                  </td>
                </tr>
              </table>

              <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;">

              <p style="margin: 0; color: #64748b; font-size: 14px; line-height: 1.6;">
                Questions? Just reply to this email – I read every one.
              </p>

              <p style="margin: 15px 0 0 0; color: #1a2f4f; font-size: 16px;">
                Happy planning!<br>
                <strong>The Snowthere Team</strong>
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding-top: 30px; text-align: center;">
              <p style="margin: 0 0 10px 0; color: #94a3b8; font-size: 12px;">
                Snowthere · Family Ski Trip Guides
              </p>
              <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                <a href="https://snowthere.com/unsubscribe?email=${encodeURIComponent(email)}" style="color: #94a3b8;">Unsubscribe</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
`

  const text = `
Hey ${displayName}!

Welcome to Snowthere! You're now part of a community of parents planning unforgettable family ski trips.

Here's what you can expect from us:
- Resort guides written specifically for families with kids
- Real costs – no hiding the numbers
- Age-specific tips – because a 3-year-old and a 10-year-old need different things
- Weekly deals on lift tickets, lodging, and gear

Pro tip: Did you know it can be CHEAPER to fly to Austria than ski in Colorado? We'll show you how in our next email.

Browse Family-Friendly Resorts: https://snowthere.com/resorts

Questions? Just reply to this email – I read every one.

Happy planning!
The Snowthere Team

---
Snowthere · Family Ski Trip Guides
Unsubscribe: https://snowthere.com/unsubscribe?email=${encodeURIComponent(email)}
`

  return sendEmail({
    to: email,
    subject: '🎿 Welcome to Snowthere!',
    html,
    text,
  })
}
