# Snowthere Quick Start

> Compound Beads v3.0 | Last Updated: 2026-02-19

**Round QA: COMPLETE.** Fixed 8 resort issues + 3 guide issues (11 fixes total). Published 7 stuck draft guides.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Stats**: 99 resorts, 17 guides (all published), 14 countries, 6 collection pages, 151+ static pages

**QA Fixes Implemented (Feb 19):**
1. resort-linker.ts: 5-char minimum + common word exclusion for hyphenated names
2. Content truncation: max_tokens 1500→2500 + auto-retry at 4000 + quality gate
3. Non-place entities: product/event type detection → skip Maps resolution
4. Calendar: retry with backoff + stderr logging + traceback on exception
5. Lodging discovery: dedicated Exa + Haiku pass, integrated into acquire_resort_costs()
6. Internal cross-links: published resort check before external entity resolution
7. FAQ style: list-of-dicts handling via extracted _apply_text_fixes() + anti-hedging prompt
8. Expert panel: SkepticExpert advisory_only, low-confidence publish tier, rejection logging
9. Draft guides: all 7 published (9.8k-12.6k chars, images, 8 sections each)
10. Guide resort links: render-time via resort-linker.ts, removed generation-time injection

**Pipeline**: Active on Railway (snowthere-agents)
- Resorts: ~6/day, entity linking with internal cross-link priority
- Guides: Mon/Thu, 4-voting + 1-advisory expert panel (was 5-voting)
- Newsletter: DISABLED (handed off to GTM team)
- Welcome sequence: Still runs daily via Railway cron

**Next Steps:**
- Re-run Bad Gastein (429 rate limit)
- Runner.py decomposition (R18 — 2,105 line monolith)
- Homepage redesign (deferred from R14)
- Regenerate resort content with personality-forward prompts

**Full context**: CLAUDE.md | .compound-beads/context.md | AGENTS.md
