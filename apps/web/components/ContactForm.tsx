'use client'

import { useState } from 'react'
import { Send, CheckCircle, AlertCircle } from 'lucide-react'

type FormStatus = 'idle' | 'submitting' | 'success' | 'error'

export function ContactForm() {
  const [status, setStatus] = useState<FormStatus>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setStatus('submitting')
    setErrorMessage('')

    const form = e.currentTarget
    const formData = new FormData(form)

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.get('name'),
          email: formData.get('email'),
          subject: formData.get('subject'),
          message: formData.get('message'),
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.error || 'Something went wrong')
      }

      setStatus('success')
      form.reset()
    } catch (error) {
      setStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Failed to send message')
    }
  }

  if (status === 'success') {
    return (
      <div className="bg-gradient-to-br from-teal-50 to-mint-50 rounded-2xl p-8 border border-teal-200 text-center">
        <CheckCircle className="w-12 h-12 text-teal-600 mx-auto mb-4" />
        <h3 className="font-display text-xl font-bold text-dark-800 mb-2">
          Message Sent!
        </h3>
        <p className="text-dark-600 mb-6">
          Thanks for reaching out. We&apos;ll get back to you as soon as we can.
        </p>
        <button
          onClick={() => setStatus('idle')}
          className="text-teal-600 hover:underline font-medium"
        >
          Send another message
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {status === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-800 font-medium">Failed to send message</p>
            <p className="text-red-600 text-sm">{errorMessage}</p>
          </div>
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-dark-700 mb-2">
          Your Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          required
          className="w-full px-4 py-3 rounded-xl border border-dark-200 focus:border-coral-500 focus:ring-2 focus:ring-coral-500/20 outline-none transition-colors"
          placeholder="Jane Smith"
        />
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-dark-700 mb-2">
          Email Address
        </label>
        <input
          type="email"
          id="email"
          name="email"
          required
          className="w-full px-4 py-3 rounded-xl border border-dark-200 focus:border-coral-500 focus:ring-2 focus:ring-coral-500/20 outline-none transition-colors"
          placeholder="jane@example.com"
        />
      </div>

      <div>
        <label htmlFor="subject" className="block text-sm font-medium text-dark-700 mb-2">
          Subject
        </label>
        <select
          id="subject"
          name="subject"
          required
          className="w-full px-4 py-3 rounded-xl border border-dark-200 focus:border-coral-500 focus:ring-2 focus:ring-coral-500/20 outline-none transition-colors bg-white"
        >
          <option value="">Select a topic...</option>
          <option value="resort-question">Question about a resort</option>
          <option value="resort-suggestion">Suggest a resort to cover</option>
          <option value="feedback">Feedback on a guide</option>
          <option value="correction">Report an error or outdated info</option>
          <option value="general">General question</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label htmlFor="message" className="block text-sm font-medium text-dark-700 mb-2">
          Message
        </label>
        <textarea
          id="message"
          name="message"
          required
          rows={5}
          className="w-full px-4 py-3 rounded-xl border border-dark-200 focus:border-coral-500 focus:ring-2 focus:ring-coral-500/20 outline-none transition-colors resize-none"
          placeholder="Tell us what's on your mind..."
        />
      </div>

      <button
        type="submit"
        disabled={status === 'submitting'}
        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-coral-500 text-white font-semibold rounded-xl hover:bg-coral-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {status === 'submitting' ? (
          <>
            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Sending...
          </>
        ) : (
          <>
            <Send className="w-5 h-5" />
            Send Message
          </>
        )}
      </button>

      <p className="text-dark-500 text-xs text-center">
        By submitting this form, you agree to our{' '}
        <a href="/privacy" className="text-teal-600 hover:underline">Privacy Policy</a>.
      </p>
    </form>
  )
}
