# Snowthere Design System: Spielplatz

> **Design Philosophy:** A family ski directory should be FUN, not another boring database.

---

## Brand Identity

**Name:** snowthere
**Logo:** ❄️ snow**there** (snowflake emoji + wordmark, "there" in coral)
**Tagline:** "The fun way to find your next family ski adventure"
**Voice:** Instagram mom friendly, practical, encouraging, never intimidating

---

## Design Philosophy

**Core Principle:** Playful. Memorable. Fun.

**The Feeling We Create:**
- Excitement about planning a ski trip (not overwhelm)
- Confidence that you can do this (not intimidation)
- Joy in the browsing experience itself (not just the destination)
- Trust that we understand families (not generic travel advice)

**Design Influences:**
- Memphis Design (geometric shapes, bold colors, playful chaos)
- Trading card culture (collectible feel, numbered items)
- Playground aesthetics (rounded, soft, colorful)
- Instagram lifestyle (aspirational but achievable)

---

## Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| **Coral** | `#FF6B6B` | Primary CTAs, highlights, energy, "there" in logo |
| **Teal** | `#4ECDC4` | Secondary, success, calm |
| **Yellow/Gold** | `#FFE066` | Accents, tips, celebration |
| **Mint** | `#95E1D3` | Soft backgrounds, tertiary |
| **Charcoal** | `#2D3436` | Text, dark elements, "snow" in logo |
| **Dark-800** | `#1E2324` | Headings, emphasis |
| **Cream** | `#FFF5E6` | Warm backgrounds |

### Color Usage Rules
- Coral for primary actions and "pay attention here"
- Teal for secondary actions and "this is good"
- Yellow for tips, callouts, and celebration moments
- Mint for soft backgrounds and tertiary elements
- Never use pure black (#000000), always charcoal
- Background gradients: cream to light pink to light blue

### Shadows (Color-Tinted)
```css
--shadow-coral: 0 4px 14px rgba(255, 107, 107, 0.25);
--shadow-teal: 0 4px 14px rgba(78, 205, 196, 0.25);
--shadow-gold: 0 4px 14px rgba(255, 224, 102, 0.25);
--shadow-base: 0 4px 16px rgba(45, 52, 54, 0.08);
```

---

## Typography

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| **Display** | Fraunces | 700-900 | Headlines, section titles |
| **Body** | Plus Jakarta Sans | 400-600 | Body text, UI |
| **Accent** | Caveat | 400 | Handwritten touches, quotes |

### Type Scale
- Hero: 6xl to 9xl (responsive)
- Section title: 3xl to 4xl
- Card title: xl to 2xl
- Body: base to lg
- Small: sm to xs

### Typography Rules
- Display font for all section headers
- Never use generic system fonts in visible UI
- Mid-sentence **bolding** for scannable key info
- No em dashes or en dashes, use commas or "to"

---

## Spacing & Layout

### Border Radius
- Cards: `rounded-3xl` (24px)
- Buttons: `rounded-full` (pill) or `rounded-2xl`
- Callouts: `rounded-2xl` (16px)
- Small elements: `rounded-xl` (12px)

### Spacing Scale
- Section padding: `py-24` to `py-40` (responsive)
- Card padding: `p-6` to `p-8`
- Gap between cards: `gap-6` to `gap-8`
- Container max-width: `max-w-7xl` (1280px)

---

## Interactive Elements

### Hover Effects
```css
/* Cards */
hover:scale-105 or hover:scale-[1.02]
hover:-translate-y-1 or hover:-translate-y-2
transition-all duration-300

/* Buttons */
hover:scale-110
hover:rotate-2 (playful)
active:scale-95

/* Links */
hover:underline
hover:text-coral-600
```

### Animations
```css
/* Bounce (for emojis, decorative elements) */
@keyframes bounce-emoji {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
animation: bounce-emoji 2s infinite;

/* Float (for background shapes) */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
animation: float 6s ease-in-out infinite;

/* Fade in up (for content on load) */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Timing Functions
```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
--ease-bounce-subtle: cubic-bezier(0.34, 1.56, 0.64, 1);
```

---

## Emoji Usage

### When to Use Emojis
- Section headers (✈️ Getting There, 🏠 Where to Stay)
- Callout boxes (💡 PRO TIP, 🎉 KIDS SKI FREE)
- Navigation CTA (Let's Go! 🎿)
- Logo (❄️ snowthere)
- Social proof and trust indicators
- Age group selectors (👶 🧒 👧 🧑)

### Emoji Rules
- One emoji per section header, placed before text
- Emojis should enhance meaning, not replace it
- Bouncing emojis for decorative/playful moments
- Never use emojis in body text paragraphs
- Keep emoji set consistent (family/winter/travel themed)

### Approved Emoji Set
```
Navigation: ❄️ 🎿
Ages: 👶 🧒 👧 🧑
Sections: ✈️ 🏠 🎟️ ⛷️ ☕ 💬 📬
Callouts: 💡 🎉 ⚠️ 🌙 🎯
Reactions: ❤️ ✨ 🚀
Social: 📸 🐦 📘
```

---

## Component Patterns

### Cards
- Always `rounded-3xl` (24px)
- Subtle border or shadow (not both heavy)
- Hover: scale + shadow increase
- Color-coded borders for categories

### Callout Boxes
- Background: 20% opacity of accent color
- Border: 2px solid accent color (optional)
- Icon + bold header + body text
- `rounded-2xl`

### Badges
- Pill shape (`rounded-full`)
- Small text (xs to sm)
- Solid background for emphasis
- Outlined for secondary

### Tables
- Rounded container
- Alternating row backgrounds (subtle)
- Bold headers
- Highlight important rows (coral/teal bg)

---

## Content Guidelines

### Voice Principles
1. **Encouraging:** "You can totally do this"
2. **Practical:** Real info, not fluff
3. **Honest:** "Real talk:" moments
4. **Fun:** Light touch, occasional humor
5. **Expert:** We've done the research

### Writing Rules
- No em dashes or en dashes
- Use "to" for ranges: "3 to 5 days" not "3-5 days"
- Mid-sentence **bolding** for key info
- Short paragraphs (3 to 4 sentences max)
- Bullet points for lists of 3+ items
- Active voice over passive

### Banned Phrases (LLM Giveaways)
- "It's important to note that..."
- "In conclusion..."
- "Let's dive in..."
- "Whether you're a... or a..."
- Anything with em dashes

---

## Section Header Pattern

All content sections should follow this pattern:

```
┌─────────────────────────────────────────────────────────────────────┐
│ ✈️ Getting There                    (emoji + display font)          │
│ ──────────────────────                                              │
│ [Content below with proper spacing and components]                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Resort Page Sections

Each section has its own component treatment:

| Section | Emoji | Border Color | Key Components |
|---------|-------|--------------|----------------|
| Getting There | ✈️ | Teal | AirportCard, ProTipCallout |
| Where to Stay | 🏠 | Mixed | LodgingTierCard (budget/mid/luxury) |
| Lift Tickets | 🎟️ | Coral | PricingTable, PassCard, KidsFreeCallout |
| On the Mountain | ⛷️ | Teal | TerrainBreakdown, SkiSchoolCard |
| Off the Mountain | ☕ | Gold | CategoryHeader, RestaurantCard |
| What Parents Say | 💬 | Coral | QuoteCard, LovesCard, HeadsUpCard |

---

## Trading Card Style (Homepage)

Resort cards on the homepage use a "trading card" aesthetic:

- Numbered badges (01, 02, 03, 04)
- Color-coded by position (coral, teal, gold, mint)
- Subtle rotation (`-4.5°`, `-1.5°`, `+1.5°`, `+4.5°`)
- Hover: scale 110%, reset rotation to 0°
- 4:3 aspect ratio images with zoom on hover
- Score bar with 5 segments

---

## Quick Reference: Tailwind Classes

### Buttons
```html
<!-- Primary CTA -->
<button class="bg-coral-500 hover:bg-coral-600 text-white px-8 py-4 rounded-full font-semibold shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all">
  Let's Go! 🎿
</button>

<!-- Secondary -->
<button class="border-2 border-teal-500 text-teal-600 px-6 py-3 rounded-full font-medium hover:bg-teal-50">
  Learn More
</button>
```

### Cards
```html
<div class="bg-white rounded-3xl p-6 shadow-card hover:shadow-card-hover hover:-translate-y-1 hover:scale-[1.02] transition-all duration-300">
  <!-- content -->
</div>
```

### Callouts
```html
<!-- Pro Tip (yellow) -->
<div class="bg-gold-100/50 border-2 border-gold-300 rounded-2xl p-5">
  <span class="font-semibold">💡 PRO TIP</span>
  <p>...</p>
</div>

<!-- Kids Free (coral) -->
<div class="bg-coral-100/50 border-2 border-coral-300 rounded-2xl p-5">
  <span class="font-semibold">🎉 KIDS SKI FREE</span>
  <p>...</p>
</div>
```

### Section Headers
```html
<h2 class="font-display text-3xl font-bold text-dark-800 flex items-center gap-3">
  <span>✈️</span>
  <span>Getting There</span>
</h2>
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `tailwind.config.ts` | All Spielplatz colors, shadows, animations |
| `globals.css` | CSS variables, component classes, keyframes |
| `layout.tsx` | Font loading (Fraunces, Plus Jakarta Sans, Caveat) |
| `DESIGN_SYSTEM.md` | This document (permanent reference) |
