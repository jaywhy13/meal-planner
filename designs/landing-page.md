# Landing Page — Section Spec

Companion document to [`landing-page.html`](landing-page.html). Captures the structure,
copy, and design decisions for the unauthenticated marketing page that converts
the choleric segment described in [`/product.md`](../product.md).

---

## Aesthetic direction

**Editorial cooking-journal meets warm software product page.** A sophisticated
cookbook publication aesthetic — generous typography, asymmetric layouts,
hand-drawn underline and arrow accents, food iconography sprinkled through —
brought to life with the in-app vibrant Tailwind-style palette so the page
feels energetic rather than sedated.

Three registers run through the page, mirroring the in-app design system in
[`product.md` §12](../product.md):

| Register | Where it lives on the landing page |
|---|---|
| **Power surface** | Section copy tone (confident, no fluff), data-dense product mockups, FAQ density |
| **Warm brand expression** | Cream background, hand-drawn accents, Fraunces italics, food doodles, character illustrations |
| **Kid cook mode preview** | The tablet showing kid cook mode in the hero, and the parent+kid illustration in the Saturday ritual |

### Type pairing

| Role | Font | Notes |
|---|---|---|
| Display | **Fraunces** (variable, opsz + SOFT axes) | Italics with `SOFT 100` are doing visual heavy lifting — used as "punctuation" |
| Body | **Plus Jakarta Sans** | Carried over from the in-app brand for consistency |
| Mono | **JetBrains Mono** | Used for eyebrows, numerals, fine editorial details |

### Color palette

Aligned with the in-app design tokens in [`overview.md`](overview.md) but warmed up with editorial cream surfaces.

| Token | Value | Role |
|---|---|---|
| `--cream` | `#FBF5E6` | Page background |
| `--cream-deep` | `#F4EBCD` | Recipes section background |
| `--cream-soft` | `#FEFAEE` | Card surfaces, Rituals + Pricing sections |
| `--ink` | `#1A1612` | Primary text, AI honesty section bg |
| `--forest` | `#22C55E` | Brand green (Tailwind green-500, in-app brand) |
| `--forest-deep` | `#16A34A` | Hover (green-600) |
| `--leaf` | `#4ADE80` | Lighter green (green-400) |
| `--mint` | `#DCFCE7` | Light tint (green-100) |
| `--tomato` | `#EF4444` | Editorial punctuation, accents (red-500) |
| `--mustard` | `#FBBF24` | Warm accent, sticky notes (yellow-400) |
| `--butter` | `#FEF3C7` | Soft tag bg (yellow-100) |
| `--pumpkin` | `#FB923C` | Warm splash, stool, sticky note (orange-400) |

---

## Sections, top to bottom

### 1. Nav

Sticky, transparent on top of the cream page, picks up a hairline border on scroll.

- **Brand:** logo mark (filled green circle with lowercase italic `m` glyph) + word mark "Meal Planner" in Fraunces medium
- **Links:** *How it works · Recipes · Pricing · FAQ*
- **Right-side:** *Sign in* link + green primary CTA *"Start free trial →"*

---

### 2. Hero

Asymmetric two-column layout. Generous vertical breathing room. Staggered entrance
animations: eyebrow → headline → lead → buttons → stats.

**Left column:**
- **Eyebrow:** `ISSUE 01 · THE WEEKLY MEAL PLAN, MADE BETTER`
- **Headline:** *"You've got a plan. Let's make it better."*
  - "Let's make it" is italicized in green
  - Hand-drawn yellow squiggle underline beneath it, animated with `stroke-dashoffset`
- **Lead:** *"Bring whatever you already use — Pinterest pins, a whiteboard, a spreadsheet,
  even just the rotation in your head. We turn it into a clean weekly plan, a smart
  shopping list, and a cook mode your kids can actually follow along with."*
- **Primary CTA:** *"Start your 7-day trial →"* (green-500 with glow shadow)
- **Microcopy:** *"No credit card needed."* in Fraunces italic
- **Hand-drawn red arrow** doodle pointing at the CTA (animated draw)
- **Stat strip** along the bottom, divided by a top border:
  - `10 min · Sunday planning`
  - `150+ · Tested recipes`
  - `0. · Ads, ever`

**Right column:**
- **Floating dashboard peek** (week strip) rotated -4°, behind and offset
- **Tablet** rotated 2.5° showing kid cook mode (step 3 of 7, "Crack two eggs into the bowl...")
- **Floating decorative doodles** arranged around the tablet:
  - Green herb sprig (top right, gently floating)
  - Red tomato (bottom left)
  - Fried egg (mid right)
  - Green music note (bottom right)
  - Three colored sparkles (yellow/orange/green at varying positions)
- All doodles animate with `float` and `twinkle` keyframes

---

### 3. Ticker

Dark band, full bleed, scrolling editorial taglines with mustard italic accents.

> *"Plan the week **in ten minutes** ✦ Cook with your kid **on a tablet** ✦ Bring your **own recipes** ✦ Shopping list, **shared with your partner** ✦ An honest AI that **explains itself** ✦"*

Continuous CSS scroll animation (36s loop, duplicated for seamless loop).

---

### 4. A few things we believe (principles section)

**Section heading:** *"A few things we believe."*

**Intro:** *"You're already doing the hard part — thinking about what your family eats every
week. These are the principles we built the rest around."*

**Hero illustration:** Full-width **planning-chaos scene** — parent figure leaning over a
laptop showing a spreadsheet, surrounded by yellow/orange/red sticky notes, a handwritten
paper meal list, a pinned Pinterest recipe card, and a coffee mug with steam. A question
mark and exclamation point hover above the scene as visual punctuation of the cognitive
load. Visually communicates *"we see the chaos; here's the principles for fixing it."*

**Six principle pillars** in a 3×2 grid with editorial dividers:

1. Sunday planning shouldn't take *ninety minutes*.
2. Your kids have opinions. The plan should *respect them*.
3. Cooking with kids should be *joyful*, not chaotic.
4. Your partner should be able to *follow the plan* without asking.
5. AI should *explain itself*, not assert things as fact.
6. The recipes you bring in are *yours*. Forever.

---

### 5. Three rituals

**Section heading:** *"Three moments we're trying to make better."*

**Intro:** *"We didn't invent a new system. We took the three meal-planning moments most
families already live through every week — and gave each one a home that's a little less
chaotic."*

Three alternating-direction blocks. Each has: a date/time eyebrow in tomato, a Fraunces
headline with green italic accent, a body paragraph, a meta divider line with the punchline.

#### 5a. Sunday · 06:00 PM

- **Headline:** *Plan the week in ten minutes.*
- **Body:** AI drafts from your existing recipes, you edit inline, shopping list falls out.
- **Punchline:** **90 min → 10 min**
- **Visual:** Mockup window of the weekly planner — 7-day grid, today highlighted in green,
  one cell empty/red showing "Add a meal," AI suggestion strip at the bottom

#### 5b. Weeknight · 05:15 PM

- **Headline:** *Tonight's dinner, ready when you are.*
- **Body:** One push at 5pm. Tonight's meal with kid acceptance predictions (always with
  reasoning). Two backup meals pre-loaded one tap away.
- **Punchline:** **Always recovers.** Never asserts.
- **Visual:** Mockup window of the "Tonight" card — meal title, cook time / serves / pantry
  status, per-kid prediction with pill labels, primary "Start cooking" / "Swap for backup" buttons

#### 5c. Saturday · 10:00 AM

- **Headline:** *Cook with your kid, hands-on.*
- **Body:** Big steps, simple words, the app reads each step aloud. Background music. Kid
  taps the giant next button.
- **Punchline:** **One-way audio.** The app talks, your kid doesn't.
- **Visual:** **Cooking scene illustration** — parent and kid at a counter, mixing bowl with
  batter and a wooden spoon, tablet propped showing cook mode (step 3 of 7), music notes
  drifting from the tablet, banana on the counter, steam rising, sparkles scattered

---

### 6. AI honesty

Dark inverted section. Single most counter-cultural moment on the page; every other
meal-app landing page hypes AI, this one *under-promises*.

**Section heading:** *"A few honest words about the AI."*

**Intro:** *"Recommender systems are wrong sometimes. Kids are chaos. We built this knowing
both — so what the AI does is bounded, explainable, and easy to recover from when it misses."*

Two-column "YES / NO" with editorial Fraunces italic headlines and bulleted lists.

**What it does** (in green-leaf):
- Drafts your week from your own recipes
- Scales portions and suggests substitutions
- Adapts recipes for kid-friendly cooking
- Learns each kid's likes, dislikes, and allergens
- Explains its reasoning, every time

**What it doesn't** (in tomato):
- Invent recipes from scratch. Every recipe is real and tested.
- Listen to your kids. Cook mode is one-way audio only.
- Store voice recordings. Of anyone, ever.
- Show ads. Not now, not in v2, not ever.
- Pretend to know your family better than you do.

---

### 7. Recipes

**Section heading:** *"Real recipes from real people."*

**Intro:** *"One hundred and fifty family-tested recipes at launch, plus every recipe you
bring in yourself. Every imported recipe credits the original creator — link, byline, the works."*

**Recipe shelf:** 5 recipe cards in a row, each with:
- CSS-only food gradient evocation as the card image (sweet potato, banana, pesto, taco, sesame chicken)
- Time/category tag pill in the top corner
- Recipe name in Fraunces with italic ingredient highlight
- Attribution byline: *"via [domain]"* with the domain underlined in forest green

**Blogger outreach CTA** beneath the shelf:
- *"Are you a food blogger?"* — primary CTA *"Get in touch →"*
- Establishes the community/content-partnership angle even on the marketing page

---

### 8. Privacy

Surfaces the privacy stance prominently because cholerics distrust apps that touch kids.

**Headline:** Huge typographic statement — *"Your kids. Your data."*

**Three "No" pillars** in a 3-column grid with vertical dividers:

| No · 01 | No · 02 | No · 03 |
|---|---|---|
| No *microphone* for kids in cook mode | No *voice recordings* stored | No *ads.* Not now, not later. |

Each pillar has a tomato `NO · NN` label, a Fraunces headline with italic accent, and a short
body paragraph explaining the commitment.

---

### 9. Pricing

Centered single card — no tiers, no asterisks. The simplicity is the message.

**Section heading:** *"One price. No asterisks."*

**Price card:**
- Eyebrow: `MEAL PLANNER · MONTHLY`
- **$5.99 / per month** (Fraunces 88px display)
- *"or $48/year — save 33%"* in mono
- Feature list with green checkmark accents:
  - Up to three eater profiles
  - Full recipe library plus your imports
  - Weekly planning and kid cook mode
  - Shopping list with shareable link
  - Cancel anytime, no questions asked
- **CTA:** *"Start your 7-day trial →"*
- Microcopy: *"No credit card required."*

The Family Plan tier (deferred to v2 per [`product.md` §15](../product.md)) is intentionally
hidden — surfacing it now would muddy the single-tier message.

---

### 10. FAQ

Editorial accordion for the deep-research choleric. Top item open by default. Five questions:

- What if I'm *already using Notion, Excel, or paper?*
- Will this work for my *really picky kid?*
- Can my *partner use it too?*
- Will this work for *kosher, halal, or cultural cooking?*
- What happens *after the 7-day trial?*

Answers are honest, no marketing fog. Each answer caps at ~3 sentences.

---

### 11. Closer

Forest green full-bleed section. Big italic headline, single CTA.

- **Headline:** *"Bring your plan in. Cook tonight."*
- **CTA:** *"Start your 7-day trial →"* (cream/white button on green)
- **Microcopy:** *"No credit card required — cancel anytime."*

The closer headline mirrors the wedge: "you already plan" + "value is immediate."

---

### 12. Footer

Dark, structured, no surprises.

- **Brand block:** Fraunces "Meal Planner." with italic period, plus a Fraunces-italic
  tagline.
- **Columns:** Product / Company / Legal
- **Meta row:** `© 2026 Meal Planner · Made for organized parents · Issue 01`

---

## Motion

### Entrance animations

- **Hero:** staggered fade-in on eyebrow (100ms), headline (250ms), lead (450ms),
  buttons (600ms), stats (750ms)
- **Hand-drawn underline:** `stroke-dashoffset` from 600 → 0 over 1.4s starting at 1.1s
- **Hand-drawn arrow:** same draw effect, 1.2s starting at 1.3s
- **Sections:** IntersectionObserver-triggered fade + 28px translate-up, rootMargin
  -60px for under-the-fold trigger
- **Doodles:** continuous `float` (6–8s) and `twinkle` (2.2–2.8s) keyframe loops

### Parallax

Subtle scroll-driven motion on stable elements (never on items with their own keyframe
animations, to avoid transform conflicts). 15 elements parallax-tagged via `data-parallax`:

| Element | Speed |
|---|---|
| `.hero-flourish` | 0.18 |
| `.tablet` | -0.05 (reverse) |
| `.dashboard-peek` | 0.08 |
| Sunday `.mockup` | 0.06 |
| Weeknight `.mockup` | 0.07 |
| `.chaos-illustration` | 0.04 |
| `.cooking-scene` | 0.05 |
| Recipe cards (each) | 0.04, -0.02, 0.06, -0.03, 0.05 (staggered) |
| `.privacy-headline` | 0.04 |
| `.closer-headline` | 0.05 |

Implementation: `requestAnimationFrame`-throttled scroll handler. Computes element offset
from viewport center, applies `translate3d(0, Ypx, 0)` plus preserved base rotation.
Respects `prefers-reduced-motion`. Skips elements still in their entrance reveal.

---

## Open questions / variants to consider

- **Real food photography on recipe cards.** Currently using CSS-only radial gradients
  to evoke food. Real photos (Unsplash or partner sourced) would lift the page significantly.
- **More illustrations.** Could add character illustrations to the Privacy section ("Your kids,
  your data" works with a family-at-table scene) and the Closer.
- **Comparison table** vs. Mealime / EatThisMuch / "your whiteboard" — omitted in v1, but
  could be a powerful insert before Pricing for the deep-research choleric.
- **Testimonial section** — once we have beta users, drop a 2–3 testimonial strip between
  Honesty and Recipes.
- **Hero variant:** the current asymmetric layout could be flipped (illustration left, text
  right) or centered with the illustration as a wide hero band beneath.
- **Sticky CTA** in the nav once user has scrolled past hero — currently the CTA is in nav
  but its prominence could change.

---

## File layout

```
designs/
  ├── landing-page.md          ← this document
  ├── landing-page.html        ← the implementation, self-contained
  ├── overview.md              ← in-app design system overview
  ├── 01-dashboard--empty-state.png
  ├── 01-dashboard--populated-state.png
  ├── 01-meal-plan-detail--card.png
  └── 02-meal-plan-detail--list.png
```

Open `landing-page.html` directly in a browser — no build step, no dependencies beyond
Google Fonts (Fraunces, Plus Jakarta Sans, JetBrains Mono).
