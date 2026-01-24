# Snowthere Quick Start

**Round 5.9.5**: Pipeline Bug Fixes (completed 2026-01-24)
**Type**: bug fix
**Status**: Complete, needs commit + deploy

**Recent**:
- R5.9.5: Fixed confidence score + duplicate resort bugs
- R5.9.4: Hidden FamilyMetricsTable, fixed sticky sidebar, fixed anchor scrolling
- R5.9.3: Homepage/resorts ordering by score, duplicate Kitzbuhel removed, CostTable hidden

**Bugs Fixed (R5.9.5)**:
1. **Stale confidence**: Recalculate after cost acquisition (was 0.16 with 88% quality)
2. **Duplicate resorts**: Added `unidecode` to slugify (Kitzbühel → kitzbuhel not kitzbühel)

**Note**: "Only 2 resorts ran" is expected - quality queue has 45-day cooling off period.

**Pending**:
- Commit and push for Railway deploy
- Round 5 remaining: cron alerts, accessibility, trademark notices, Core Web Vitals
- Round 6: Homepage redesign

**Full context**: CLAUDE.md | .compound-beads/context.md
