# Snowthere Quick Start

**Round 5.9.5**: Pipeline Confidence Fix (completed 2026-01-24)
**Type**: bug fix
**Status**: Complete, needs commit + deploy

**Recent**:
- R5.9.5: Fixed stale confidence score - now recalculates after cost acquisition
- R5.9.4: Hidden FamilyMetricsTable, fixed sticky sidebar, fixed anchor scrolling
- R5.9.3: Homepage/resorts ordering by score, duplicate Kitzbuhel removed, CostTable hidden
- R5.9: Country landing pages + hero images + cost/metrics data fixes
- R5.8: Comprehensive resort page audit (Zermatt gold standard)

**Bug Fixed (R5.9.5)**:
- Confidence was calculated BEFORE cost acquisition (line 274 of runner.py)
- Price data = 40% of confidence score, but was 0 at calculation time
- Result: "88% quality but 0.16 confidence" in logs
- Fix: Recalculate confidence after cost acquisition succeeds (lines 417-424)

**Pending**:
- Commit and push for Railway deploy
- Round 5 remaining: cron alerts, accessibility, trademark notices, Core Web Vitals
- Round 6: Homepage redesign

**Full context**: CLAUDE.md | .compound-beads/context.md
