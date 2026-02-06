# Snowthere Quick Start

> Compound Beads v3.0 | Last Updated: 2026-02-06

**Round 20 COMMITTED + EXPERT REVIEWED.** All code committed (b5c3e8f content, 0c7121b type safety + security). All 7 expert reviewers STRONG APPROVE / APPROVE. Migrations 042+043 applied. Backfills not yet run (~$9.29).

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Stats**: ~75 resorts, 10 guides, 14 countries, 6 collection pages, 96 static pages

**Round 20 Changes (committed b5c3e8f)**:
- Strong-tag-first entity extraction (eliminates ~$0.03/resort Claude calls)
- Airport links → Skyscanner flight search URLs via IATA code extraction
- Quick Takes: 40-65 word single paragraph (was 80-120 word 4-part)
- Taglines: fact-based calibration + forbidden pattern regex blocklist
- Three-layer hybrid scoring: structural 30% + content LLM 50% + review 20%
- Dollar sign always shown on resort cards (fallback $$ when NULL)
- Internal resort links injected into guide prose
- 3 new backfill scripts: costs, quick_takes, hybrid_scores

**Type Safety + Security (committed 0c7121b)**:
- Zero `as any` casts (was ~15) — proper types for Supabase joins
- `sanitizeHTML()` on all `dangerouslySetInnerHTML` paths
- `sanitizeJSON()` on all JSON-LD `<script>` blocks (7 pages)
- 8 missing fields added to `database.types.ts` (migrations 042+043)

**Next Steps**:
- Run backfills: costs → links --clear-cache → quick_takes → taglines → hybrid_scores (~$9.29)
- Sign up for affiliate networks (Travelpayouts, Skiset, World Nomads)

**Pipeline**: Active on Railway (snowthere-agents)
- Resorts: ~6/day, entity linking (10-20 links/resort)
- Light refresh for stale resorts (~$0.50 vs ~$3)
- Guides: Mon/Thu, 3-agent expert panel
- Newsletter: Thursday 6am PT

**Infrastructure**:
- Vercel: www.snowthere.com (ISR, 96 static pages)
- Railway: snowthere-agents (daily cron)
- Supabase: Snowthere, AWS us-east-2, 30+ tables

**Planned Rounds**:
- **R17: Agent-Native Parity** — Expose remaining primitives as MCP tools
- **R18: Pipeline Architecture** — Decompose runner monolith

**Full context**: CLAUDE.md | .compound-beads/context.md | AGENTS.md
