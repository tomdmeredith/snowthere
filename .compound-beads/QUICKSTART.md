# Snowthere Quick Start

> Compound Beads v3.0 | Last Updated: 2026-02-07

**Round 20 COMPLETE + Pipeline Bug Fix deployed.** All code on origin/main. Migrations 042+043 applied. Backfills done. Pipeline fix (f3e892c) deployed to Railway — next cron run will auto-retry 5 failed resorts.

**North Star**: "Snowthere is THE go-to source for high value, trusted information for family ski trips anywhere in the world"

**Guiding Principles**:
- Agent-native (atomic primitives, composable, full parity)
- Store atoms, compute molecules (deterministic formulas from data)
- SEO/GEO optimized (Schema.org, llms.txt, AI crawler whitelist)
- Autonomous operation (daily cron: resorts + guides + newsletter)

**Stats**: ~75 resorts, 10 guides, 14 countries, 6 collection pages, 96 static pages

**Pipeline Bug Fix (f3e892c, Feb 7)**:
- `runner.py`: Local `from datetime import datetime, timezone` shadowed module-level → moved `timezone` to module-level
- `discovery_agent.py` + `quality_agent.py`: `check_budget()` called with no args → replaced with `settings.daily_budget_limit - get_daily_spend()`
- 5 failed resorts (Snowbasin, Stratton, Taos, Big White, Las Leñas) will auto-retry next cron

**Next Steps**:
- Sign up for affiliate networks (Travelpayouts, Skiset, World Nomads)
- Apply migration 036 to cloud Supabase (GDPR data_requests table)
- Re-run quick takes backfill for 31 resorts that exceeded 65-word limit
- Homepage redesign (deferred from R14)

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
