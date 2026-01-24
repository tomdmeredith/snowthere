# Resort Page Comprehensive Audit - Round 5.8

**Date:** 2026-01-23
**Audited Pages:** Park City, St. Anton, Zermatt
**Auditor:** Claude Code

---

## Executive Summary

Three resort pages were audited for visual quality, data completeness, technical correctness, and design consistency. **Zermatt emerged as the best example**, with a real hero photo and complete data. Park City and St. Anton have significant data gaps that impact user experience.

**Key Findings:**
- 2 of 3 pages have placeholder images instead of real photos
- All 3 pages have missing cost data (all "—" values)
- Country landing pages return 404 errors (broken breadcrumb links)
- St. Anton is missing family metrics entirely (no score displayed in hero)
- Trail map data quality varies significantly

---

## Issue List

### Critical Issues (Block Publishing)

| # | Issue | Affected | Details |
|---|-------|----------|---------|
| C1 | **No hero image** | Park City, St. Anton | Gray placeholder with mountain icon instead of real resort photo. Zermatt has a real image - this proves the system works. |
| C2 | **Country pages 404** | All | Breadcrumb links to `/resorts/united-states`, `/resorts/austria`, `/resorts/switzerland` all return 404 RSC errors. |
| C3 | **Missing family metrics** | St. Anton | No Family Score badge in hero, no ages badge. The `family_metrics` data is missing or incomplete. |

### Major Issues (Impact User Experience)

| # | Issue | Affected | Details |
|---|-------|----------|---------|
| M1 | **Cost data all empty** | All | Cost breakdown sidebar shows "—" for all prices (adult/child lift tickets, budget/mid/luxury lodging). Content mentions prices but structured data is missing. |
| M2 | **Trail map data quality** | St. Anton | Shows only 13 runs, 7 lifts (Ski Arlberg has 305km/~300 runs). "Partial Data" badge is honest but data is unusable. 92% "Family Terrain" contradicts content saying it's expert-oriented. |
| M3 | **Family metrics gaps** | Park City, Zermatt | Missing values: Kid-Friendly Terrain %, Kids Ski Free info, Magic Carpet presence. Shows "—" in table. |
| M4 | **Ski Calendar missing** | All | No Ski Quality Calendar visible on any page despite component existing. |

### Minor Issues (Polish)

| # | Issue | Affected | Details |
|---|-------|----------|---------|
| m1 | **Social links use emoji** | All | Footer social icons (Instagram, Twitter, Facebook) use emoji (📸🐦📘) instead of proper icons. |
| m2 | **Similar Resorts missing** | All | No "Similar Resorts" section visible despite code support and `resort_similarities` table. |
| m3 | **Terrain Breakdown missing** | All | TerrainBreakdown visual component not rendering despite data existing in trail_map_data. |
| m4 | **Newsletter CTA non-functional** | All | "Get the Checklist" button has no onClick handler, just a `<button>`. |

---

## Comparative Analysis

| Feature | Park City | St. Anton | Zermatt |
|---------|:---------:|:---------:|:-------:|
| **Hero Photo** | Placeholder | Placeholder | Real photo |
| **Family Score Badge** | 8/10 | Missing | 8/10 |
| **Ages Badge** | 3-16 | Missing | 3-16 |
| **Quick Take** | Excellent | Good | Excellent |
| **Getting There** | Complete | Complete | Complete |
| **Where to Stay** | Complete | Complete | Complete |
| **Lift Tickets** | Complete | Complete | Complete |
| **On the Mountain** | Complete | Complete | Complete |
| **Trail Map Quality** | Full (1077 runs) | Partial (13 runs) | Full (290 runs) |
| **Off the Mountain** | Complete | Complete | Complete |
| **What Parents Say** | Complete | Complete | Complete |
| **FAQ** | 6 questions | 6 questions | 6 questions |
| **Cost Data** | All "—" | All "—" | All "—" |
| **Family Metrics Table** | Partial | Missing entirely | Partial |
| **Sidebar Score Card** | Present | Present | Present |
| **Mobile Responsive** | Good | Good | Good |

### Content Quality Scores (1-10)

| Dimension | Park City | St. Anton | Zermatt |
|-----------|:---------:|:---------:|:-------:|
| Voice Consistency | 9 | 8 | 9 |
| Factual Accuracy | 9 | 8 | 9 |
| Actionable Info | 9 | 8 | 9 |
| Parent-Focused | 9 | 7 | 9 |
| **Overall** | **9** | **7.75** | **9** |

---

## Technical Findings

### Console Errors
- `[404] /resorts/united-states?_rsc=...` - RSC prefetch fails for country pages
- `[404] /resorts/austria?_rsc=...` - Same issue
- `[404] /resorts/switzerland?_rsc=...` - Same issue

### Schema.org Markup
- SkiResort schema present and well-structured
- `aggregateRating` included when family_overall_score exists
- `amenityFeature` correctly lists childcare, ski school, magic carpet
- FAQPage schema in FAQSection component

### SEO
- Title tags optimized with resort name + "Family Ski Guide"
- Meta descriptions pull from quick_take content
- Canonical URLs properly set
- OG tags present with image references

### Mobile Responsiveness
- Hamburger menu works correctly at 375px
- Hero stacks properly on mobile
- Sidebar moves below main content on mobile
- Breadcrumbs wrap appropriately

---

## Root Cause Analysis

### Why are images missing?
The `resort_images` table stores hero images, but Park City and St. Anton don't have rows with `image_type = 'hero'`. The pipeline likely failed to fetch/store images for these resorts.

**Evidence:** Zermatt has a real photo, proving the system works when data exists.

### Why is cost data empty?
The `resort_costs` table likely has NULL values for structured pricing. The content sections mention prices in prose, but the structured `costs` object (used by CostTable) is empty.

### Why is St. Anton missing metrics?
The `resort_family_metrics` table either has no row for St. Anton, or the `family_overall_score` is NULL. The hero badge logic checks `metrics && metrics.family_overall_score`.

### Why do country pages 404?
The breadcrumb links to `/resorts/[country]` but there's no dynamic route at that path - only `/resorts/[country]/[slug]` exists for individual resorts.

---

## Perfect Resort Page Checklist

### Must Have (Critical - Blocks Publishing)

- [ ] **Hero image present** - Real resort photo, not placeholder
- [ ] **Family Score displayed** - In hero badges AND sidebar card
- [ ] **Age range displayed** - "Ages X-Y" badge in hero
- [ ] **All 13 content sections present:**
  - [ ] Quick Take with Perfect if/Skip if
  - [ ] Getting There
  - [ ] Where to Stay
  - [ ] Lift Tickets & Passes
  - [ ] On the Mountain
  - [ ] Trail Map
  - [ ] Off the Mountain
  - [ ] What Parents Say
  - [ ] FAQ (5-8 questions)
- [ ] **No console errors** - Especially no 404s
- [ ] **Valid Schema.org markup** - SkiResort + FAQPage
- [ ] **Trail map data quality** - "Full Coverage" badge, accurate run counts

### Should Have (Important - Impacts Quality)

- [ ] **Family metrics table complete** - All 8 rows populated, no "—"
- [ ] **Cost breakdown populated** - Lift ticket and lodging prices
- [ ] **Ski quality calendar** - All 12 months with conditions
- [ ] **Ski passes linked** - Pass badges with working URLs
- [ ] **Tagline present** - Handwritten-style subtitle
- [ ] **Perfect if/Skip if cards** - Visual summary cards
- [ ] **Pro Tips in content** - Yellow callout boxes

### Nice to Have (Polish)

- [ ] **Similar Resorts section** - 4-6 related resorts
- [ ] **Terrain breakdown visual** - Pie chart of difficulty
- [ ] **Useful links** - Official site, trail map, etc.
- [ ] **Atmosphere image** - Secondary resort image
- [ ] **Print-friendly layout** - Content works when printed

### Design Excellence (Aspirational)

- [ ] **Real UGC photos** - Multiple user photos in gallery
- [ ] **Video embed** - Resort intro video
- [ ] **Interactive calendar** - Clickable months with details
- [ ] **Price comparison** - vs nearby resorts
- [ ] **Booking integration** - Direct links to book lodging

---

## Recommendations (Prioritized)

### Immediate (This Sprint)

1. **Fix country pages** - Either create `/resorts/[country]/page.tsx` or update breadcrumbs to not link to non-existent pages
2. **Populate St. Anton family metrics** - Re-run pipeline or manual data entry
3. **Add hero images** - Run UGC photo fetch for Park City and St. Anton

### Near-Term (Next Sprint)

4. **Fix trail map data** - St. Anton shows wrong data; verify OpenSkiMap integration
5. **Populate cost tables** - Extract structured pricing from content or research
6. **Add Ski Calendar data** - Monthly conditions for all resorts

### Future

7. **Replace social emoji with icons** - Use Lucide icons for social links
8. **Implement newsletter signup** - Connect CTA button to API
9. **Add Similar Resorts** - Populate `resort_similarities` table

---

## Verification Commands

```bash
# Check for resorts missing hero images
SELECT r.name, r.country, ri.image_type
FROM resorts r
LEFT JOIN resort_images ri ON r.id = ri.resort_id AND ri.image_type = 'hero'
WHERE r.status = 'published' AND ri.id IS NULL;

# Check for resorts missing family metrics
SELECT r.name, r.country, rfm.family_overall_score
FROM resorts r
LEFT JOIN resort_family_metrics rfm ON r.id = rfm.resort_id
WHERE r.status = 'published' AND rfm.family_overall_score IS NULL;

# Check for resorts missing cost data
SELECT r.name, r.country, rc.lift_adult_daily
FROM resorts r
LEFT JOIN resort_costs rc ON r.id = rc.resort_id
WHERE r.status = 'published' AND rc.lift_adult_daily IS NULL;
```

---

## Files Referenced

| File | Purpose |
|------|---------|
| `apps/web/app/resorts/[country]/[slug]/page.tsx` | Main resort page |
| `apps/web/components/resort/*.tsx` | 24 resort components |
| `supabase/migrations/001_initial.sql` | Database schema |

---

## Screenshots

Saved in `.playwright-mcp/audit/`:
- `park-city-viewport.png` - Desktop hero
- `park-city-mobile.png` - Mobile hero
- `st-anton-viewport.png` - Desktop hero (missing badges)
- `zermatt-viewport.png` - Desktop hero (with real photo)
- `zermatt-mobile.png` - Mobile hero

---

**Audit Complete** - Round 5.8
