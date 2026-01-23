# Snowthere Context

> Last synced: 2026-01-23
> Agent: compound-beads v2.0

## Current Round

**Round 6: Homepage Redesign** (pending)
- Type: feature
- Status: Not started
- Goal: Implement chosen homepage design from concepts

## Round 5.1: Agent-Native Scalability (Completed)

**Goal**: Scale duplicate detection to 3000+ resorts

**Accomplishments**:
- New primitives: `check_resort_exists()`, `find_similar_resorts()`, `count_resorts()`
- Two-phase validation: Claude suggests → DB validates
- 99% token reduction (22,500 → 310 tokens)
- Transliteration via unidecode for international names

**Key Insight**: Primitives should be atomic; agents query, not receive massive lists.

## Round 5: Compliance & Polish (In Progress)

**Goal**: Monitoring, accessibility, final polish

**Remaining tasks**:
- [ ] Cron failure alerts
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Trademark notices for ski pass logos
- [ ] Performance optimization (Core Web Vitals)

## Round 4: Production Launch (Completed)

**Goal**: Deploy to production, configure monitoring

**Key outcomes**:
- www.snowthere.com live on Vercel
- Railway cron (creative-spontaneity) running daily
- Google Search Console + Analytics configured
- Supabase production with 23 tables

## Active Tasks

From Round 5 (Compliance & Polish):
1. Cron failure alerts
2. Accessibility audit (WCAG 2.1 AA)
3. Trademark notices for ski pass logos
4. Performance optimization (Core Web Vitals)

From Round 4 (Production Launch):
1. Newsletter signup API integration
2. Run first automated batch (10-20 resorts)
3. Monitor and iterate

## Key Files

| Category | Files |
|----------|-------|
| **Pipeline** | `agents/pipeline/runner.py`, `orchestrator.py`, `decision_maker.py` |
| **Primitives** | `agents/shared/primitives/` (63 atomic operations) |
| **Frontend** | `apps/web/app/resorts/[country]/[slug]/page.tsx` |
| **Config** | `agents/shared/config.py`, `CLAUDE.md` |

## Infrastructure

| Service | Status |
|---------|--------|
| Vercel | www.snowthere.com (live) |
| Railway | creative-spontaneity (daily cron) |
| Supabase | Snowthere (23 tables, AWS us-east-2) |

## Recent Commits

- `6b9804c` feat: Add extraction layer and voice pattern post-processing
- `0cfa695` fix: P0 critical bugs - ghost resorts, low confidence publishing
- `17966de` fix: Handle dict context in generate_tagline
