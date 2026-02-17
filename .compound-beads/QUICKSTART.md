# Snowthere Quick Start

> Compound Beads v3.0 | Last Updated: 2026-02-17

**Voice Evolution COMPLETE.** Section prompts rewritten personality-forward (70/30 perspective-to-info), VoiceCoach upgraded to 6-criteria evaluation, anti-hedging in style pre-pass, Layer 3 upgraded to Opus. All code on origin/main. 99 published resorts.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- MEO optimized (link-predictive titles, question headings, anti-repetition, source citations)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Stats**: 99 resorts, 15 guides (10 published), 14 countries, 6 collection pages, 151+ static pages

**Voice Evolution (Feb 15) — Personality-Forward Content**:
- Section prompts: Lead with personality, not logistics. 70/30 perspective-to-info ratio
- VoiceCoach: 6-criteria evaluation (personality density, opening variety, emotional hooks, rhythm, stance, hedging)
- Anti-hedging: deterministic stripping of "roughly"/"approximately" before numbers
- Layer 3 style: Upgraded from Sonnet to Opus 4.6 (~$0.40/section)
- Stance commitment: "Tell them which hotel you'd book, not list three neutrally"
- Price intros: 5+ varied options, anti-"Expect to pay" repetition
- Test: "Would a parent screenshot this and send it to their partner?"

**Deep Audit (Feb 13) — 6 systemic bugs fixed**:
- Calendar, coordinates, data_completeness, title dedup, pricing cache, content truncation
- Content model: Opus 4.6 | GA4: quiz_complete + affiliate_click

**Audit Remediation (Feb 17) — Critical correctness fixes**:
- Supabase migration numbering conflict resolved (`033` duplicate removed by renumbering GSC migration to `045`)
- Decision-maker budget context now uses configured `daily_budget_limit` (no hardcoded `$5.00`)
- Quiz scoring data mapping corrected (`has_ski_school` / terrain fields instead of childcare-derived proxy math)

**Expert Review Loop (Feb 17) — Strong approval gate passed**:
- Multi-expert remediation loop completed with browser UI testing (Playwright) on desktop + mobile
- Fixed `/quiz/[step]` runtime 500 caused by route validation redirect during render
- Fixed guide rendering correctness: dynamic Tailwind class no-ops replaced with static class maps
- Fixed guide resort URL fallback to valid route when country mapping missing
- Hardened API IP extraction for rate-limiting via `getClientIp()` helper (validated parsing + trusted header precedence)
- Local UI QA signal cleaned: Travelpayouts verification script now skips localhost (no CORS console error noise)
- Final UI gate: 16/16 routes passed, zero console/page errors

**Execution Rubric (Feb 17) — First principles codified**:
- Added explicit `Execution Rubric (First Principles)` to `AGENTS.md`
- Captures shared mental model: agent-native, atomic primitives, probabilistic/deterministic boundary, discovery-led delivery, and MEO-first optimization
- Written project-specifically (no external project references)

**Next Steps**:
- Re-run Bad Gastein (429 rate limit failure)
- Sign up for affiliate networks (Travelpayouts, Skiset, World Nomads)
- Homepage redesign (deferred from R14)
- Apply migration 036 to cloud Supabase (GDPR form)
- Content strategy discussion
- Regenerate resort content with new personality-forward prompts

**Pipeline**: Active on Railway (snowthere-agents)
- Resorts: ~6/day, entity linking (10-20 links/resort)
- Light refresh for stale resorts (~$0.50 vs ~$3)
- Guides: Mon/Thu, 3-agent expert panel
- Newsletter: Thursday 6am PT
- Bing: 124 URLs indexed, AI Performance tracking

**Infrastructure**:
- Vercel: www.snowthere.com (ISR, 151+ static pages)
- Railway: snowthere-agents (daily cron)
- Supabase: Snowthere, AWS us-east-2, 30+ tables
- Bing Webmaster Tools: Connected, 124 URLs indexed
- Pinterest: Tracking pixel (Tag ID 2613199211710)

**Planned Rounds**:
- **R17: Agent-Native Parity** — Expose remaining primitives as MCP tools
- **R18: Pipeline Architecture** — Decompose runner monolith

**Full context**: CLAUDE.md | .compound-beads/context.md | AGENTS.md
