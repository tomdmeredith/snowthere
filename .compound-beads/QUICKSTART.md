# Snowthere Quick Start

> Compound Beads v3.0 | Last Updated: 2026-02-05

**All rounds through R16 + Linking Strategy + Pipeline Improvements complete.** No active round. Site is live, pipeline is autonomous, entity linking improved.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Intelligence Summary**:
- **Working well**: Autonomous pipeline, deterministic scoring, 4-tier image fallback, ISR revalidation, improved entity linking (HIGH confidence extraction, light refresh mode)
- **Needs attention**: 9 resorts at 0% completeness, 20 cost data outliers, migration 036 not applied
- **Watch**: Google indexing pace, affiliate program signups pending

**Recent Session (2026-02-05) — Pipeline Improvements**:
- **Entity extraction prompt**: HIGH confidence (0.8+) guidance, multi-entity example, explicit city exclusion
- **Confidence threshold**: 0.6 → 0.5 (catches more valid entities)
- **Stale detection fix**: `get_stale_resorts()` now actually filters by days_threshold (was returning N oldest regardless)
- **Light refresh mode**: New `_run_light_refresh()` function (~$0.50 vs ~$3), skips research/content, updates costs/links/images
- **CLI flag**: `--light-refresh` added to cron.py
- **JSON serialization fix**: `log_reasoning()` now handles dataclasses (KeywordResearchConfig error fixed)
- **Backfills**: Whitefish (3→12), Obergurgl (4→14), Okemo (4→14), Snowbird (10→29), Sun Peaks (9→17)

**Key Commits (2026-02-05)**:
```
1e218e2 fix: Serialize metadata in log_reasoning to handle dataclasses
82a3951 fix: Exclude major cities from entity extraction
b182e33 fix: Treat 'refreshed' status as success in exit code
98cbc6b feat: Pipeline improvements — entity extraction, stale detection fix, light refresh mode
```

**Stats**: 43+ resorts published, 10 guides published, pipeline adds ~6/day

**Pipeline**: Active on Railway (snowthere-agents)
- Resorts: ~6/day, improved entity linking (10-20 links/resort vs 3-5 before)
- Light refresh for stale resorts (~$0.50 vs ~$3)
- Guides: Mon/Thu, 3-agent expert panel
- Newsletter: Thursday 6am PT

**Infrastructure**:
- Vercel: www.snowthere.com (ISR)
- Railway: snowthere-agents (daily cron)
- Supabase: Snowthere, AWS us-east-2, 30+ tables

**Planned Rounds**:
- **R17: Agent-Native Parity** — Expose remaining primitives as MCP tools
- **R18: Pipeline Architecture** — Decompose runner monolith

**Full context**: CLAUDE.md | .compound-beads/context.md | AGENTS.md
