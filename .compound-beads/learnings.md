# Learnings

Knowledge extracted across all rounds with Arc narratives.

---

## Round 5.1: Agent-Native Scalability

**Arc:**
- **Started believing**: Claude can handle lists of all 3000 resorts in context
- **Ended believing**: Primitives should be atomic; agents query, not receive lists
- **Transformation**: Two-phase validation (suggest → validate) scales infinitely

**Technical:**
- `check_resort_exists()` replaces massive name lists in prompts
- 99% token reduction (22,500 → 310 tokens)
- Transliteration via `unidecode` for international names (Zürs → Zurs)
- Country name variants (Schweiz, Österreich) handled automatically
- Google Places: Place IDs cacheable indefinitely, photos are not

**Process:**
- Measure token usage before optimization attempts
- Validate against production data, not test fixtures
- Two-phase validation: Claude suggests freely, database validates after

---

## Round 4: Production Launch

**Arc:**
- **Started believing**: Launch when feature-complete
- **Ended believing**: Launch early, iterate with real traffic
- **Transformation**: Production feedback more valuable than pre-launch polish

**Technical:**
- ISR revalidation needs POST-only endpoint with rate limiting
- Railway cron schedule syntax differs from standard cron
- Vercel deployment preview URLs differ from production for ISR

**Process:**
- Deploy to production before "ready" - real traffic reveals real issues
- Configure monitoring (Search Console, Analytics) day one
- Keep deployment simple: Railway for agents, Vercel for frontend

---

## Round 3: Security Audit

**Arc:**
- **Started believing**: Security can be added incrementally
- **Ended believing**: Legal compliance must be foundational
- **Transformation**: GDPR/CCPA compliance shapes architecture decisions

**Technical:**
- DOMPurify for all `dangerouslySetInnerHTML` usages
- Security headers in `vercel.json`: CSP, HSTS, X-Frame-Options
- Cookie consent must block GA until user consents (GDPR)
- AI disclosure component required for generated content

**Process:**
- Security audit early, not as afterthought
- Legal pages (Privacy, Terms) template from attorney review
- CAN-SPAM: privacy notice mandatory on newsletter forms

---

## Round 2: Core Agents

**Arc:**
- **Started believing**: Agents need complex orchestration frameworks
- **Ended believing**: Direct Python + Claude API simpler than MCP for autonomy
- **Transformation**: Autonomous pipelines beat interactive tools for scale

**Technical:**
- 63 atomic primitives cover all agent operations
- MCP is for interactive Claude Code sessions; cron jobs don't need it
- Voice profiles define consistent tone across all content
- Three-agent approval panel (TrustGuard, FamilyValue, VoiceCoach) for quality

**Process:**
- Build primitives first, compose into agents second
- Confidence scoring: >0.8 auto-publish, <0.6 auto-reject, middle asks Claude
- Log all reasoning for observability (`log_reasoning()`)

---

## Round 1: Foundation

**Arc:**
- **Started believing**: Need custom CMS for ski content
- **Ended believing**: Supabase + Next.js sufficient for MVP
- **Transformation**: Simplicity over features for faster launch

**Technical:**
- Next.js 14 App Router with ISR for SEO
- Supabase PostgreSQL with 23 tables (normalized schema)
- "Alpine Golden Hour" design system (coral + navy)
- TypeScript types generated from Supabase schema

**Domain:**
- Core insight: International skiing often cheaper than US resorts
- Target: Parents with kids under 12
- Voice: Instagram mom friendly (practical, encouraging, relatable)
- Content: Complete trip guides families can print and use

---

## Anti-Patterns Discovered

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| All data in Claude's context | Atomic primitives agents query |
| Complex orchestration frameworks | Direct Python + Claude API |
| Security as afterthought | Legal compliance foundational |
| Launch when "ready" | Launch early, iterate |
| Formula-based confidence only | Claude for borderline decisions |
| Massive lists in prompts | Two-phase validation |

---

## Patterns That Work

| Pattern | Why It Works |
|---------|--------------|
| Atomic primitives | Composable, testable, cacheable |
| Two-phase validation | Claude suggests, DB validates |
| Three-agent approval | Diverse perspectives catch issues |
| Voice profiles | Consistent tone across content |
| Arc narratives | Capture transformation, not just tasks |
| Session close protocol | Work isn't done until pushed |
