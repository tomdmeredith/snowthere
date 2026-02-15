# Frontend Design Skill — Snowthere Spielplatz

> Combined Spielplatz design system + bold frontend design principles.
> Use this skill when building or modifying any user-facing page.

## Design Philosophy

**Core Principle:** A family ski directory should be FUN, not another boring database.

- Playful. Memorable. Fun.
- Excitement about planning (not overwhelm)
- Confidence that you can do this (not intimidation)
- Joy in browsing itself (not just the destination)
- Trust that we understand families

**Design Influences:** Memphis Design (geometric shapes, bold colors, playful chaos), trading card culture, playground aesthetics, Instagram lifestyle.

**NEVER use generic AI-generated aesthetics.** Every design choice must be intentional. If it looks like a template, try again.

## Color Palette

| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Coral | `#FF6B6B` | `coral-500` | Primary CTAs, highlights, energy |
| Teal | `#4ECDC4` | `teal-500` | Secondary, success, calm |
| Gold | `#FFE066` | `gold-300` | Accents, tips, celebration |
| Mint | `#95E1D3` | `mint-400` | Soft backgrounds, tertiary |
| Charcoal | `#2D3436` | `dark-800` | Text, dark elements |
| Cream | `#FFF5E6` | — | Warm backgrounds |

### Color Rules
- Coral for primary actions and "pay attention here"
- Teal for secondary actions and "this is good"
- Gold for tips, callouts, celebration
- Never use pure black (#000000), always charcoal
- Background gradients: cream to light pink to light blue

### Shadows (Color-Tinted)
```css
--shadow-coral: 0 4px 14px rgba(255, 107, 107, 0.25);
--shadow-teal: 0 4px 14px rgba(78, 205, 196, 0.25);
--shadow-gold: 0 4px 14px rgba(255, 224, 102, 0.25);
```

## Typography

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| Display | **Fraunces** | 700-900 | Headlines, section titles |
| Body | **Plus Jakarta Sans** | 400-600 | Body text, UI |
| Accent | **Caveat** | 400 | Handwritten touches, quotes |

### Rules
- Display font (`font-display`) for ALL section headers
- Never use generic system fonts in visible UI
- Mid-sentence **bolding** for scannable key info
- No em dashes or en dashes, use commas or "to"

## Spacing & Border Radius

- Cards: `rounded-3xl` (24px)
- Buttons: `rounded-full` (pill) or `rounded-2xl`
- Callouts: `rounded-2xl` (16px)
- Small elements: `rounded-xl` (12px)
- Section padding: `py-24` to `py-40`
- Card padding: `p-6` to `p-8`

## Interactive Effects

```css
/* Cards */
hover:scale-[1.02] hover:-translate-y-1 transition-all duration-300

/* Buttons */
hover:scale-105 active:scale-95

/* Playful hover */
hover:rotate-2

/* Bounce (emojis, decorative) */
animation: bounce-emoji 2s infinite;

/* Float (background shapes) */
animation: float 6s ease-in-out infinite;
```

## Emoji Usage

### When to Use
- Section headers (one emoji before text)
- Callout boxes (💡 PRO TIP, 🎉 KIDS SKI FREE)
- Navigation CTAs (Let's Go! 🎿)
- Age group selectors (👶 🧒 👧 🧑)

### Rules
- One emoji per section header, placed BEFORE text
- Emojis enhance meaning, never replace it
- Bouncing emojis for decorative/playful moments
- NEVER use emojis in body text paragraphs
- Keep emoji set consistent (family/winter/travel)

### Approved Emoji Set
```
Navigation: ❄️ 🎿
Sections: ✈️ 🏠 🎟️ ⛷️ ☕ 💬 📬
Callouts: 💡 🎉 ⚠️ 🌙 🎯
Guide types: ⛷️ (comparison) ✅ (how-to) 🗺️ (regional) 🎟️ (pass) 📅 (seasonal) 🎿 (gear)
Topics: 💰 (budget) ✈️ (travel) 🏠 (lodging) 👨‍👩‍👧‍👦 (family) ☕ (food) 📋 (checklist) 📊 (comparison) ❓ (faq)
```

## Component Patterns

### Cards
```html
<div class="bg-white rounded-3xl p-6 shadow-card hover:shadow-card-hover hover:-translate-y-1 hover:scale-[1.02] transition-all duration-300">
```

### Callout Boxes
```html
<!-- Pro Tip (gold) -->
<div class="bg-gold-100/50 border-2 border-gold-300 rounded-2xl p-5">
  <span class="font-display font-semibold text-gold-700">💡 PRO TIP</span>
  <p>...</p>
</div>

<!-- Warning (coral) -->
<div class="bg-coral-100/50 border-2 border-coral-300 rounded-2xl p-5">
  <span class="font-display font-semibold text-coral-700">⚠️ HEADS UP</span>
  <p>...</p>
</div>

<!-- Celebration (teal) -->
<div class="bg-teal-100/50 border-2 border-teal-300 rounded-2xl p-5">
  <span class="font-display font-semibold text-teal-700">🎉 GREAT NEWS</span>
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

### Buttons
```html
<!-- Primary CTA -->
<button class="bg-coral-500 hover:bg-coral-600 text-white px-8 py-4 rounded-full font-semibold shadow-coral hover:shadow-coral-lg hover:scale-105 transition-all">
  Let's Go! 🎿
</button>
```

### Tables
- Rounded container (`rounded-2xl overflow-hidden`)
- Coral/teal gradient header row
- Alternating cream row tints
- Bold first column

## Voice & Content

- **Encouraging:** "You can totally do this"
- **Practical:** Real info, not fluff
- **Honest:** "Real talk:" moments
- **Fun:** Light touch, occasional humor

### Banned Phrases
- "It's important to note that..."
- "In conclusion..."
- "Let's dive in..."
- "Whether you're a... or a..."
- Anything with em dashes

## Bold Aesthetic Execution

When designing pages:
1. **Typography is identity** — Fraunces display font for all headlines, Caveat for handwritten accents
2. **Color tells a story** — coral for energy/action, teal for calm/success, gold for delight
3. **Space is a feature** — generous whitespace, `py-24` minimum between sections
4. **Motion adds life** — spring animations, hover lifts, bouncing emojis
5. **Details matter** — color-tinted shadows, rounded-3xl corners, gradient backgrounds
6. **Content in containers** — white cards on warm gradient backgrounds, never text floating on gradient
