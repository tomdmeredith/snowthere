# Snowthere Design System

## Design Philosophy: "Alpine Golden Hour"

The aesthetic of **sunset on snow** - when the mountains turn golden pink and you're cozy inside the lodge with hot chocolate. This is the moment families remember: kids exhausted and happy, hot chocolate in hand, the adventure done but the glow remaining.

### Core Insight
Skiing imagery is typically cold (blue, white, harsh). We counter that with *warmth*:
- The emotional warmth of family adventure
- The visual warmth of alpenglow and lodge fires
- The confidence warmth of a helpful friend

### Design Principles

1. **Warm Over Cold** - Every color choice, texture, and element should feel inviting, not intimidating
2. **Confident Simplicity** - Clear hierarchy that builds confidence, not overwhelming data dumps
3. **Playful Sophistication** - Fun without being childish (Anthropologie, not Party City)
4. **Earned Trust** - Visual elements that signal expertise without pretension
5. **Adventure is Achievable** - Design that says "you can do this" not "this is hard"

---

## Color Palette

### Primary Colors

```css
:root {
  /* Alpine Cream - Primary background, warm not clinical */
  --cream-50: #FFFDF8;
  --cream-100: #FFF9ED;
  --cream-200: #FFF3DC;
  --cream-300: #FFECC8;

  /* Alpenglow - The hero color, sunset on snow */
  --glow-50: #FFF5F2;
  --glow-100: #FFE8E1;
  --glow-200: #FFD4C7;
  --glow-300: #FFB8A3;
  --glow-400: #FF9678;
  --glow-500: #FF7A5C;  /* Primary accent */
  --glow-600: #E8624A;
  --glow-700: #C44A36;

  /* Forest Lodge - Deep, grounding, trustworthy */
  --forest-50: #F2F7F5;
  --forest-100: #E0EDE8;
  --forest-200: #B8D4CA;
  --forest-300: #89B8A8;
  --forest-400: #5C9A86;
  --forest-500: #3D7D68;  /* Secondary accent */
  --forest-600: #2F6353;
  --forest-700: #264D42;
  --forest-800: #1E3D35;
  --forest-900: #162D28;

  /* Powder Slate - For text and contrast */
  --slate-50: #F8FAFB;
  --slate-100: #EEF2F4;
  --slate-200: #D9E2E7;
  --slate-300: #B8C9D1;
  --slate-400: #8FA5B2;
  --slate-500: #6A8494;
  --slate-600: #526875;
  --slate-700: #45535D;
  --slate-800: #3A454D;
  --slate-900: #2A3238;

  /* Golden Hour - Warm accents, optimism */
  --gold-50: #FFFCF0;
  --gold-100: #FFF7D6;
  --gold-200: #FFECAD;
  --gold-300: #FFDF7A;
  --gold-400: #FFD047;
  --gold-500: #F5BC24;
  --gold-600: #D99E12;
  --gold-700: #B47D0F;
}
```

### Semantic Colors

```css
:root {
  /* Backgrounds */
  --bg-primary: var(--cream-50);
  --bg-secondary: var(--cream-100);
  --bg-card: #FFFFFF;
  --bg-accent: var(--glow-50);
  --bg-dark: var(--forest-900);

  /* Text */
  --text-primary: var(--slate-900);
  --text-secondary: var(--slate-600);
  --text-muted: var(--slate-500);
  --text-inverse: var(--cream-50);

  /* Interactive */
  --interactive-primary: var(--glow-500);
  --interactive-primary-hover: var(--glow-600);
  --interactive-secondary: var(--forest-500);
  --interactive-secondary-hover: var(--forest-600);

  /* Feedback */
  --success: var(--forest-500);
  --warning: var(--gold-500);
  --info: var(--slate-500);
}
```

### Usage Guidelines

- **Primary backgrounds**: Always warm cream, never pure white
- **Hero accent**: Alpenglow (coral/peach) for CTAs, badges, highlights
- **Trust signals**: Forest green for "verified", "family approved", scores
- **Text**: Warm slate, never pure black
- **Gold**: Sparingly for "best value", "top pick" highlights

---

## Typography

### Font Stack

```css
:root {
  /* Display - For headlines, warmth + personality */
  --font-display: 'Fraunces', Georgia, serif;

  /* Body - Readable, friendly, modern */
  --font-body: 'DM Sans', -apple-system, sans-serif;

  /* Accent - For callouts, quotes, personality moments */
  --font-accent: 'Caveat', cursive;
}
```

### Why These Fonts

**Fraunces** - A "soft serif" with optical sizing and warmth. It has a slight playfulness in its curves that feels friendly without being childish. The variable font allows us to dial in exactly the right weight and optical size.

**DM Sans** - Clean, geometric, highly readable. Warmer than Inter, more personality than system fonts. Great x-height for mobile reading.

**Caveat** - Handwritten feel for "Pro tip:" callouts and personal touches. Makes it feel like notes from a friend.

### Type Scale

```css
:root {
  --text-xs: 0.75rem;     /* 12px - captions, metadata */
  --text-sm: 0.875rem;    /* 14px - secondary text */
  --text-base: 1rem;      /* 16px - body text */
  --text-lg: 1.125rem;    /* 18px - lead text */
  --text-xl: 1.25rem;     /* 20px - small headings */
  --text-2xl: 1.5rem;     /* 24px - section headings */
  --text-3xl: 1.875rem;   /* 30px - page headings */
  --text-4xl: 2.25rem;    /* 36px - hero headings */
  --text-5xl: 3rem;       /* 48px - display */
  --text-6xl: 3.75rem;    /* 60px - large display */
}
```

### Type Styles

```css
/* Display Heading - Resort names, page titles */
.heading-display {
  font-family: var(--font-display);
  font-weight: 600;
  font-optical-sizing: auto;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

/* Section Heading */
.heading-section {
  font-family: var(--font-display);
  font-weight: 500;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

/* Body Text */
.body-text {
  font-family: var(--font-body);
  font-weight: 400;
  line-height: 1.7;
  letter-spacing: 0.01em;
}

/* Handwritten Callout */
.callout-handwritten {
  font-family: var(--font-accent);
  font-size: 1.25em;
  line-height: 1.4;
}
```

---

## Spacing System

Based on 4px grid with comfortable, breathable layouts.

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
  --space-24: 6rem;     /* 96px */
}
```

### Spacing Guidelines

- **Generous padding**: Cards and sections should breathe (24-32px internal padding)
- **Comfortable gaps**: 24-48px between major sections
- **Mobile-first**: Reduce by ~25% on mobile
- **Asymmetric layouts**: Use offset spacing for visual interest

---

## Border Radius

Soft, organic, approachable - no sharp corners.

```css
:root {
  --radius-sm: 0.5rem;    /* 8px - buttons, badges */
  --radius-md: 0.75rem;   /* 12px - inputs, small cards */
  --radius-lg: 1rem;      /* 16px - cards */
  --radius-xl: 1.5rem;    /* 24px - large cards, modals */
  --radius-2xl: 2rem;     /* 32px - hero sections */
  --radius-full: 9999px;  /* Pills */
}
```

---

## Shadows

Soft, warm shadows that add depth without harshness.

```css
:root {
  /* Subtle lift */
  --shadow-sm:
    0 1px 2px rgba(42, 50, 56, 0.04),
    0 2px 4px rgba(42, 50, 56, 0.04);

  /* Card elevation */
  --shadow-md:
    0 4px 6px rgba(42, 50, 56, 0.04),
    0 8px 16px rgba(42, 50, 56, 0.06);

  /* Prominent elevation */
  --shadow-lg:
    0 8px 16px rgba(42, 50, 56, 0.06),
    0 16px 32px rgba(42, 50, 56, 0.08);

  /* Floating elements */
  --shadow-xl:
    0 16px 32px rgba(42, 50, 56, 0.08),
    0 32px 64px rgba(42, 50, 56, 0.12);

  /* Glow effect for CTAs */
  --shadow-glow:
    0 4px 14px rgba(255, 122, 92, 0.3);
}
```

---

## Components

### Cards

```css
.card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-md);
  border: 1px solid rgba(42, 50, 56, 0.06);
}

.card-warm {
  background: linear-gradient(
    135deg,
    var(--cream-50) 0%,
    var(--glow-50) 100%
  );
}

.card-featured {
  border: 2px solid var(--glow-200);
  position: relative;
}

.card-featured::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(
    135deg,
    rgba(255, 122, 92, 0.05) 0%,
    transparent 50%
  );
  pointer-events: none;
}
```

### Buttons

```css
/* Primary - Alpenglow gradient */
.btn-primary {
  background: linear-gradient(
    135deg,
    var(--glow-500) 0%,
    var(--glow-600) 100%
  );
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-full);
  font-family: var(--font-body);
  font-weight: 600;
  box-shadow: var(--shadow-glow);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow:
    var(--shadow-glow),
    0 8px 20px rgba(255, 122, 92, 0.25);
}

/* Secondary - Forest outline */
.btn-secondary {
  background: transparent;
  color: var(--forest-600);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-full);
  border: 2px solid var(--forest-300);
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--forest-50);
  border-color: var(--forest-400);
}

/* Ghost - Subtle */
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.btn-ghost:hover {
  background: var(--cream-100);
  color: var(--text-primary);
}
```

### Badges

```css
/* Family Score Badge */
.badge-score {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--forest-100);
  color: var(--forest-700);
  border-radius: var(--radius-full);
  font-weight: 600;
  font-size: var(--text-sm);
}

.badge-score.high {
  background: linear-gradient(
    135deg,
    var(--forest-100) 0%,
    var(--forest-200) 100%
  );
}

/* Category Badge */
.badge-category {
  padding: var(--space-1) var(--space-3);
  background: var(--cream-200);
  color: var(--slate-700);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Highlight Badge */
.badge-highlight {
  padding: var(--space-2) var(--space-3);
  background: var(--glow-100);
  color: var(--glow-700);
  border-radius: var(--radius-full);
  font-weight: 600;
}
```

### Tables (GEO-optimized)

```css
.data-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.data-table th {
  background: var(--forest-800);
  color: var(--cream-50);
  padding: var(--space-4);
  font-weight: 600;
  text-align: left;
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  padding: var(--space-4);
  border-bottom: 1px solid var(--cream-200);
  color: var(--text-primary);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover td {
  background: var(--cream-50);
}

/* Highlight important cells */
.data-table .highlight {
  color: var(--glow-600);
  font-weight: 600;
}
```

---

## Special Elements

### Quick Take Card (Hero component)

The "Quick Take" is the first thing families see - it must build confidence immediately.

```css
.quick-take {
  background: linear-gradient(
    135deg,
    var(--forest-800) 0%,
    var(--forest-900) 100%
  );
  color: var(--cream-50);
  border-radius: var(--radius-2xl);
  padding: var(--space-8);
  position: relative;
  overflow: hidden;
}

.quick-take::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 60%;
  height: 200%;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 122, 92, 0.15) 0%,
    transparent 70%
  );
  pointer-events: none;
}

.quick-take-score {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.quick-take-verdict {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  line-height: 1.4;
  margin: var(--space-6) 0;
}
```

### Perfect If / Skip If Lists

```css
.condition-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.condition-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
}

.condition-item.perfect {
  background: var(--forest-50);
  border-left: 3px solid var(--forest-500);
}

.condition-item.skip {
  background: var(--glow-50);
  border-left: 3px solid var(--glow-500);
}

.condition-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}
```

### Pro Tip Callout

```css
.pro-tip {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--gold-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--gold-200);
}

.pro-tip-label {
  font-family: var(--font-accent);
  color: var(--gold-700);
  font-size: var(--text-xl);
  white-space: nowrap;
}

.pro-tip-content {
  color: var(--slate-700);
}
```

### Ski Calendar (Monthly view)

```css
.ski-calendar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}

@media (max-width: 768px) {
  .ski-calendar {
    grid-template-columns: repeat(2, 1fr);
  }
}

.calendar-month {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  text-align: center;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.calendar-month:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.calendar-month.recommended {
  border-color: var(--forest-300);
  background: var(--forest-50);
}

.calendar-month.best {
  border-color: var(--glow-400);
  background: linear-gradient(
    135deg,
    var(--glow-50) 0%,
    var(--gold-50) 100%
  );
}

.month-name {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.month-indicator {
  display: flex;
  justify-content: center;
  gap: var(--space-1);
}

.snow-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--slate-300);
}

.snow-dot.filled {
  background: var(--glow-500);
}
```

---

## Animation & Motion

### Principles

1. **Purposeful** - Every animation should guide attention or provide feedback
2. **Quick** - 150-300ms for UI transitions
3. **Smooth** - Use cubic-bezier easing, never linear
4. **Restrained** - One hero animation per page load, subtle micro-interactions elsewhere

### Timing Functions

```css
:root {
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Standard Transitions

```css
/* Hover states */
.interactive {
  transition: all 0.2s var(--ease-out);
}

/* Card hover lift */
.card-lift:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

/* Button press */
.btn:active {
  transform: scale(0.98);
}
```

### Page Load Stagger

```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeInUp 0.5s var(--ease-out) forwards;
  opacity: 0;
}

.animate-in:nth-child(1) { animation-delay: 0ms; }
.animate-in:nth-child(2) { animation-delay: 75ms; }
.animate-in:nth-child(3) { animation-delay: 150ms; }
.animate-in:nth-child(4) { animation-delay: 225ms; }
```

---

## Iconography

### Style Guidelines

- **Line weight**: 1.5px stroke
- **Corner radius**: Rounded caps and joins
- **Size**: 24x24 default, 20x20 small, 32x32 large
- **Color**: Inherit from text color

### Custom Icons Needed

1. **Mountain peaks** - Logo element
2. **Ski lift** - Getting there
3. **Snowflake** - Conditions
4. **Family/kids** - Family-friendly indicator
5. **Piggy bank** - Budget indicator
6. **Calendar** - Best times
7. **Checkmark in circle** - Perfect if
8. **X in circle** - Skip if
9. **Lightbulb** - Pro tips
10. **Star** - Ratings

---

## Layout Patterns

### Resort Card (Browse page)

```
┌────────────────────────────────────────┐
│  ┌──────────────────────────────────┐  │
│  │         Resort Image             │  │
│  │    (16:9, rounded corners)       │  │
│  │                                  │  │
│  │  [Score Badge]                   │  │
│  └──────────────────────────────────┘  │
│                                        │
│  Region, Country                       │
│  Resort Name                           │
│  [Best for ages X-X] [Pass badges]     │
│                                        │
│  Quick verdict in one line...          │
│                                        │
│  [View Guide →]                        │
└────────────────────────────────────────┘
```

### Resort Page Layout

```
┌──────────────────────────────────────────────────────────┐
│ Breadcrumb: Home / Resorts / Country / Resort            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Region, Country                                         │
│  RESORT NAME                                             │
│  [Score: 8/10]  Best for ages 5-12                       │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────┐  ┌───────────────┐  │
│  │                                 │  │               │  │
│  │  Main Content (2/3)             │  │  Sidebar      │  │
│  │                                 │  │  (1/3)        │  │
│  │  - Quick Take                   │  │               │  │
│  │  - The Numbers table            │  │  Cost Card    │  │
│  │  - Getting There                │  │               │  │
│  │  - Where to Stay                │  │  Jump Links   │  │
│  │  - Lift Tickets                 │  │               │  │
│  │  - On the Mountain              │  │  Newsletter   │  │
│  │  - Off the Mountain             │  │  CTA          │  │
│  │  - Calendar                     │  │               │  │
│  │  - Parent Reviews               │  │               │  │
│  │  - FAQ                          │  │               │  │
│  │                                 │  │               │  │
│  └─────────────────────────────────┘  └───────────────┘  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  Similar Resorts                                         │
│  [Card] [Card] [Card]                                    │
└──────────────────────────────────────────────────────────┘
```

---

## Responsive Breakpoints

```css
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}
```

### Mobile-First Guidelines

- Default styles for mobile (320-640px)
- Stack layouts, full-width cards
- Larger touch targets (44px minimum)
- Reduce decorative elements
- Maintain generous padding

---

## Brand Voice in Design

The design should reflect the "Instagram mom" voice:

| Voice Trait | Design Expression |
|-------------|-------------------|
| Encouraging | Warm colors, friendly rounded shapes |
| Practical | Clear information hierarchy, scannable tables |
| Relatable | Handwritten accents, casual photography |
| Honest | Clear "Skip if" sections, real cost data |
| Expert | Professional layout, trust signals |

---

## Implementation Notes

### CSS Variables Setup (Tailwind)

Extend tailwind.config.ts with these custom values. Create CSS custom properties in globals.css.

### Font Loading

Use `next/font` for Fraunces and DM Sans. Load Caveat from Google Fonts for accent use only.

### Priority Components

1. Quick Take card
2. Family metrics table
3. Ski calendar
4. Resort browse card
5. Buttons and badges

---

*This design system captures the "Alpine Golden Hour" aesthetic - warm, confident, sophisticated but accessible. Every element should make overwhelmed parents feel: "I can do this."*
