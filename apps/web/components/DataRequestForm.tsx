'use client'

import { useState } from 'react'
import { Trash2, FileText, Loader2, CheckCircle2 } from 'lucide-react'

export function DataRequestForm() {
  const [email, setEmail] = useState('')
  const [requestType, setRequestType] = useState<'deletion' | 'access'>('deletion')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')

    try {
      const res = await fetch('/api/data-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, request_type: requestType }),
      })

      const data = await res.json()

      if (res.ok && data.success) {
        setStatus('success')
        setMessage(data.message)
        setEmail('')
      } else {
        setStatus('error')
        setMessage(data.error || 'Something went wrong. Please try again.')
      }
    } catch {
      setStatus('error')
      setMessage('Network error. Please try again.')
    }
  }

  if (status === 'success') {
    return (
      <div className="bg-teal-50 border border-teal-200 rounded-2xl p-6 flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-teal-600 mt-0.5 shrink-0" />
        <p className="text-teal-800">{message}</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="data-email" className="block text-sm font-medium text-dark-700 mb-1">
          Your email address
        </label>
        <input
          id="data-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full px-4 py-3 rounded-xl border border-dark-200 text-dark-800 placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-transparent"
        />
      </div>

      <div>
        <span className="block text-sm font-medium text-dark-700 mb-2">Request type</span>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setRequestType('deletion')}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              requestType === 'deletion'
                ? 'bg-coral-100 text-coral-700'
                : 'bg-dark-100 text-dark-600 hover:bg-dark-200'
            }`}
          >
            <Trash2 className="w-4 h-4" />
            Delete my data
          </button>
          <button
            type="button"
            onClick={() => setRequestType('access')}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              requestType === 'access'
                ? 'bg-teal-100 text-teal-700'
                : 'bg-dark-100 text-dark-600 hover:bg-dark-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            Access my data
          </button>
        </div>
      </div>

      {status === 'error' && (
        <p className="text-sm text-coral-600">{message}</p>
      )}

      <button
        type="submit"
        disabled={status === 'loading' || !email}
        className="inline-flex items-center gap-2 px-6 py-3 bg-dark-800 text-white rounded-full font-semibold hover:bg-dark-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {status === 'loading' ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Submitting...
          </>
        ) : (
          'Submit request'
        )}
      </button>

      <p className="text-xs text-dark-400">
        We will process your request within 30 days as required by GDPR/CCPA.
      </p>
    </form>
  )
}
