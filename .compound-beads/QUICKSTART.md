# Snowthere Quick Start

> Compound Beads v3.0 | Last Updated: 2026-02-10

**Round 22 COMPLETE (ad373c6 + a7edaaa).** MEO + voice de-mandating deployed + Vercel build fix. All code on origin/main. 7 expert reviewers ALL APPROVE/PASS. Build passes, 151 static pages on Vercel.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- MEO optimized (link-predictive titles, question headings, anti-repetition, source citations)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Stats**: ~90 resorts, 15 guides (10 published), 14 countries, 6 collection pages, 151 static pages

**Round 22 — MEO + Voice De-Mandating (ad373c6)**:
- content.py: Probabilistic voice guidance replaces prescriptive rules (no more 80/20 ratio, mandatory patterns)
- page.tsx: Link-predictive titles ("Family Ski Guide: {Name} with Kids"), 6 question-based headings
- Anti-repetition block + "content that gets cited" MEO framing + source citation guidance
- Date displays now include day for content freshness signal
- Based on Princeton GEO study + Exa link prediction model research
- Vercel build fix (a7edaaa): Array.isArray() guards for JSONB data — Garmisch-Partenkirchen had non-array value crashing `.map()`

**Round 21 — Voice Rebalancing (7b7dbd9)**:
- Voice shifted from "Instagram mom" to "Morning Brew for family ski trips" (smart, witty, efficient)
- Future-casting, self-contained paragraphs, honest tension, rhythmic variety
- Multilingual research queries, thin content gate, child price floor

**Next Steps**:
- Sign up for affiliate networks (Travelpayouts, Skiset, World Nomads)
- Homepage redesign (deferred from R14)

**Pipeline**: Active on Railway (snowthere-agents)
- Resorts: ~6/day, entity linking (10-20 links/resort)
- Light refresh for stale resorts (~$0.50 vs ~$3)
- Guides: Mon/Thu, 3-agent expert panel
- Newsletter: Thursday 6am PT
- Bing: 124 URLs indexed, AI Performance tracking

**Infrastructure**:
- Vercel: www.snowthere.com (ISR, 96+ static pages)
- Railway: snowthere-agents (daily cron)
- Supabase: Snowthere, AWS us-east-2, 30+ tables
- Bing Webmaster Tools: Connected, 124 URLs indexed

**Planned Rounds**:
- **R17: Agent-Native Parity** — Expose remaining primitives as MCP tools
- **R18: Pipeline Architecture** — Decompose runner monolith

**Full context**: CLAUDE.md | .compound-beads/context.md | AGENTS.md
