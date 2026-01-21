export async function GET() {
  const robotsTxt = `User-agent: *
Allow: /
Sitemap: https://snowthere.com/sitemap.xml

User-agent: GPTBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /
`
  return new Response(robotsTxt, {
    headers: { 'Content-Type': 'text/plain' },
  })
}
