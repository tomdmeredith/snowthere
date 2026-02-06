# AGENTS.md

> Compound Beads v3.0 | Project: Snowthere (Family Ski Directory) | Initialized: 2026-02-02

## Methodology: Compound Beads

Core loop: START ROUND > WORK > COMPOUND (Arc + learnings) > CLOSE (push + update)

Files: CLAUDE.md (handoff) | .compound-beads/QUICKSTART.md (continuity) | context.md (state) | rounds.jsonl (history) | learnings.md (insights)

Round types: feature | bug_fix | triage | polish | infrastructure
Sizing: 30min-4hr. Break larger work into multiple rounds.

### Session Protocol
Start: Read QUICKSTART.md > context.md > scan recent learnings
End: git commit > session intelligence capture > update tracking files > regenerate QUICKSTART.md > git push
Rule: Work is not done until pushed AND tracking files updated.

### Auto-Triggers
| Condition | Action |
|-----------|--------|
| Session start + .compound-beads/ exists | Load QUICKSTART.md and context.md |
| Context window > 80% full | Run handoff protocol |
| Round has >5 file modifications | Update context.md |
| Round marked complete | Capture Arc + extract learnings |
| Session ending detected | Run session close protocol |
| Significant work completed | Update CLAUDE.md |
| Pattern discovered | Add to learnings.md |
| Bead open > 7 days | Prompt: close, defer, or update? |
| Completion signals ("that worked") | Capture learnings |
| 3+ decisions made | Capture rationale |
| Error or dead end | Record for future avoidance |

### Narrative Capture
Every round: We started believing > We ended believing > The transformation

## Skills
<!-- Run /compound:discover to scan available skills and add to this project -->
<!-- Format: name | description | trigger phrases | output -->
frontend-design | Spielplatz design system — playful, on-brand UI with Memphis Design influences, bold colors, Fraunces/Jakarta Sans typography | "design", "build page", "create component", "UI", "frontend" | UI components

## Tools & MCPs
<!-- Populated during skill discovery or when tools are added -->
playwright | Browser automation (Playwright MCP) | screenshots, testing, visual verification, accessibility snapshots
exa | AI-powered web search (Exa MCP) | research, current events, code context, company research
context7 | Library documentation (Context7 MCP) | framework docs, API reference, up-to-date code examples
replicate | AI model execution (Replicate MCP) | image generation (Nano Banana Pro primary)
glif | AI creative tools (Glif MCP) | image generation fallback
gh | GitHub CLI | issues, PRs, releases, actions
supabase | Database — PostgreSQL (Supabase cloud) | resort data, content, entity links, 30+ tables
vercel | Hosting & deployment (Vercel) | ISR revalidation, preview deployments, security headers

## Project Rules
<!-- Add as the project evolves -->
- **Agent-native**: Atomic primitives, composable, full parity. Agents query primitives, not receive massive lists.
- **Store atoms, compute molecules**: Deterministic formulas from data beat LLM opinion. Entity atoms in DB, links computed.
- **SEO/GEO optimized**: Schema.org (SkiResort, FAQ, BreadcrumbList, WebSite, Organization, ItemList), llms.txt, AI crawler whitelist.
- **Voice**: Instagram mom friendly — practical, encouraging, relatable, not intimidating. See voice_profiles.py.
- **Image model**: Nano Banana Pro on Replicate ($0.15/image, 4-tier fallback: Nano Banana Pro → Glif → Gemini → Flux Schnell).
- **Design system**: Spielplatz — playful, Memphis Design influenced. Never generic AI aesthetics. See .claude/skills/frontend-design/SKILL.md.
- **Entity links**: Three-tier resolution (brand registry → Google Places verified → Maps search fallback). Per-type confidence thresholds.
- **Content structure**: 10-section trip guides families can print. Quick Take BLUF at top for AI extraction.
- **Pipeline**: Fully autonomous daily cron on Railway. Direct Python + Claude API (not MCP for autonomy).
- **Two-phase validation**: Claude suggests freely, database validates after. Scales to 3000+ resorts.
