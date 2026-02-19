# Snowthere Context

> Last synced: 2026-02-19 (Round QA — COMPLETE)
> Agent: compound-beads v3.0
> Session ID: QA-2
> Sessions This Round: 2

## Current State

**Round QA complete.** Fixed 8 resort issues + 3 guide issues (11 fixes total). Published 7 stuck draft guides. All 17 guides now published. Frontend build passes.

- **Resorts:** 99 published with entity links, pipeline adds ~6/day
- **Guides:** 15 total (10 published, 5 drafts), autonomous generation Mon/Thu
- **Countries:** 14 with country pages + intro content
- **Collections:** 6 programmatic SEO pages (best-for-beginners, best-for-toddlers, etc.)
- **Static Pages:** 151+ on Vercel (build passes, zero TypeScript errors)
- **Voice:** Snowthere Guide — personality-forward (70/30 perspective-to-info), 6-criteria VoiceCoach, anti-hedging
- **MEO:** Link-predictive titles, question-based headings (2/6 with entity names), anti-repetition, source citations
- **Entity Links:** Strong-tag-first extraction, Skyscanner flight URLs, context-aware destinations, structural guardrails
- **Scoring:** Three-layer hybrid: structural 30% + content LLM 50% + review 20%
- **Quick Takes:** 50-90 word single paragraph format (fact-based, validation accepts up to 95)
- **Type Safety:** Zero `as any` casts, 8 migration fields in database.types.ts
- **Security:** `sanitizeHTML()` on all dangerouslySetInnerHTML, `sanitizeJSON()` on all JSON-LD
- **Newsletter:** DISABLED in cron.py (welcome sequence still runs via Railway cron)
- **SEO:** HeroSpielplatz server component, country pages have generateStaticParams, ISR 6h
- **Bing Webmaster Tools:** Connected, 124 URLs indexed, 0 errors, AI Performance baseline 0 citations
- **Content Freshness:** Date display includes day (e.g., "Feb 7, 2026") for freshness signal
- **Google Places:** Both APIs enabled, correct API key deployed to Railway
- **Content Model:** Claude Opus 4.6 (upgraded from 4.5 on Feb 13)
- **Style Primitive:** 3-layer editing — deterministic pre-pass + Haiku + Opus (upgraded from Sonnet)
- **Pricing:** Exa discovery + Claude Haiku interpretation + country-specific validation
- **Calendar:** All 99 resorts have ski quality calendar (495 entries via generate_ski_calendar())
- **GA4 Events:** quiz_complete + affiliate_click deployed (0a53767)
- **Pinterest:** Tracking pixel active (Tag ID 2613199211710)
- **Migrations:** 042 + 043 + 044 applied to cloud Supabase
- **Audit Remediation (Feb 17):** Fixed duplicate migration versioning, decision-maker budget hardcode, and quiz scoring data mapping
- **Expert Review Loop (Feb 17):** Multi-expert strong-approval gate passed with browser QA (16/16 routes, desktop+mobile, zero console/page errors)
- **First-Principles Rubric (Feb 17):** `AGENTS.md` now includes explicit execution rubric for agent-native, atomic, discovery-led, probabilistic/deterministic, and MEO-first delivery

---

## Round QA: Resort & Guide Quality Audit Remediation (2026-02-19) 🔧

**Goal:** Fix 8 resort issues and 3 guide issues discovered during browser + database audit of the 12 most recent published resorts.

### Resort Issues Found

| # | Priority | Issue | Files |
|---|----------|-------|-------|
| 1 | P0 | resort-linker.ts partial word matching ("fee" → Saas-Fee) | `apps/web/lib/resort-linker.ts` |
| 2 | P1 | Content truncation (max_tokens=1500 too low) | `agents/shared/primitives/content.py`, `runner.py` |
| 3 | P1 | Non-place entities linked to Google Maps | `agents/shared/primitives/intelligence.py` |
| 4 | P2 | Calendar generation missing (all 12 resorts) | `agents/pipeline/runner.py` |
| 5 | P2 | Lodging costs missing | `agents/shared/primitives/costs.py` |
| 6 | P2 | Internal cross-links missed | `agents/shared/primitives/intelligence.py` |
| 7 | P3 | FAQ hedging (list-of-dicts bypasses style pre-pass) | `agents/shared/primitives/style.py` |
| 8 | P3 | Multilingual research not used | Low priority — deferred |

### Guide Issues Found

| # | Issue | Root Cause |
|---|-------|------------|
| G1 | 7 guides stuck in draft since Feb 2 | SkepticExpert in 5-expert panel always rejects → effective threshold 3/4 |
| G2 | Resort links point to generic /resorts | Generation-time link injection fails when resorts aren't published yet |
| G3 | Guide FAQs bypass style pre-pass | Same as P3 — list-of-dicts skipped |

### Fixes Applied

_(in progress)_

---

## GTM Handoff Session (2026-02-18) ✅

**Goal:** Disable newsletter for GTM handoff, create Resend handoff doc, complete affiliate CSV with all 7 network signups, evaluate Codex refactoring recommendations.

### Newsletter Disabled

- Commented out `newsletter_result = asyncio.run(run_weekly_newsletter())` in `agents/cron.py` (~line 371)
- Welcome email sequence still runs daily via Railway cron (separate from newsletter)

### Resend Handoff Doc

- Created `scratchpad/resend-handoff.md` — complete GTM handoff for Resend email system
- Covers: API key locations (Vercel + Railway), sender config, subscriber data (Supabase tables), signup flow, welcome sequence, migration path to other email tools, GA4 tracking already in place

### Affiliate CSV Completed

- Updated `scratchpad/affiliate-programs.csv` from 39 rows to 54 rows
- Discovered 7 networks signed up (was tracking only 3): Travelpayouts (21 programs), Admitad, CJ, FlexOffers, AWIN, AvantLink, Impact
- All affiliate IDs, tracking codes, network statuses, and ACTION items included
- Credentials stored in `memory/affiliates-credentials.md` (gitignored)

### Codex Refactoring Evaluation

Evaluated Codex's 6 refactoring recommendations by reading the actual files:

| # | Recommendation | Verdict | Rationale |
|---|---------------|---------|-----------|
| 1 | API route composition layer | SKIP | Premature abstraction — 4 routes, ~20 lines shared pattern each. Not worth a middleware layer. |
| 2 | Quiz adapter + scoring tests | Tests YES, adapter NO | `scoring.ts` (610 lines) is pure functions, perfectly testable. But the "adapter" extraction has exactly 1 caller — not worth it. |
| 3 | Guide config unification | Low ROI | Real duplication (~30 lines) across 2 files. But extracting a shared config for 2 files is marginal. |
| 4 | Playwright CI | SKIP | Premature for a content site. Browser testing is useful but CI integration adds complexity that doesn't pay off yet. |
| 5 | Migration hygiene tooling | SKIP | One-time problem (duplicate 033 prefix, already fixed in AR round). Tooling for a solved problem. |
| 6 | **Runner.py decomposition** | **THE ONE** | 2,105 lines. Distinct stages (research, generate, style, approve, publish) jammed into one file. This is R18. |

### Key Deliverables

- `scratchpad/resend-handoff.md` — Resend GTM handoff doc
- `scratchpad/affiliate-programs.csv` — 54 programs, 7 networks, all IDs/statuses
- `agents/cron.py` — Newsletter disabled (~line 371)
- `memory/affiliates-credentials.md` — All 7 network logins (NOT in git)

**Arc:**
- Started believing: GTM handoff was mainly about disabling the newsletter and writing a doc
- Ended believing: Deep transcript archaeology revealed 4 more affiliate networks than tracked, and honest evaluation of refactoring recommendations filtered 6 ideas down to 1 genuine priority
- Transformation: From surface-level handoff to comprehensive inventory — the value was in what we didn't know we had

---

## First-Principles Rubric Codification (2026-02-17) ✅

**Goal:** Encode the team’s mental model directly in `AGENTS.md` as an execution rubric, without cross-project references.

### Change Applied

- Added `Execution Rubric (First Principles)` section in `AGENTS.md` covering:
  - Agent-native by default
  - Atomic primitives over monoliths
  - Probabilistic where possible, deterministic where necessary
  - Discovery-led delivery
  - Optimize for agents + users + SEO/GEO/AEO, with MEO-first priority
  - Human judgment in high-stakes loops
  - Definition-of-done quality gates

**Arc:**
- Started believing: The principles were already shared and implicitly applied
- Ended believing: Shared principles need explicit operational encoding to remain consistent across sessions and agents
- Transformation: From implicit understanding to explicit execution contract

---

## Expert Review Loop + Browser QA Hardening (2026-02-17) ✅

**Goal:** Reach strong approval with a full team-style review loop, including mandatory browser UI testing, and remediate any failing gates.

### Fixes Applied

1. **Quiz step runtime stability**
   - Updated `apps/web/app/quiz/[step]/page.tsx` route validation to redirect via `useEffect` instead of render-time router calls
   - Result: fixed `/quiz/ages` 500 runtime failure found in Playwright audit

2. **Guide rendering correctness**
   - Updated `apps/web/app/guides/page.tsx` and `apps/web/app/guides/[slug]/page.tsx` to replace dynamic Tailwind interpolation with static color class maps
   - Updated `apps/web/components/guides/GuideContent.tsx`:
     - fixed invalid route fallback (`/resorts` instead of malformed `/resorts/{slug}`)
     - replaced non-existent classes (`bg-cream-50/50`, `font-body`) with valid classes
   - Result: deterministic styles and valid fallback navigation

3. **API rate-limit IP extraction hardening**
   - Added `apps/web/lib/request-ip.ts` with normalized IP parsing and validation
   - Applied to:
     - `apps/web/app/api/revalidate/route.ts`
     - `apps/web/app/api/subscribe/route.ts`
     - `apps/web/app/api/data-request/route.ts`
     - `apps/web/app/api/contact/route.ts`
   - Result: reduced spoof/garbage header risk and consistent rate-limit identity extraction

4. **Local browser QA signal cleanup**
   - Updated `apps/web/app/layout.tsx` Travelpayouts verification script to skip localhost/127.0.0.1
   - Result: removed local CORS console noise from strict browser QA

### Validation

- `pnpm lint` ✅ (existing `<img>` optimization warnings only)
- `pnpm build` ✅
- `python3 -m compileall -q agents` ✅
- Migration prefix collision check (`uniq -d`) ✅ none
- Strict Playwright QA (desktop + mobile, 16 routes) ✅
  - 16/16 passed
  - 0 page errors
  - 0 console errors

**Arc:**
- Started believing: Green build/lint plus targeted patches were enough for sign-off
- Ended believing: Strong approval requires explicit runtime browser evidence and re-validation loops
- Transformation: From static confidence to expert-gated runtime confidence

---

## Audit Remediation: Migration + Budget + Quiz Correctness (2026-02-17) ✅

**Goal:** Fix highest-severity audit findings that could cause migration drift, incorrect autonomous budget guidance, and skewed quiz rankings.

### Fixes Applied

1. **Migration numbering conflict**
   - Renamed `supabase/migrations/033_gsc_performance.sql` → `supabase/migrations/045_gsc_performance.sql`
   - Made `045_gsc_performance.sql` idempotent (`IF NOT EXISTS` table/indexes + guarded policy creation)
   - Result: removed duplicate `033` prefix collision in migration ordering

2. **Decision-maker budget context**
   - Updated `agents/pipeline/decision_maker.py` budget section to use:
     - `settings.daily_budget_limit`
     - `remaining_budget = max(0.0, daily_limit - daily_spend)`
   - Result: prompt guidance now reflects runtime config, not a stale hardcoded `$5.00`

3. **Quiz scoring source mapping**
   - Updated `apps/web/app/quiz/results/page.tsx` to query and map:
     - `has_ski_school`, `ski_school_min_age`
     - `terrain_beginner_pct`, `terrain_advanced_pct`
   - Removed childcare proxy mapping and negative-prone advanced terrain formula
   - Result: must-have ski school and skill-terrain signals now use correct fields and bounded values

### Validation

- `python3 -m compileall -q agents/pipeline/decision_maker.py` ✅
- `pnpm lint` in `apps/web` ✅ (existing `<img>` warnings only)
- `pnpm build` in `apps/web` ✅
- Duplicate migration prefix check (`uniq -d`) ✅ none

**Arc:**
- Started believing: Remaining issues were mostly medium/low and could be deferred
- Ended believing: Deterministic correctness bugs in migrations/config/ranking inputs needed immediate remediation
- Transformation: From broad audit confidence to targeted correction of high-blast-radius correctness paths

---

## Voice Evolution: Personality-Forward Content (2026-02-15) ✅

**Goal:** Evolve voice from "smart and practical" to "personality-forward" — content worth screenshotting and sending to your partner. 70/30 personality-to-info ratio.

### Section Prompts Rewritten — 6 sections overhauled

All section prompts in `content.py` rewritten to lead with personality, not logistics:
- **getting_there:** Lead with whatever is most interesting (scenic drive, surprising shortcut, airport chaos). NOT "Getting to X is..."
- **where_to_stay:** Lead with a take (apartments crush hotels here, one standout property everyone should know). Tell them which one YOU'D book
- **lift_tickets:** Give the verdict fast. Screaming deal or premium worth paying? Commit to numbers, no hedging
- **on_mountain:** Lead with the ONE thing parents need to know, not terrain percentage breakdown
- **off_mountain:** Paint the vibe first. One-street town? Lively village? Then get specific
- **parent_reviews_summary:** Where honest tension lives. Where parent opinion contradicts official line

### VoiceCoach Evaluation — 6 criteria

Evaluator in `approval.py` rewritten from 5 generic criteria to 6 specific, measurable criteria:
1. **Personality density:** Flag sections that read as pure info delivery
2. **Opening variety:** Flag formulaic opening patterns
3. **Emotional hooks:** At least one sensory/emotional detail (soft guidance)
4. **Sentence rhythm:** Flag 3+ medium-length declarative sentences in a row
5. **Stance strength:** Flag neutral option-presenting without verdicts
6. **Hedging frequency:** Count "roughly", "around", "approximately" before numbers

Test changed: "Would a parent feel informed?" → "Would a parent screenshot this and send it to their partner?"

### Anti-Hedging — deterministic stripping

- `HEDGING_PATTERNS` in `style.py`: regex strips "roughly" and "approximately" before numbers
- Voice profile `avoid` list expanded: "roughly", "around", "typically", "about", "approximately" before numbers
- Guidance: "Pick a number and commit. '90 minutes' not 'roughly 1 hour and 45 minutes'"

### Layer 3 Style Edit — Opus upgrade

- `style.py` Layer 3 upgraded from Sonnet (~$0.08/section) to Opus 4.6 (~$0.40/section)
- Better prose quality justifies 5x cost increase for style editing

### Voice Profile Updates

- 70/30 personality-to-info ratio: "If a paragraph could appear in any resort guide, rewrite it"
- Stance commitment: "Don't present options neutrally, tell them what you'd actually do"
- Rhythm contrast: "Short punchy sentences for verdicts: 'That's the play.' 'Skip it.' 'Done.'"
- Price intro variety: 5+ options instead of defaulting to "Expect to pay" every time
- Emotional hooks: "Paint moments. What does it feel like?"
- "Here's the thing:" and "Here's the deal:" re-allowed sparingly (removed from FORBIDDEN_PHRASES)
- Anti-hedging in avoid list: explicit guidance on committed numbers

### Default Voice Profile — 4 params updated

`content.py`: `voice_profile` default changed from `instagram_mom` to `snowthere_guide` in:
- `write_section()`, `generate_faq()`, `apply_voice()`, `generate_country_intro()`

### Files Modified

| File | Changes |
|------|---------|
| `agents/shared/primitives/approval.py` | VoiceCoach 6-criteria evaluation, new test, new system prompt |
| `agents/shared/primitives/content.py` | 6 section prompts rewritten, system prompt personality-forward, 4 default params |
| `agents/shared/primitives/quick_take.py` | Anti-hedging in calibration examples, varied price intros |
| `agents/shared/primitives/style.py` | Layer 3 Opus upgrade, HEDGING_PATTERNS, re-allow "Here's the thing" |
| `agents/shared/voice_profiles.py` | 70/30 ratio, stance commitment, price variety, emotional hooks, anti-hedging |

**Arc:**
- Started believing: Smart, practical voice was producing quality content
- Ended believing: Smart and practical without personality density produces interchangeable content. 70/30 personality-to-info with stance commitment creates content worth screenshotting
- Transformation: From respectful intelligence to personality-forward intelligence — the voice should make parents send it to their partner, not just nod approvingly

---

## Deep Audit + GA4 Events (2026-02-13) ✅

**Goal:** Audit 4 new resorts (Stubai, Arosa, Engelberg, Revelstoke), fix systemic pipeline bugs, deploy GA4 custom events.

### 6 Systemic Bugs Fixed

| Bug | Root Cause | Fix |
|-----|------------|-----|
| Calendar never generated | No primitive existed | NEW `generate_ski_calendar()` in calendar.py (~$0.003/resort via Haiku) |
| Coordinates missing for new resorts | `extract_coordinates()` never called after resort creation | Added call in runner.py |
| data_completeness always 0.0 | 12 columns missing from `RESORT_FAMILY_METRICS_COLUMNS` allowlist | Added to database.py |
| Duplicate title "| Snowthere | Snowthere" | Layout template + content.py both appending suffix | Strip suffix in page.tsx + don't generate in content.py |
| Pricing cache → resort_costs disconnect | `research_data["costs"]` empty by write time | Cache fallback at write time + automatic USD column updates |
| Content truncation | Not detected | Added truncation detection in runner.py |

### Additional Fixes

- **Content model:** Opus 4.5 → Opus 4.6
- **LLM preamble stripping:** 9 phrases (e.g., "Here's the content...", "I'll create...") in deterministic style pre-pass + voice profile avoid list
- **Entity link guardrails:** Blacklist + structural filters (colon-ending text, age-range patterns, all-lowercase short phrases)
- **Em-dash enforcement:** Comprehensive removal in deterministic pre-pass (spaced, unspaced, trailing, stray patterns)
- **Pricing cache fallback:** `acquire_resort_costs()` now writes to resort_costs via cache fallback
- **Ski quality calendar:** 495 entries backfilled across all 99 resorts
- **Stubai Glacier coordinates:** Added to KNOWN_COORDINATES dict
- **GA4 custom events:** `quiz_complete` (result_count, top_result) + `affiliate_click` (partner_name from URL domain)

### Key Commits
```
0a53767 feat: Add quiz_complete and affiliate_click GA4 custom events
550d1fa fix: Comprehensive em-dash/en-dash removal in deterministic pre-pass
8fda4f9 feat: Add ski quality calendar generation primitive + backfill all 99 resorts
eecdf0b fix: Add pricing cache fallback + USD column updates in pipeline
6ae9e51 fix: Add entity link guardrails to prevent nonsensical Maps links
6daf220 fix: Add Stubai Glacier to KNOWN_COORDINATES, backfill 4 new resort coords
dc71625 fix: Deep audit fixes — Opus 4.6, preamble stripping, data completeness, title dedup, coordinates
```

**Arc:**
- Started believing: The pipeline was producing quality content at scale
- Ended believing: 6 systemic bugs were silently degrading every resort — calendar never generated, coordinates missing, completeness always 0.0, titles duplicated, pricing disconnected, content truncated
- Transformation: From trusting pipeline output to auditing individual resort pages, revealing systemic issues invisible in aggregate logs

---

## Affiliate Verification + Pinterest (2026-02-12-13) ✅

**Goal:** Add tracking pixels and verification tags for affiliate networks and Pinterest.

- **Pinterest tracking pixel:** Tag ID 2613199211710 via next/script
- **AvantLink:** Multiple attempts to add verification tag (script tag, next/script, http://, plain) — ultimately removed (broken)
- **Travelpayouts:** Added tp-em.com to CSP for verification
- **SEO duplicate title fix:** Additional instances found and fixed

### Key Commits
```
766656f feat: Add Pinterest tracking pixel (Tag ID 2613199211710)
4fe3f15 fix: Remove broken AvantLink script, keep Pinterest meta tag
504d7d0 feat: Add affiliate verification tags + fix SEO duplicate titles
```

---

## Coordinates + Pricing Backfill (2026-02-12) ✅

**Goal:** Backfill coordinates and pricing data for all 95 resorts that had gaps.

- All 95 resorts now have coordinates and pricing data
- Fills gaps left by earlier pipeline runs that missed coordinate extraction

### Key Commits
```
f51f23b fix: Backfill coordinates + pricing for all 95 resorts
```

---

## Round 24: Style Primitive + Pricing Redesign (2026-02-12) ✅

**Goal:** Build 3-layer style editing system, redesign pricing acquisition, add snow conditions chart, fix coordinate issues.

### 3-Layer Style Primitive — COMMITTED (120610e)

1. **Layer 1: Deterministic pre-pass** (free) — Em-dash/en-dash removal, preamble stripping, whitespace cleanup
2. **Layer 2: Haiku contextual** (~$0.002/section) — Context-aware em-dash replacement (comma, period, or removal based on position)
3. **Layer 3: Sonnet style edit** (~$0.08/section) — Full voice editing for natural prose

Results: Alta 24→4 em-dashes, Crested Butte 19→2 em-dashes.

### Pricing Redesign — COMMITTED (120610e)

4. **Exa discovery** — Finds official resort pricing pages via semantic search
5. **Claude Haiku interpretation** — Extracts structured pricing from discovered pages
6. **Country-specific validation** — Rejects impossible prices per-country (Mount Bachelor $23 → $149, Sunday River $29 → $129)
7. **Migration 044:** pricing_cache provenance columns

### SnowConditionsChart — COMMITTED (120610e)

8. **Animated bar chart** — framer-motion animations, teal/gold/coral color tiers
9. **Crowd dots** — Visual indicator of crowd levels per month
10. **"Best" pill** — Highlights recommended months
11. **Southern Hemisphere** — Month sorting adjusted (Jun-Oct instead of Dec-Apr)

### Coordinate Fixes — COMMITTED (120610e)

12. **Nominatim query reordered** — "ski area" first in search
13. **Country codes parameter** — Constrains Nominatim search to correct country
14. **Country bounding box validation** — Rejects coordinates outside country bounds
15. **Google Geocoding fallback** — When Nominatim fails

### Pipeline Fixes — COMMITTED (120610e)

16. **429 errors** — Now reset to "pending" not "rejected" (allows retry next day)
17. **Style applied before all DB writes** — Deterministic style runs on every content section
18. **Em-dash/en-dash in approval** — Added to FORBIDDEN_PATTERNS in approval.py

### Key Commits
```
120610e feat: Style primitive, pricing redesign, snow chart, pipeline fixes (Round 24)
```

### New Files
- `agents/shared/primitives/style.py` — 3-layer style editing primitive
- `agents/shared/style_profiles.py` — Style profile configuration
- `agents/scripts/backfill_style.py` — Style backfill script
- `agents/scripts/fix_feb12_resorts.py` — Fix specific resort data
- `agents/shared/primitives/costs.py` — Major rewrite with Exa discovery + validation
- `apps/web/components/resort/SnowConditionsChart.tsx` — Animated snow chart
- `supabase/migrations/044_pricing_cache_provenance.sql` — Provenance columns

**Arc:**
- Started believing: Em-dashes just need a regex find-and-replace and pricing just needs a better prompt
- Ended believing: Em-dashes need context-aware replacement (3 layers for different complexity levels) and pricing needs discovery + interpretation + validation as separate stages
- Transformation: From single-pass solutions to multi-layer systems where each layer handles a different complexity level

---

## Round 23: Content Refresh System (2026-02-11) ✅

**Goal:** Align VoiceCoach with MEO voice, build batch content regeneration system for existing resorts and guides.

### Voice Alignment — COMMITTED (e1762c4)

1. **VoiceCoach prompt** — Aligned with MEO voice (smart, practical, expert) — removed "warmth" as primary evaluator criterion
2. **4 default voice_profile params** — Changed from `instagram_mom` to `snowthere_guide` in approval.py
3. **Newsletter voice** — Dropped "warm" from newsletter prompts, added VOICE directive to parent hack section

### Batch Regeneration — COMMITTED (e1762c4)

4. **Resort batch mode** — `regenerate_resort_content.py` now supports `--batch`, `--batch-limit`, `--batch-offset` for bulk content refresh
5. **Guide regeneration** — New `regenerate_guide_content.py` script for refreshing draft + published guide content

### Key Commits
```
e1762c4 feat: Content refresh system + guide pipeline fixes (Round 23)
```

**Arc:**
- Started believing: Content regeneration is a one-resort-at-a-time manual process
- Ended believing: Batch regeneration with voice-aligned quality gates enables systematic content refresh across the entire corpus
- Transformation: From manual per-resort updates to scalable batch content refresh with consistent voice application

---

## Round 22: MEO Optimization + Voice De-Mandating (2026-02-10) ✅

**Goal:** Optimize content for AI search engines (Exa, ChatGPT, Perplexity, Google AI Overviews) and de-mandate prescriptive voice rules that were creating formulaic content.

### Research Findings

- **Exa:** Trained on LINK PREDICTION ("which URL follows this text"), not text similarity
- **Princeton GEO (peer-reviewed, 10K queries):** Quotations +41%, Statistics +33%, Fluency +29%, Citing sources +28%, Keyword stuffing -9%
- **Content freshness:** 3.2x more AI citations for content updated within 30 days
- **Tables/lists:** 2.5x more cited than prose (already doing well)
- **Bing:** ChatGPT + Perplexity both start with Bing's index — confirmed connected (124 URLs indexed)

### Voice De-Mandating — COMMITTED (ad373c6)

1. **content.py system prompt rewrite** — Replaced prescriptive rules ("Use at least ONE per section", "Every paragraph must have you/your", "~80/20 ratio") with probabilistic personality guidance ("emerge NATURALLY", "Let rhythm emerge", "internalize these, don't mechanically apply")
2. **Anti-repetition block** — Dedicated system prompt section preventing repeated facts/numbers/adjectives across sections
3. **"Content that gets cited" MEO framing** — Lead with quotable take, self-contained paragraphs, named entities for embeddings, source attribution, price contextualization
4. **voice_profiles.py** — Removed ratio mandate, simplified opener rule, added 2 anti-repetition avoid entries

### Frontend MEO Changes — COMMITTED (ad373c6)

5. **Link-predictive titles** — `"Family Ski Guide: {Name} with Kids"` (was `"{Name} Family Ski Guide"`) — matches how people describe links when sharing
6. **Question-based headings** — All 6 section headings converted to questions, 2 of 6 include resort name for RAG chunk independence without keyword stuffing
7. **TOC sidebar labels** — Updated to short question format ("Getting There?", "Lift Ticket Costs?", etc.)
8. **Content freshness dates** — Both LastUpdated.tsx and QuickScoreSummary.tsx now show day (e.g., "Feb 7, 2026" not "Feb 2026")
9. **generate_seo_meta() fallback** — Aligned with link-predictive title format

### Guide Voice Alignment — COMMITTED (ad373c6)

10. **guides.py voice** — Updated from "warm, practical, encouraging. Like a helpful ski mom friend" to "smart, practical, encouraging. Like a well-traveled friend who respects your time" + MEO principles (lead with take, cite sources, no repetition)
11. **guides.py system prompt** — "Be smart, practical, and specific. Lead with your take, not a description."

### Expert Review — ALL APPROVE/PASS

| Reviewer | Verdict |
|----------|---------|
| Python (Kieran) | APPROVE (consistency gap with approval.py noted as follow-up) |
| Pattern Consistency | APPROVE (pipeline production path CLEAN, stale defaults functionally OK via alias) |
| Code Simplicity | APPROVE (triple-layer reinforcement is intentional belt-and-suspenders) |
| Architecture | APPROVE (selective 2/6 entity naming well-calibrated, title format aligned) |
| UI Browser Test | PASS (question headings, TOC labels, date format verified on St. Anton + Les Gets) |
| Python Round 2 | PASS (SEO title + QuickScoreSummary fixes correct) |
| UI Retest | PASS ("Updated Jan 23, 2026" confirmed, all headings intact) |

### Vercel Build Fix — COMMITTED (a7edaaa)

12. **Array.isArray() guards** — Garmisch-Partenkirchen had a JSONB field stored as a non-array truthy value, causing `g.map is not a function` during Vercel prerendering. The `|| []` fallback only catches null/undefined, not strings/objects. Fix: replaced 7 `|| []` guards with `Array.isArray()` across `page.tsx` (faqs, calendar, passes, images, links, perfect_if, skip_if).
13. **4 consecutive Vercel deployments were failing** — commits `53d3503`, `7b7dbd9`, `ad373c6`, `0c79dd5` all crashed on the same resort. Production was stuck on `a0fea02` (Feb 8). Now fixed, all MEO changes live.

### Key Commits
```
a7edaaa fix: Add Array.isArray() guards to prevent Vercel build failure
ad373c6 feat: MEO optimization + voice de-mandating + question-based headings
```

### Section Heading Changes

| Old | New | Entity Name? |
|-----|-----|--------------|
| Getting There | How Do You Get to {resort.name}? | Yes |
| Where to Stay | Where Should Your Family Stay? | No |
| Lift Tickets & Passes | How Much Do Lift Tickets Cost at {resort.name}? | Yes |
| On the Mountain | What's the Skiing Like for Families? | No |
| Off the Mountain | What Can You Do Off the Slopes? | No |
| What Parents Say | What Do Other Parents Think? | No |

### Follow-up Items (not blockers)

- approval.py VoiceCoach evaluator still says "warmth" (functionally OK, voice profile injection handles it)
- MCP server descriptions still reference `instagram_mom` (functionally OK via alias)
- Default params in content.py/approval.py still use `instagram_mom` (functionally equivalent)
- Stored SEO titles in DB use old format — new resorts will get link-predictive format automatically

**Arc:**
- Started believing: Prescriptive voice rules (80/20 ratio, mandatory patterns per section) produce consistent quality
- Ended believing: Prescriptive rules produce formulaic content — probabilistic personality guidance with anti-repetition lets the LLM internalize voice rather than mechanically satisfy checklists
- Transformation: From mandating voice patterns to trusting the model with personality guidance, and from traditional SEO to Meaning Engine Optimization for AI citation

---

## Round 21: Voice Rebalancing — Wirecutter + Personality (2026-02-08) ✅

**Goal:** Rebalance voice from "Instagram mom" to "Morning Brew for family ski trips" — smart, witty, efficient. Add future-casting, self-contained paragraph rules, child price floor, multilingual research, thin content gate.

### Voice Rebalancing — COMMITTED (fd92739, 5f1806e, 53d3503)

1. **Voice identity shift** — From "Instagram mom" (performative encouragement) to "Morning Brew meets ski trip planning" (smart, witty, efficient)
2. **SNOWTHERE_GUIDE profile** — New tone items: "Smart and clear", "Confident expertise without being preachy", "Honest tension", "Rhythmic variety", "Future-casting"
3. **Personality toolkit** — "Pro tip:", "Locals know:", "The move:", parenthetical humor, tension patterns, future-casting patterns
4. **Avoid list expanded** — Em-dash ban (non-negotiable), dropped articles, section openers as descriptions, bare prices, cold inventory lists, third-person detachment
5. **Include list expanded** — BLUF, self-contained paragraphs, future-casting, price context, foreign term translation, resort full name usage, credibility through counting
6. **Child price floor** — `max(child_price, adult_price * 0.5)` prevents $0 child prices
7. **Self-contained paragraph rule** — Every paragraph must make sense without reading the headline

### Multilingual Research + Thin Content Gate — COMMITTED (7b7dbd9)

8. **Multilingual research queries** — Resort research now searches in local language (German, French, Japanese, etc.) using Claude for translation
9. **Thin content gate** — Sections with < 200 words rejected, resort with < 3 substantial sections flagged for manual review
10. **Voice prompt hardening** — Section prompts now include explicit voice guidance with concrete examples

### Expert Review — ALL PASS

| Reviewer | Verdict |
|----------|---------|
| Python (Kieran) x3 rounds | APPROVE |
| Pattern Consistency x3 rounds | APPROVE |
| Code Simplicity x3 rounds | APPROVE |

### Key Commits
```
7b7dbd9 feat: Voice prompt hardening + multilingual research + thin content gate
53d3503 fix: Child price floor + voice future-casting + self-contained paragraphs
5f1806e fix: Resolve voice rebalancing consistency issues from expert review
fd92739 feat: Voice rebalancing — Wirecutter + personality (Level B)
e34007a fix: Update PERFECT_PAGE_CHECKLIST and learnings.md stale word counts
a0fea02 docs: Update compound-beads docs with current Quick Take word ranges
```

**Arc:**
- Started believing: The Instagram mom voice was the right voice for family ski content
- Ended believing: A Morning Brew / Wirecutter style (smart, practical, witty) serves families better than performative enthusiasm — parents are intelligent adults doing research
- Transformation: From performative encouragement to respectful intelligence — the voice shift from "Instagram mom" to "smart friend who respects your time"

---

## Round 20: Content Quality & Linking Overhaul + Type Safety (2026-02-06) ✅

**Goal:** Improve content quality (Quick Takes, taglines, scoring), add Skyscanner flight links, inject resort links into guides, eliminate TypeScript `as any` casts, harden security across all pages.

### Content Quality — COMMITTED (b5c3e8f)

1. **Strong-tag-first entity extraction** — Eliminates ~$0.03/resort Claude calls by parsing `<strong>` tags before falling back to LLM extraction
2. **Airport links → Skyscanner** — IATA code extraction from content, flight search URLs generated automatically
3. **Quick Takes reformatted** — 50-90 word single paragraph (was 80-120 word 4-part editorial model, validation accepts up to 95)
4. **Taglines calibrated** — Fact-based generation + forbidden pattern regex blocklist (blocks "hidden gem", "world-class", etc.)
5. **Three-layer hybrid scoring** — structural 30% + content LLM 50% + review 20%, completeness multiplier removed
6. **Dollar sign always shown** — Resort cards show $$ fallback when `estimated_family_daily` is NULL
7. **Guide resort links** — Internal resort links injected into guide prose via `resort-linker.ts`
8. **Content prompts** — Mandatory `<strong>` for named businesses, IATA codes in getting_there
9. **3 new backfill scripts** — `backfill_costs.py`, `backfill_quick_takes.py`, `backfill_hybrid_scores.py`
10. **`calculate_structural_score()`** — Replaces `calculate_family_score()` (alias kept for compatibility)

### Type Safety + Security — COMMITTED (0c7121b)

11. **Zero `as any` casts** — Defined `SupabaseResortRow`, `SimilarityRow` types; exported `TrailMapData`; fixed `UsefulLinks` null types
12. **8 missing fields in database.types.ts** — `data_completeness`, `structural_score`, `content_score`, `review_score`, `score_confidence`, `score_reasoning`, `score_dimensions`, `scored_at`
13. **`sanitizeHTML()` hardening** — Applied to ContentRenderer content sections (6), GuideContent IntroSection + TextSection
14. **`sanitizeJSON()` hardening** — Applied to all JSON-LD blocks across 7 pages (homepage, /resorts, /guides, /guides/[slug], /resorts/[country], /resorts/[country]/[slug], /collections/[collection])
15. **Nullish coalescing** — `||` → `??` for score_confidence, explicit `!= null` for data_completeness checks

### Migrations

- **042:** `structural_score`, `content_score`, `review_score`, `score_confidence`, `score_reasoning`, `score_dimensions`, `scored_at` columns on `resort_family_metrics`
- **043:** `hybrid_score` column on `resort_family_metrics`
- Both applied to cloud Supabase via SQL Editor (Feb 6)

### Expert Review — ALL PASS

| Reviewer | Verdict |
|----------|---------|
| Security (full app audit) | STRONG APPROVE |
| Security (backfills + data flow) | APPROVE |
| TypeScript (type safety re-review) | STRONG APPROVE |
| TypeScript (original R20) | APPROVE (all findings fixed) |
| Python | APPROVE |
| Code Simplicity | APPROVE |
| Performance | APPROVE |

### UI Testing — PASS
- Zermatt resort page: all sections render (Quick Take, Getting There, entity links, sidebar, trail map, FAQ)
- Resort listing: 75 resorts with $$ price badges
- Build: 96 static pages, zero errors

### Key Commits
```
0c7121b fix: Type safety + security hardening across frontend
b5c3e8f feat: Round 20 — Content quality & linking overhaul
```

### Backfills COMPLETE (Feb 7)

| Script | Result |
|--------|--------|
| Costs | 0 needed (all resorts had cost data) |
| Links (`--clear-cache`) | 247 entity links across 66 resorts, 2,325 stale cache entries cleared |
| Quick Takes | 44/75 updated (31 failed: mostly 1-8 words over 65-word limit, 3 had "legendary") |
| Taglines | 75/75 updated (quality evaluator JSON parse errors fell back to 0.50 defaults) |
| Hybrid Scores | 75/75 scored (range 6.0-9.1, all high confidence) |

**Top hybrid scores:** Serfaus-Fiss-Ladis 9.1, Les Gets 8.1, Aspen Snowmass 8.0, Lake Louise 8.0, Saas-Fee 7.9

### Pipeline Bug Fix (f3e892c, Feb 7)

Feb 7 daily cron: 0 published, 5 failed (Snowbasin, Stratton, Taos, Big White, Las Leñas). Two bugs:

1. **runner.py:** Local `from datetime import datetime, timezone` at line 1309 shadowed module-level import → `UnboundLocalError` at line 553 before the local import executed. Fix: moved `timezone` to module-level import, deleted local.
2. **discovery_agent.py + quality_agent.py:** Called `check_budget()` with no args (expects `required_usd: float` → `bool`). Fix: replaced with `settings.daily_budget_limit - get_daily_spend()` (3 call sites).

Both bugs introduced in Round 20 commit (b5c3e8f). Fix pushed to origin/main, Railway auto-deployed.

### Pending
- Sign up for affiliate networks (Travelpayouts, Skiset, World Nomads)
- Apply migration 036 to cloud Supabase (GDPR data_requests table)
- Re-run quick takes for 31 resorts over word limit (consider relaxing to 70 words)
- Homepage redesign (deferred from R14)

**Arc:**
- Started believing: Content quality improvements and type safety are separate concerns
- Ended believing: Content quality, type safety, and security hardening form a single trust layer
- Transformation: From treating content, types, and security as independent workstreams to a unified quality-and-trust layer where each reinforces the others

---

## Round 19: SEO Fixes, Programmatic Pages & Country Content (2026-02-05) ✅

**Goal:** Fix critical SEO issues (invisible H1, missing static params, slow ISR), add programmatic collection pages, build country intro content system.

### SEO Fixes — COMMITTED (cae670a)

1. **HeroSpielplatz → server component** — Was `'use client'`, making H1 invisible to crawlers
2. **Country pages `generateStaticParams()`** — Was missing, preventing static generation
3. **ISR reduced to 6h** — Was 12h, too slow for content updates
4. **Canonical leak** — Verified Vercel already has 308 redirect (GSC duplicates are legacy)

### Programmatic Pages — 6 CREATED

5. **Collection pages** at `/collections/[collection]` — best-for-beginners, best-for-toddlers, best-value, best-for-teens, shortest-transfer, best-ski-schools
6. **Route constraint:** Can't have `[collection]` and `[country]` at same level under `/resorts/`

### Country Content System

7. **Country intro content** — AI-generated intros for all 14 country pages
8. **BreadcrumbList JSON-LD** — Added to country pages

### Key Commits
```
cae670a feat: Round 19 — SEO fixes, programmatic pages, country content system
```

**Arc:**
- Started believing: The homepage H1 was rendering correctly and country pages were properly configured
- Ended believing: Client components hide H1 from crawlers, missing generateStaticParams prevents static generation
- Transformation: From trusting client-rendered content to ensuring all critical SEO elements are server-rendered and statically generated

---

## Pipeline Improvements (2026-02-05) ✅

**Goal:** Fix low entity link density, stale detection bug, add light refresh mode for efficiency

### Issue 1: Low Entity Link Density — FIXED

**Problem:** Whitefish only got 3 links when 20+ were possible. Claude's entity extraction was returning conservative confidence scores.

**Fixes applied:**
1. **Extraction prompt** — Added HIGH confidence (0.8+) guidance for named businesses
2. **Multi-entity example** — JSON template now shows 3 entities (was 1)
3. **System prompt strengthened** — Explicit confidence examples (Kandahar Lodge → 0.9)
4. **Confidence threshold** — 0.6 → 0.5 in `external_links.py`
5. **City exclusion** — Explicitly exclude major cities/metros from extraction (Sandy, Draper, Vancouver, etc.)

### Issue 2: Stale Detection Bug — FIXED

**Problem:** Deer Valley was refreshed after 10 days, not 30+. `get_stale_resorts()` calculated cutoff but never used it.

**Fix:** Added `.or_(f"last_refreshed.lt.{cutoff_date},last_refreshed.is.null")` filter in `publishing.py`

### Issue 3: Light Refresh Mode — IMPLEMENTED

**Problem:** Full refresh costs ~$3/resort but resorts don't change much.

**Fix:** New `_run_light_refresh()` function (~180 lines) in `runner.py`:
- Skips research, content generation
- Only updates costs, entity links, images
- Cost: ~$0.50 vs ~$3 (85% reduction)
- Added `--light-refresh` CLI flag to `cron.py`
- Stale resorts automatically use light refresh

### Issue 4: JSON Serialization Error — FIXED

**Problem:** `TypeError: Object of type KeywordResearchConfig is not JSON serializable` in audit logs

**Fix:** Added `json.loads(json.dumps(metadata or {}, default=str))` in `log_reasoning()` in `system.py`

### Backfills Performed

| Resort | Before | After |
|--------|--------|-------|
| Whitefish | 3 | 12 |
| Obergurgl-Hochgurgl | 4 | 14 |
| Okemo | 4 | 14 |
| Snowbird | 10 | 29 |
| Sun Peaks | 9 | 17 |

### Files Modified

| File | Changes |
|------|---------|
| `agents/shared/primitives/intelligence.py` | Extraction prompt improvements, city exclusion |
| `agents/shared/primitives/external_links.py` | Confidence threshold 0.6 → 0.5 |
| `agents/shared/primitives/publishing.py` | Stale detection fix |
| `agents/shared/primitives/system.py` | JSON serialization for dataclasses |
| `agents/pipeline/orchestrator.py` | refresh_mode parameter |
| `agents/pipeline/runner.py` | `_run_light_refresh()` function |
| `agents/cron.py` | `--light-refresh` flag, "refreshed" exit code |

### Key Commits
```
1e218e2 fix: Serialize metadata in log_reasoning to handle dataclasses
82a3951 fix: Exclude major cities from entity extraction
b182e33 fix: Treat 'refreshed' status as success in exit code
98cbc6b feat: Pipeline improvements — entity extraction, stale detection fix, light refresh mode
```

### Railway Pipeline Investigation

Used 3-agent expert panel to investigate today's Railway run:
- **Published with issues (5 resorts):** By design — publish-first model, queued for improvement
- **Tagline retries (48):** By design — strict dual-threshold (overall 0.7 AND structure_novelty 0.6)
- **JSON serialization error:** Fixed with metadata serialization

**Arc:**
- Started believing: Entity extraction confidence scores were appropriate and stale detection worked correctly
- Ended believing: Conservative extraction was missing valid entities; stale detection had a bug; full refresh is overkill for maintenance
- Transformation: From accepting pipeline defaults to targeted improvements that increase link density 3x and reduce refresh costs 85%

---

## Linking Strategy Overhaul (2026-02-02) ✅

**Goal:** Fix broken 3-layer linking system — context-aware entity link destinations, UTMs on in-content links, rel attribute preservation, full backfill across all published resorts.

### Phase 1: Fix Infrastructure — DEPLOYED
1. **Google Places API types fixed** — `grocery_or_supermarket` → `grocery_store`, `point_of_interest` → omit (Table B only), added `sporting_goods_store`, `tourist_attraction`, `transit_station`
2. **API key fallback** — Falls back to `settings.google_api_key` if `google_places_api_key` missing
3. **Error logging** — Response body logged on error, not just status code
4. **Entity type constraint expanded** — Migrations 037+038: added `airport`, `location`, `childcare`, `bar`, `cafe`, `spa`, `attraction`, `retail`, `transportation` to `entity_link_cache` CHECK constraint

### Phase 2: Context-Aware Link Destinations — DEPLOYED
5. **Data-driven priority table** — Replaced nested if/elif with `PRIORITY` dict per entity type:
   - Hotels/rentals → affiliate > direct > maps (parents want to book)
   - Restaurants/grocery → maps > direct (parents need directions)
   - Ski schools → direct > maps (parents want to register)
   - Activities/transport → direct > maps (booking or finding)
6. **UTMs on in-content links** — `utm_medium=in_content` distinct from sidebar's `resort_page`
7. **Dofollow for entity links** — `rel="noopener"` (sends referrer for partner attribution)
8. **Affiliate links** — `rel="sponsored noopener"` (Google-compliant)
9. **Maps links** — `rel="nofollow noopener"` (no equity, still sends referrer)

### Phase 3: Content Generation Improvements — DEPLOYED
10. **Enhanced section prompts** — Request named entities with `<strong>` tags for where_to_stay, on_mountain, off_mountain, getting_there
11. **Sidebar link curation** — Increased target from 3-8 to 8-15 links, minimums per category

### Phase 4: Frontend Polish — DEPLOYED
12. **sanitize.ts rel preservation** — Allowlist validation: only `noopener`, `noreferrer`, `nofollow`, `sponsored`, `ugc` tokens pass through
13. **html.escape defense-in-depth** — `html.escape(link_url, quote=True)` before href interpolation
14. **Parent-friendly labels** — "Where to Stay", "Ski Lessons", "Rent Gear", etc.
15. **Sidebar UsefulLinks** — Unified rel scheme matching entity links

### Phase 5: Backfill — COMPLETE
16. **New script** — `agents/scripts/backfill_links.py` with `--dry-run`, `--limit`, `--sidebar-only`, `--content-only`, `--resort` flags
17. **Results** — 371 entity links injected across 58 resorts, 1,262 entity_link_cache entries

### Phase 6: Expert Review — ALL PASS (2 rounds)
18. **Round 1** — Security Sentinel, Architecture Strategist, Code Simplicity, Data Integrity Guardian, Performance Oracle identified 6 findings
19. **Round 2** — All fixes applied, re-review: 5/5 PASS with no blocking findings

### Dead Code Removed
- `log_link_click()` (44 lines), `get_click_stats()` (53 lines), `clear_broken_link()` (19 lines), `get_broken_link_count()` (22 lines)
- Unused `hashlib` import, dead `skip_sections` set
- Dead exports removed from `__init__.py`
- Net: ~182 lines removed

### Files Modified
| File | Changes |
|------|---------|
| `agents/shared/primitives/external_links.py` | Context-aware destinations, UTMs, html.escape, dead code removal, type mapping |
| `agents/shared/primitives/__init__.py` | Removed dead exports |
| `agents/shared/primitives/content.py` | Enhanced section prompts requesting named entities |
| `agents/shared/primitives/intelligence.py` | Sidebar link curation 8-15 target |
| `agents/shared/primitives/links.py` | UTM campaign param fix |
| `agents/pipeline/runner.py` | Pass resort_slug to inject_links_in_content_sections |
| `apps/web/lib/sanitize.ts` | Rel allowlist validation, preserve existing tokens |
| `apps/web/components/resort/UsefulLinks.tsx` | Parent-friendly labels, unified rel |
| `supabase/migrations/037_expand_entity_types.sql` | Expand CHECK constraint |
| `supabase/migrations/038_add_retail_transportation_entity_types.sql` | Add retail + transportation |
| `agents/scripts/backfill_links.py` | **NEW** — backfill script |

### Key Commits
```
075f681 feat: Linking strategy overhaul — context-aware destinations, UTMs, rel preservation
32a855d fix: Use valid Places API (New) types for includedType parameter
18700fb fix: Expand entity_link_cache valid types + migration 037
1412d97 fix: Send referrer on all entity links for partner traffic attribution
ede019f refactor: Expert review fixes — html.escape, dead code removal, rel allowlist
```

### Verified on Live Site
- Zermatt page: entity links for Hotel Sonne, Hotel Astoria, Wolli Park, Chez Vrony, Coop, Skiguide Zermatt, etc.
- Sidebar links: UTM params visible in URLs
- rel attributes: correct per entity type (dofollow for entities, sponsored for affiliates)

**Arc:**
- Started believing: External linking is a flat priority chain — affiliate beats direct beats maps for everything
- Ended believing: Link destinations must match user intent by entity type — parents want to book hotels, get restaurant directions, register for ski school
- Transformation: From generic link injection to context-aware destinations that match what parents actually do with each entity type

---

## Round 16: Error Handling & Polish (2026-01-30) ✅

**Goal:** Improve resilience, edge-case handling, and interactive filtering. Comprehensive browser testing.

### Error Boundaries — DEPLOYED
1. **`error.tsx`** — Global error boundary with branded Spielplatz design, retry button, go-home fallback
2. **`not-found.tsx`** — Custom 404 page: "This trail doesn't exist" with Browse Resorts and Go Home buttons

### Loading Skeletons — DEPLOYED
3. **`resorts/loading.tsx`** — Breadcrumb, hero, filter bar, and card grid skeleton with `animate-pulse`
4. **`resorts/[country]/[slug]/loading.tsx`** — Resort detail page skeleton (hero image, content sections)
5. **`guides/[slug]/loading.tsx`** — Guide page skeleton (hero, content sections)

### Resort Filtering System — DEPLOYED
6. **`ResortFilters.tsx`** — Country pills, age group pills (0-3, 4-7, 8-12, 13+), budget pills ($-$$$$), sort options (Family Score, Price, A-Z)
7. **`ResortGrid.tsx`** — Country-grouped display (default) or flat list (when sorted by Price/A-Z), empty state with newsletter CTA
8. **`ResortCard.tsx`** — Card component with hero image, score badge, price badge ($/$$/$$$/$$$$), age range, region
9. **`SearchInput.tsx`** — Debounced (300ms) search input with URL sync, clear button
10. **`resort-filters.ts`** — Filter logic: URL search params ↔ filter state, country/age/budget/search matching
11. **`resorts/page.tsx`** — Updated to use filtering components, sticky filter bar with backdrop blur
12. **`resorts/[country]/page.tsx`** — Country-scoped filtering (no country pills, scoped search placeholder)

### GDPR Data Request — DEPLOYED (migration pending)
13. **`DataRequestForm.tsx`** — Email input + deletion/access toggle, loading/success/error states, GDPR copy
14. **`api/data-request/route.ts`** — POST endpoint with in-memory rate limiting (2/min/IP), email validation, Supabase insert
15. **`privacy/page.tsx`** — Updated with "Exercise Your Rights" section containing data request form
16. **Migration 036** — `data_requests` table with RLS, unique index per email/type/day

### CSP Headers — DEPLOYED
17. **`vercel.json`** — Tightened CSP: `img-src` now HTTPS-only, added `object-src 'none'`

### Comprehensive Browser Testing — ALL PASS
- **15 test categories** executed via Playwright browser MCP tools
- **3 customer walkthroughs**: First-time visitor, parent with toddlers, power user (direct URL)
- **Build verification**: `pnpm build` succeeded — 76 pages, 0 errors

### Blocked
- **Test 12.3 (GDPR form submission)**: Returns 500 because migration 036 not yet applied to cloud Supabase. Code is correct; needs `supabase db push` or SQL Editor apply.

**Files created:**
- `apps/web/app/error.tsx`, `apps/web/app/not-found.tsx`
- `apps/web/app/resorts/loading.tsx`, `apps/web/app/resorts/[country]/[slug]/loading.tsx`, `apps/web/app/guides/[slug]/loading.tsx`
- `apps/web/components/resort/ResortFilters.tsx`, `ResortGrid.tsx`, `ResortCard.tsx`, `SearchInput.tsx`
- `apps/web/lib/resort-filters.ts`
- `apps/web/components/DataRequestForm.tsx`, `apps/web/app/api/data-request/route.ts`
- `supabase/migrations/036_data_requests.sql`

**Arc:**
- Started believing: Error handling and polish is about adding safety nets around existing code
- Ended believing: Polish means building complete interactive experiences — filtering, loading, error recovery, and privacy rights are all user-facing quality
- Transformation: From defensive code additions to cohesive user experience where every state (loading, empty, error, filtered) is intentionally designed

---

## Round 15: GEO & Rich Results Enhancement + Data Quality Backfill (2026-01-30) ✅

**Goal:** Maximize AI citability and search rich results. Run data quality backfill.

### Schema & Sitemap — DEPLOYED
1. **WebSite JSON-LD** on homepage — includes SearchAction for sitelinks search box
2. **Organization JSON-LD** on homepage — name, URL, logo, founding date
3. **ItemList JSON-LD** on /resorts — dynamic list from published resorts with position, name, URL, tagline
4. **ItemList JSON-LD** on /guides — dynamic list from published guides with position, name, URL, excerpt
5. **Image sitemap extension** — `xmlns:image` namespace, `<image:image>` tags for all resort images
6. **Legal pages in sitemap** — /about, /methodology, /contact, /privacy, /terms, /quiz (monthly, priority 0.3)
7. **Guides revalidate** — Added `revalidate = 3600` (was missing)

### Data Quality Backfill — APPLIED
- **Migration 033 applied** via Supabase SQL Editor (`data_completeness` column + `NOTIFY pgrst, 'reload schema'`)
- **38 resorts processed**, 33 updated, 5 unchanged, 0 errors
- **Completeness: 30% → 43% average**
- **Full tables: 3 → 7 resorts** (Lake Louise, Cerro Catedral, Aspen Snowmass, Serfaus-Fiss-Ladis, Niseko, Killington, Lech-Zürs)
- **Hidden tables halved: 18 → 9 resorts**
- **Score range widened: 5.4-7.8 → 3.8-8.3** (better differentiation)
- **Tavily API key refreshed** (old key expired, new key in .env and ~/.api-keys)

### Cross-Resort Validation
- 20 cost outlier warnings (pre-existing data quality, not from backfill)
- US resorts with implausibly low lift prices (Deer Valley $37, Copper $29, Smugglers $27)
- Austrian resorts with high prices (likely EUR stored as USD without conversion)
- Grade: D (43% completeness + 20 warnings) — will improve as pipeline enriches data

### New Work Items Identified
- Update TAVILY_API_KEY on Railway (local updated, Railway still has old expired key)
- Fix cost data outliers (currency confusion, stale prices)
- 9 resorts at 0% completeness need targeted research (Selva Val Gardena, Cortina, Stowe, Deer Valley, Hakuba, Winter Park, Smugglers Notch)

**Key commit:** ee6b3ec

**Arc:**
- Started believing: Schema markup and data backfill are separate concerns
- Ended believing: They're complementary — schema makes data discoverable, backfill makes the data worth discovering
- Transformation: From adding metadata about content to ensuring the content behind the metadata is substantive

---

## Round 14: SEO & Schema Critical Fixes + Bug Fixes (2026-01-30) ✅

**Goal:** Fix everything broken or hurting search/social presence

### Fixes Applied — DEPLOYED
1. **Duplicate title suffix** — Removed `| Snowthere` from page-level titles on /resorts, /guides, /resorts/[country] (layout.tsx template already appends it)
2. **Quiz page** — Created layout.tsx with proper metadata + Footer component
3. **Unified footer** — All pages now use shared Footer component (replaced inline footer on resorts/country pages)
4. **Newsletter link** — CTA now points to `/#newsletter` (was `/`)
5. **Kitzbühel 404** — Unicode slug normalization fix: added `decodeURIComponent(slug).normalize('NFC')` to getResort()
6. **Kitzbühel duplicate** — Deleted archived record (4ce9f3b3), updated published slug to ASCII `kitzbuhel`

### Already Clean (no changes needed)
- AggregateRating: Not present in current code
- FAQ schema: Already server-rendered in page.tsx
- BreadcrumbList: Already present in page.tsx
- OG images: Using hero images (no broken /og/ route)

### Migration 035
- Applied via Supabase SQL Editor: Delete archived Kitzbühel + update published slug to ASCII

**Key commits:** cf167cd, a6a6b37, 3ef05c9, 71d7369

**Arc:**
- Started believing: The audit would find many broken things to fix
- Ended believing: Most schema items were already correct; the real bugs were Unicode normalization and template duplication
- Transformation: From expecting widespread schema gaps to discovering the codebase was healthier than the audit suggested

---

## Data Quality & Scoring Overhaul (2026-01-29) ✅

**Goal:** Fix false scoring defaults, add data completeness tracking, conditional table rendering, and publication quality gates

### Scoring Fixes
- **3 false defaults fixed** in `scoring.py`: `has_childcare`, `has_magic_carpet`, `has_ski_school` no longer default to `true` when data is missing (were inflating scores)
- **Completeness multiplier** added to formula: resorts with < 50% data completeness get penalized proportionally
- New primitive: `calculate_data_completeness()` with `KEY_COMPLETENESS_FIELDS` checklist

### Database
- **Migration 033:** Added `data_completeness` DECIMAL(4,3) column to `resort_family_metrics` (default 0.0)

### Frontend
- **FamilyMetricsTable + CostTable unhidden** with conditional rendering — only shown when `data_completeness >= 0.3`
- Data completeness < 0.6 shows disclaimer: "Some data is pending verification"

### Pipeline
- `data_completeness` stored after data extraction stage
- **Tiered publication gate:** completeness < 0.3 → draft only, 0.3-0.6 → publish with caveat, >= 0.6 → full publish
- **Dynamic quality queue:** low-completeness resorts re-queued for data enrichment

### MCP Server
- 3 new tools: `calculate_data_completeness`, `recalculate_family_score`, `audit_data_quality`

### Agent
- FamilyValue agent: data completeness check added to approval criteria

### New Files
- `agents/scripts/audit_data_quality.py` — audit current data quality across all resorts
- `agents/scripts/backfill_data_quality.py` — backfill completeness scores and recalculate family scores
- `agents/scripts/validate_cross_resort.py` — cross-resort consistency validation
- `agents/shared/calibration/golden_resorts.json` — reference data for calibration

**Arc:**
- Started believing: Scores just need the right formula
- Ended believing: Scores need the right formula AND awareness of how complete the underlying data is
- Transformation: From trusting all data equally to gating outputs by data quality

---

## Round 13.2: Google Places API Fix (2026-01-29) ✅

**Goal:** Investigate and fix Google Places API 400 errors blocking UGC photos and entity resolution

### Investigation Findings
- **Root cause:** The Snowthere Google Cloud project had **zero Maps/Places APIs enabled** and the `GOOGLE_PLACES_API_KEY` on Railway pointed to a key that didn't exist on the project
- **Two code paths affected:**
  - `ugc_photos.py` — Uses legacy Places API (`maps.googleapis.com/maps/api/place/...`) for UGC photo fetching
  - `external_links.py` — Uses Places API (New) (`places.googleapis.com/v1/places:searchText`) for entity resolution
- **Code was graceful:** Both paths silently skip when no valid key is available (print warning, return None)
- **Railway had 3 different Google keys:** `GOOGLE_API_KEY` (Gemini, from Tom Global project), `GOOGLE_PLACES_API_KEY` (invalid key), and the auto-generated Maps Platform key

### Fixes Applied — DEPLOYED

1. **Enabled Places API (legacy)** on Snowthere Google Cloud project (`places-backend.googleapis.com`)
2. **Enabled Places API (New)** on Snowthere Google Cloud project (`places.googleapis.com`)
3. **Auto-generated API key:** Google created "Maps Platform API Key" with 32 API restrictions
4. **Updated Railway env var:** `GOOGLE_PLACES_API_KEY` changed from invalid key to correct Snowthere project key (`AIzaSyCGIoU3XO17vcRfhep6UzcRQ9rsUih4_38`)
5. **Deployed** Railway service with updated variable

### Discovery
- The Snowthere project had 22 enabled APIs but zero were Maps/Places related
- There are multiple Google Cloud projects (Snowthere, Tom Global, Cold Email, etc.) — keys from other projects don't work
- The API key auto-restriction to "32 APIs" means all Maps Platform APIs are allowed by default
- `GOOGLE_API_KEY` on Railway (`AIzaSyC8mfREzkQL4MPMJDMgXNVjlaMJ2y1fFHM`) is from the Tom Global project — used for Gemini, separate concern

### Pending
- Restrict the API key to only Places API + Places API (New) for security (currently allows all 32 Maps APIs)

**Arc:**
- Started believing: The 400 errors were from a code bug or API quota issue
- Ended believing: The API wasn't enabled on the project and the key was from a non-existent credential
- Transformation: From debugging code to auditing cloud project configuration — infrastructure correctness strikes again

---

## Round 13.1: Technical SEO Audit & Indexing (2026-01-29) ✅

**Goal:** Investigate GSC/Bing indexing gaps, fix canonical tags, configure IndexNow, request priority indexing

### Investigation Findings
- **Google Search Console:** 4 indexed, 39 not indexed (37 "Discovered - currently not indexed")
- **Bing:** 0 indexed, sitemap accepted, IndexNow receiving pings
- **Root causes:** 3 fixable issues + normal new-site patience (site is 11 days old)

### Fixes Applied — DEPLOYED

1. **Canonical tags on 8 pages:** Homepage, /resorts, /guides, /about, /methodology, /contact, /privacy, /terms — all now have explicit `alternates.canonical` and `openGraph.url` via Next.js Metadata API
2. **IndexNow verification file:** Created `apps/web/public/fecbf60e758044b59c0e84c674c47765.txt`
3. **INDEXNOW_KEY Railway env var:** Updated from `snowthere8f4a2b1c9e7d3f5a` to `fecbf60e758044b59c0e84c674c47765` (matching verification file)
4. **ISR revalidation bug fix:** `26db039` — fixed Jan 28 pipeline failure, added /resorts revalidation on publish

### Manual Actions Completed (via Playwright)
5. **GSC priority indexing:** Requested indexing for 7 pages: /resorts/united-states, /resorts/canada, /resorts/canada/lake-louise, /resorts/switzerland/zermatt, /resorts/austria, /resorts/france, /resorts/switzerland
6. **GSC quota hit** on /resorts/japan — retry needed tomorrow
7. **Bing www property:** Confirmed already exists (both non-www and www properties)
8. **GSC API verified:** Service account `snowthere-gsc@snowthere.iam.gserviceaccount.com` has Full permission, JSON key active (Jan 27), Search Console API enabled with 1 successful request

### Discovery
- `/resorts/canada` was "URL is unknown to Google" — country listing pages may not all be in sitemap
- `/resorts` and `/guides` were already indexed (green checkmarks)
- GSC daily quota limits indexing requests to ~10/day

**Key commits:** `36fc555`, `26db039`

**Arc:**
- Started believing: Pages aren't indexed because the site is too new — just wait
- Ended believing: 3 real technical issues were blocking indexing alongside normal new-site patience
- Transformation: From assuming patience to systematic audit revealing fixable infrastructure gaps hidden behind normal new-site behavior

---

## Round 13: Delightful, On-Brand, Image-Rich Guide Pages (2026-01-28) ✅

**Goal:** Guide page design overhaul, Nano Banana Pro image generation, exit intent popup redesign

### Design Overhaul — DEPLOYED
- **HTML bug fixes:** `dangerouslySetInnerHTML` + `sanitizeHtml()` for list descriptions and FAQ answers
- **White card containers:** Content wrapped in `bg-white rounded-3xl shadow-lg` on gradient background
- **Section emojis:** Contextual emoji mapping by section type and title keywords
- **List item styling:** Color-coded number badges (coral odd, teal even), hover effects
- **Comparison tables:** Coral/teal gradient headers, alternating row tints
- **Callout section type:** Tip/warning/celebration variants with Spielplatz colors
- **Exit intent popup:** Full Spielplatz redesign — Fraunces headline, Caveat accent, floating snowflakes, playful CTA

### Nano Banana Pro Image Integration — DEPLOYED
- **Primary model:** `google/nano-banana-pro` on Replicate ($0.15/image, 2K resolution)
- **4-tier fallback chain:** Nano Banana Pro (Replicate) → Nano Banana Pro (Glif) → Gemini → Flux Schnell
- **All 11 guide images generated:** 11/11 success via Nano Banana Pro, stored in Supabase Storage
- **Permanent hosting:** Images downloaded from Replicate and re-uploaded to Supabase Storage (Replicate URLs are temporary)
- **Pipeline integrated:** `guide_orchestrator.py` uses `generate_image_with_fallback()` which now defaults to Nano Banana Pro

### Frontend Design Skill — INSTALLED
- `.claude/skills/frontend-design/SKILL.md` — combines Spielplatz design system with Anthropic frontend-design skill
- Ensures all future page work follows brand palette, typography, emoji conventions, and component patterns

**Key commits:** `b34fc48`, `900f0f4`

**Arc:**
- Started believing: Guide pages just needed images and a few bug fixes
- Ended believing: Brand personality requires systematic design overhaul AND reliable image infrastructure
- Transformation: From patching individual issues to establishing Spielplatz as a living design standard with autonomous image generation

---

## Round 12: Content Expansion & SEO Critical Fixes (2026-01-28) ✅

**Goal:** Olympics guides, guides workflow overhaul, canonical URL fixes, indexing

### SEO Critical Fixes — DEPLOYED
**Root cause:** `NEXT_PUBLIC_SITE_URL` on Vercel had a trailing newline, breaking every canonical URL, og:url, and sitemap entry. Combined with www vs non-www mismatch and homepage `force-dynamic`.

**Fixes applied:**
1. Created `apps/web/lib/constants.ts` — centralized `SITE_URL` with `.trim()` safety net
2. Updated 7 files to import from `lib/constants.ts` (replaced scattered `BASE_URL` definitions)
3. Added `metadataBase` to `layout.tsx` using centralized `SITE_URL`
4. Deleted duplicate `app/robots.txt/route.ts` (comprehensive `robots.ts` now serves)
5. Changed homepage from `force-dynamic` to `revalidate = 3600` (ISR)
6. Added homepage revalidation to publishing pipeline (`revalidate_page("/")`)
7. Updated Vercel env var: `https://snowthere.com` → `https://www.snowthere.com`

**Post-deploy verification (all passed):**
- Canonical URLs: `https://www.snowthere.com/...` — no newline, correct www
- Sitemap: All URLs use www domain, no `%0A` encoding
- Homepage: `x-vercel-cache: HIT` (was `private, no-cache, no-store`)
- robots.txt: Comprehensive version with AI crawler rules

**Manual actions completed:**
- Google Search Console: Sitemap resubmitted (54 pages discovered, up from 43)
- Google Search Console: Homepage indexing requested (priority crawl queue)
- Bing Webmaster Tools: Sitemap resubmitted (processing)

### Olympics Guides — 6 PUBLISHED
- `cortina-skiing-2026-olympics` — Can You Ski in Cortina During the 2026 Olympics?
- `milan-cortina-2026-family-guide` — Complete Family Guide
- `dolomites-family-resorts-olympics` — Best Dolomites Family Resorts
- `milan-to-cortina-with-kids` — Transportation Guide
- `olympics-italy-family-itinerary` — 5-Day Itinerary
- `cortina-family-budget-guide` — Budget-Friendly Guide

### Guides Workflow Overhaul — 3 TRACKS
- **Track A (SEO/GEO):** Schema.org JSON-LD (Article + FAQPage + BreadcrumbList), full metadata with OpenGraph/Twitter/canonical, `generateStaticParams()` + ISR, guide llms.txt endpoints, guides in sitemap
- **Track B (Quality):** Generalized `expert_panel.py` review primitive, expert approval loop with iteration
- **Track C (UX):** Fixed resort links in guide content, related guides section, breadcrumb navigation

### Railway Crash Fixes
- Fix #1: Exa API `type: 'neural'` → `type: 'auto'` (breaking API change) + GSC dependencies
- Fix #2: NameError in runner.py (`quick_take_context` → `qt_context_result`)

**Key commits:** `a1ac49b`, `e51bcf0`, `9b001fb`, `21198f6`, `fec6c6b`, `2255a5b`

**Arc:**
- Started believing: SEO is about content and Schema.org markup
- Ended believing: A single trailing newline in an env var can block all indexing
- Transformation: Infrastructure correctness is the foundation of discoverability

---

## Round 11: Autonomous Content Systems (2026-01-27) ✅

**Goal:** Weekly newsletter + autonomous guide generation

- Newsletter system: Migration 031, `newsletter.py`, cron integration (Thursdays 6am PT)
- Guide generation pipeline: `guide_orchestrator.py`, 3-agent approval, Mon/Thu schedule
- Exit intent popup: `ExitIntentPopup.tsx`, 7-day cooldown
- Site cleanup: Removed AI disclosure, added /methodology to footer, fixed decimal display

**Arc:** Autonomous content is just primitives composed differently on a cron schedule

---

## Round 10: Content Structure & Email Fix (2026-01-27) ✅

**Goal:** Guide pages + fix email system

- Built `/guides/[slug]` page template with GuideContent, GuideHero components
- Created `lib/guides.ts` with fetching utilities
- Loaded HTML templates into `email_templates` table
- Welcome sequence now sends properly

**Arc:** The JSONB content schema was already designed — just needed frontend rendering

---

## Round 9: Scoring & Pipeline Stability (2026-01-27) ✅

**Goal:** Deterministic decimal scores + pipeline crash fixes

- **R9:** DECIMAL(3,1) scores, deterministic formula in `scoring.py`, /methodology page, quiz diversity
- **R9.1:** Pipeline crash fix (perfect_if/skip_if schema mismatch + unidecode slugify)
- **R9.2:** Integrated scoring into pipeline, backfilled 5 resorts, improved data extraction prompts

**Score distribution:** 5.4-7.8 (was clustered at 7-9 integers). Lake Louise highest at 7.8.

**Arc:** Store atoms, compute molecules — deterministic formulas from data beat LLM opinion

---

## Rounds 6-8: Summary

**Round 8 — Quick Takes & Site Audit** (2026-01-26)
- Editorial Verdict Model: hook/context/tension/verdict structure
- 31 forbidden phrases, specificity scoring, quality gates
- Created About/Contact pages, fixed quiz match percentages
- Email confirmation on signup via Resend

**Round 7 — External Linking & Affiliate** (2026-01-26-27)
- Entity link cache (Google Places), affiliate config, pipeline link injection (Stage 4.9)
- GA4 outbound click tracking, 30+ affiliate programs researched
- Migration 032 created (pending manual network signups)

**Round 6 — AI Discoverability & Email** (2026-01-26)
- AI crawler whitelist in robots.ts (GPTBot, Claude-Web, PerplexityBot, etc.)
- Full email system: 7 tables, Resend integration, 5-email welcome sequence
- CAN-SPAM compliance: unsubscribe endpoint, physical address, template variables
- Region extraction for location display

---

## Rounds 1-5: Foundation (Summary)

| Round | Name | Key Outcome |
|-------|------|-------------|
| 1 | Foundation | Next.js 14, Supabase, 23 tables, design system |
| 2 | Core Agents | 63 primitives, autonomous pipeline, MCP server |
| 3 | Security Audit | XSS, GDPR, legal pages, security headers |
| 4 | Production Launch | Vercel + Railway + Supabase in production |
| 5 | Compliance & Polish | Alerts, WCAG 2.1 AA, CWV, internal linking, site stabilization |
| 5.1 | Agent-Native Scalability | Two-phase validation, 99% token reduction |
| 5.2 | Schema Contract Audit | sanitize_for_schema(), expanded cost columns |

---

## Infrastructure

| Service | Details |
|---------|---------|
| **Vercel** | www.snowthere.com, ISR, SPIELPLATZ design system |
| **Railway** | snowthere-agents (creative-spontaneity), daily cron (resorts + guides + newsletter) |
| **Supabase** | Snowthere, AWS us-east-2, 30+ tables |
| **Google Search Console** | sc-domain:snowthere.com, sitemap: 54 pages, GSC API connected |
| **Bing Webmaster Tools** | snowthere.com + www.snowthere.com verified, sitemap submitted, IndexNow active |
| **Google Analytics** | GA4, linked to GSC |
| **Google Cloud** | Project "Snowthere", Search Console API + Places API + Places API (New) enabled, Maps Platform API Key + service account |
| **Resend** | Email delivery, domain verified (DKIM + SPF + MX) |
| **IndexNow** | Verification key `fecbf60e758044b59c0e84c674c47765`, Railway env var configured |

## Pipeline Status

- **Resorts:** ~6/day, entity linking (10-20 links/resort), 3-layer style editing on all content
- **Guides:** Mon/Thu, 3-agent approval panel, auto-publish, Nano Banana Pro featured images
- **Images:** Nano Banana Pro on Replicate (primary), 4-tier fallback, permanent Supabase Storage
- **Newsletter:** DISABLED (handed off to GTM team)
- **Email sequences:** 5-email welcome series (Day 0/2/4/7/14), still runs via Railway cron
- **Pricing:** Exa discovery + Haiku interpretation + country-specific validation
- **Calendar:** generate_ski_calendar() generates monthly snow/crowds/recommendation via Haiku (~$0.003/resort)
- **Style:** Deterministic pre-pass + Haiku em-dash replacement + Sonnet style edit on all sections
- **429 handling:** Rate-limit errors reset to "pending" (retry next day, not "rejected")

## Known Issues

- ~~Google Places API 400 errors (blocks UGC photos)~~ — **FIXED in R13.2** (APIs enabled, correct key deployed)
- ~~OG images return 404~~ — Resort pages now use hero images for OG (verified in code)
- ~~AggregateRating ratingCount: 1~~ — Removed in R14
- ~~FAQ schema client-rendered~~ — Server-side FAQPage JSON-LD added in R14 (already present in page.tsx)
- ~~BreadcrumbList missing on resort pages~~ — Added in R14 (already present in page.tsx)
- ~~Internal links open new tabs~~ — **FIXED** in sanitize.ts (internal links distinguished from external)
- ~~Entity links missing/broken~~ — **FIXED** in Linking Strategy Overhaul (371 links across 58 resorts, context-aware destinations)
- ~~sanitize.ts overwrites rel attributes~~ — **FIXED** with allowlist validation (noopener, noreferrer, nofollow, sponsored, ugc)
- ~~No UTMs on in-content links~~ — **FIXED** with utm_medium=in_content on entity links
- ~~Duplicate title suffix on index pages~~ — Fixed in R14 + Deep Audit
- ~~Quiz page missing footer~~ — Fixed in R14
- ~~Inconsistent footers~~ — Unified in R14
- ~~Kitzbühel 404~~ — Fixed in R14 (Unicode normalization + ASCII slug)
- ~~Calendar never generated~~ — **FIXED** in Deep Audit (new generate_ski_calendar() primitive, 495 entries backfilled)
- ~~Coordinates missing for new resorts~~ — **FIXED** in Deep Audit (extract_coordinates() in pipeline)
- ~~data_completeness always 0.0~~ — **FIXED** in Deep Audit (12 missing columns added to allowlist)
- ~~Pricing cache → resort_costs disconnect~~ — **FIXED** in Deep Audit (cache fallback + USD columns)
- ~~Content truncation undetected~~ — **FIXED** in Deep Audit (detection in runner.py)
- ~~Em-dashes in content~~ — **FIXED** with comprehensive 3-layer style primitive (R24) + deterministic pre-pass
- ~~LLM preamble phrases in content~~ — **FIXED** with 9-phrase strip in style pre-pass + voice profile
- ~~US resort pricing unrealistic~~ — **FIXED** in R24 (Exa discovery + country-specific validation)
- ~~AvantLink verification~~ — Removed (broken), keeping Pinterest only
- **MCP parity at ~40%** — 58 of ~340 primitive functions exposed; 22 modules missing → R17
- **Runner monolith** — `run_resort_pipeline()` is 1,627 lines, no partial re-run → R18
- ~~Quick Take length occasionally exceeds 120 word limit~~ — Reformatted to 50-90 word single paragraph (R20 initial, R21 voice rebalancing)
- ~~Quick Take score discrepancy~~ — Three-layer hybrid scoring replaces single-score model in R20
- Affiliate programs: 7 networks signed up (Feb 13-18), migration 032 pending apply, CSV at scratchpad/affiliate-programs.csv
- ~30 pages still "Discovered - currently not indexed" in GSC (normal for new site, will resolve over 2-6 weeks)
- Google Places API key is unrestricted (allows all 32 Maps APIs) — should restrict to Places only
- ~~Data quality backfill not yet run~~ — **DONE in R15** (33/38 updated, 43% avg completeness)
- ~~Cost data outliers~~ — Partially fixed in R24 (country-specific validation prevents impossible prices)
- TAVILY_API_KEY on Railway needs updating (local .env updated, Railway still has expired key)
- Migration 036 (`data_requests` table) not yet applied to cloud Supabase — GDPR form returns 500
- Bad Gastein still FAILED (429 rate limit) — needs re-run

## Planned Rounds (Ultimate Audit — 2026-01-29)

Rounds 14-16 are user/SEO/GEO-facing. Rounds 17-18 are agent infrastructure.

### ~~Round 14: SEO & Schema Critical Fixes + Bug Fixes~~ ✅

Completed 2026-01-30. See R14 section above.

### ~~Round 15: GEO & Rich Results Enhancement + Data Quality Backfill~~ ✅

Completed 2026-01-30. See R15 section above.

### ~~Round 16: Error Handling & Polish~~ ✅

Completed 2026-01-30. See R16 section above.

- [x] Add custom error boundaries (error.tsx, not-found.tsx)
- [x] Add loading states (loading.tsx for resorts, resort detail, guide pages)
- [x] Add resort filtering system (country/age/budget/search/sort with URL state)
- [x] Tighten CSP (HTTPS-only img-src, object-src none)
- [x] Add GDPR data request form + API route + migration 036
- [x] Comprehensive browser testing (15 categories, 3 walkthroughs)
- [ ] Apply migration 036 to cloud Supabase (blocked — needs manual SQL Editor apply)
- [ ] Restrict Google Places API key (deferred)

### Round 17: Agent-Native Parity

**Goal:** Close the MCP parity gap (currently 58 tools from ~8 modules; 22 modules unexposed)

- [ ] Expose intelligence/scoring/approval/quality/image/trail_map/quick_take/discovery/newsletter/guide/email/analytics/alerts/costs/links primitives as MCP tools
- [ ] Add pipeline trigger MCP tool
- [ ] Add agent memory access MCP tools
- [ ] Update AGENT_NATIVE.md

**Files:** `agents/mcp_server/server.py`, `AGENT_NATIVE.md`

### Round 18: Pipeline Architecture

**Goal:** Decompose runner monolith, improve resilience and observability

- [ ] Decompose `run_resort_pipeline()` into individually-invocable stages
- [ ] Wire AgentTracer into pipeline
- [ ] Deterministic error dispatch for known error classes
- [ ] Add max-retry depth counter
- [ ] Remove dead code
- [ ] Fix budget context mismatch
- [ ] Wire HookRegistry into production pipeline

**Files:** `agents/pipeline/runner.py`, `agents/pipeline/decision_maker.py`, `agents/agent_layer/tracer.py`, `agents/agent_layer/hooks.py`

---

## Discovered Work

Items found mid-session that don't belong to the current round. Parked here to prevent scope creep.

_(none)_

---

## Open Questions

Unresolved questions needing human input. Carried across sessions until answered.

_(none)_

---

## Session Decisions

Key decisions made during the current session with rationale. Resets each session.

_(no active session)_

---

## Session History

Log of all sessions in the current round. Carries across sessions, resets each round.

_(no active round)_

---

## Partial Completion Tracking

If interrupted mid-task, track progress here:

_(no active task)_

---

## Pending Manual Work

- ~~Commit type safety + security hardening fixes~~ → DONE (0c7121b)
- ~~Run backfills~~ → **DONE** (Feb 7): 247 links, 44 quick takes, 75 taglines, 75 hybrid scores
- ~~Pipeline bug fix~~ → **DONE** (f3e892c): datetime scope + check_budget signature
- ~~Coordinate + pricing backfill~~ → **DONE** (f51f23b): all 95 resorts
- ~~Calendar backfill~~ → **DONE** (8fda4f9): 495 entries across 99 resorts
- ~~GA4 custom events~~ → **DONE** (0a53767): quiz_complete + affiliate_click
- ~~Pinterest tracking pixel~~ → **DONE** (766656f): Tag ID 2613199211710
- Re-run Bad Gastein (`python3 cron.py --resort "Bad Gastein" --country "Austria"`)
- ~~Sign up for affiliate networks~~ — **DONE** (7 networks: Travelpayouts, Admitad, CJ, FlexOffers, AWIN, AvantLink, Impact)
- Run migration 032_comprehensive_affiliate_programs.sql on production
- Apply migration 036 to cloud Supabase (data_requests table for GDPR form)
- Request indexing for remaining GSC pages (daily quota, ~10/day)
- Monitor pipeline quality (guides Mon/Thu, welcome sequence daily)
- Homepage redesign (deferred from R14)
- Runner.py decomposition (R18 — 2,105 lines, only genuinely high-ROI refactor)
- Content strategy discussion
- Update TAVILY_API_KEY on Railway

## Key Files

| Category | Files |
|----------|-------|
| **Pipeline** | `agents/pipeline/runner.py`, `orchestrator.py`, `guide_orchestrator.py` |
| **Primitives** | `agents/shared/primitives/` (63+ atomic operations) |
| **Frontend** | `apps/web/app/resorts/[country]/[slug]/page.tsx`, `guides/[slug]/page.tsx` |
| **SEO** | `apps/web/lib/constants.ts`, `app/robots.ts`, `app/sitemap.xml/route.ts` |
| **IndexNow** | `apps/web/public/fecbf60e758044b59c0e84c674c47765.txt` |
| **Config** | `agents/shared/config.py`, `CLAUDE.md` |

## Recent Commits

```
d454caf feat: Voice evolution — personality-forward prompts, 6-criteria VoiceCoach, anti-hedging, Opus style edit
0a53767 feat: Add quiz_complete and affiliate_click GA4 custom events
550d1fa fix: Comprehensive em-dash/en-dash removal in deterministic pre-pass
8fda4f9 feat: Add ski quality calendar generation primitive + backfill all 99 resorts
eecdf0b fix: Add pricing cache fallback + USD column updates in pipeline
6ae9e51 fix: Add entity link guardrails to prevent nonsensical Maps links
6daf220 fix: Add Stubai Glacier to KNOWN_COORDINATES, backfill 4 new resort coords
dc71625 fix: Deep audit fixes — Opus 4.6, preamble stripping, data completeness, title dedup, coordinates
766656f feat: Add Pinterest tracking pixel (Tag ID 2613199211710)
504d7d0 feat: Add affiliate verification tags + fix SEO duplicate titles
f51f23b fix: Backfill coordinates + pricing for all 95 resorts
120610e feat: Style primitive, pricing redesign, snow chart, pipeline fixes (Round 24)
e1762c4 feat: Content refresh system + guide pipeline fixes (Round 23)
```
