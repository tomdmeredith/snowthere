/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.supabase.co',
      },
    ],
  },
  // Enable ISR for resort pages
  experimental: {
    // Allows revalidation via Supabase webhooks
  },
}

module.exports = nextConfig
