# Meal Planner — UI Redesign Plan

## Vision

A bold, light, airy, and energetic redesign for a family meal planning app used primarily by
parents (moms) for meal prepping for kids and families. The design should feel warm, appetizing,
and lively — not dull or clinical. Desktop-first, mobile-friendly.

**Inspired by:** mealime.com, eatthismuch.com

---

## Design Tokens

### Color Palette

| Token | Value | Use |
|---|---|---|
| `color/green-500` | `#22C55E` | Primary brand, buttons, active states |
| `color/green-600` | `#16A34A` | Button hover, darker accent |
| `color/green-100` | `#DCFCE7` | Active nav background, light tints |
| `color/green-50`  | `#F0FDF4` | Subtle background tints |
| `color/yellow-400`| `#FBBF24` | Warm accent, highlights |
| `color/yellow-100`| `#FEF3C7` | Tag backgrounds |
| `color/orange-400`| `#FB923C` | Warm splash accent |
| `color/white`     | `#FFFFFF` | Cards, sidebar background |
| `color/gray-50`   | `#F9FAFB` | App background |
| `color/gray-100`  | `#F3F4F6` | Inactive icon boxes |
| `color/gray-200`  | `#E5E7EB` | Borders, dividers |
| `color/gray-400`  | `#9CA3AF` | Muted / hint text |
| `color/gray-600`  | `#4B5563` | Secondary text |
| `color/gray-900`  | `#111827` | Primary text, headings |

#### Semantic aliases
| Token | Maps to |
|---|---|
| `semantic/bg-app` | `#F9FAF7` (slightly warm off-white) |
| `semantic/bg-sidebar` | `color/white` |
| `semantic/bg-card` | `color/white` |
| `semantic/text-primary` | `color/gray-900` |
| `semantic/text-secondary` | `color/gray-600` |
| `semantic/text-muted` | `color/gray-400` |
| `semantic/border-default` | `color/gray-200` |
| `semantic/accent-primary` | `color/green-500` |

### Typography

**Font:** Plus Jakarta Sans (all weights)

| Role | Weight | Size | Use |
|---|---|---|---|
| Display | ExtraBold | 30–36px | Page titles |
| Heading 1 | ExtraBold | 22–26px | Card titles, empty state headline |
| Heading 2 | Bold | 18–20px | Section headings |
| Body Large | Medium | 15–16px | Primary body text |
| Body | Regular | 14px | Standard body, nav labels |
| Caption | Regular | 12–13px | Hints, tips, metadata |
| Label | SemiBold | 10px + 8% letter-spacing | Section labels (ALL CAPS) |

### Spacing

`4 / 8 / 12 / 16 / 20 / 24 / 32 / 48`

### Border Radius

| Token | Value | Use |
|---|---|---|
| `radius/8`   | 8px | Icon boxes, small chips |
| `radius/12`  | 12px | Buttons, small cards |
| `radius/16`  | 16px | Medium cards |
| `radius/24`  | 24px | Large cards, panels |
| `radius/full`| 9999px | Pills, avatars |

### Shadows

- **Button glow:** `0 6px 16px rgba(34,197,94,0.35)` — used on primary green buttons
- **Card lift:** `0 4px 24px rgba(17,24,39,0.06)` — used on white cards
- **Empty state CTA:** `0 8px 20px rgba(34,197,94,0.4)`

---

## Layout

### Shell

- **Canvas:** 1440×900 desktop frame
- **Layout:** Horizontal split — fixed sidebar + fluid content area
- **Sidebar width:** 240px (fixed)
- **Content area:** fills remaining width (1200px)

### Sidebar

```
┌────────────────────────┐
│  🥗  Meal Planner      │  ← Logo (green icon + ExtraBold app name)
├────────────────────────┤
│  MAIN MENU             │  ← Muted caps label
│                        │
│  📅  Meal Plans  ←active│  ← Green bg tint + green icon box + green label
│  🥦  Foods             │  ← Gray icon box + gray label
│  ⚙️  Meal Settings     │
│                        │
│         (spacer)       │
├────────────────────────┤
│  ● Sarah M.            │  ← Avatar + name + "Family meal planner"
│    Family meal planner │
└────────────────────────┘
```

**Active nav item treatment:**
- Background: `green-100`
- Icon box: filled `green-500`
- Label: `green-600` SemiBold

**Inactive nav item treatment:**
- Background: transparent (hover: `gray-50`)
- Icon box: filled `gray-100`
- Label: `gray-600` Medium

---

## Screens to Design

### 1. Meal Plans — Empty State ✅ (in progress in Figma)

The most important screen. Must feel inviting and delightful, not like an error state.

**Layout (inside white card, centered):**
1. Large green circle icon with 🍽️ emoji (100px, drop shadow glow)
2. Colorful food category chips in a row: 🥗 Salads · 🍳 Breakfast · 🍝 Dinners · 🥤 Smoothies
3. Headline: **"Your meal planning adventure starts here!"** (ExtraBold 26px, centered)
4. Body: friendly copy explaining what to do (Regular 15px, centered, gray-500)
5. Large green CTA button: `+ Create My First Meal Plan` (glow shadow)
6. Tip text: `✨ Tip: You can plan up to 7 days at once…` (muted, 12px)

---

### 2. Meal Plans — Populated State (TODO)

Large cards in a responsive grid (2–3 per row at 1440px).

**Meal Plan Card anatomy:**
```
┌──────────────────────────────┐
│  [Colorful gradient header   │  ← Random warm gradient per card
│   with week range & emoji]   │     (green/yellow/orange tones)
├──────────────────────────────┤
│  Week of Apr 14 – Apr 20     │  ← SemiBold 16px
│  🍽️ 7 days · 21 meals        │  ← Muted caption
│                              │
│  [Meal type chips: 🥣 🍽️ 🥗] │  ← Small pill tags
│                              │
│  [Progress bar / coverage]   │  ← How complete the week is
│                              │
│  [View →]  [Edit ✏️]         │  ← Action buttons
└──────────────────────────────┘
```

Card states:
- **Default:** white bg, subtle shadow
- **Hover:** shadow lifts, slight scale (1.02)
- **Active/current week:** green left border accent

---

### 3. Foods Management (TODO)

Grid/list of foods with:
- Search bar at top (rounded, with 🔍 icon)
- Filter chips: All · Proteins · Vegetables · Grains · Fruits · Dairy
- Food cards: emoji/icon + name + macro info + add button

---

### 4. Meal Plan Detail (TODO)

Weekly calendar view:
- Day columns (Mon–Sun) across the top
- Meal type rows (Breakfast / Lunch / Dinner / Snack)
- Each cell: meal card with food name, emoji, calories
- "Add meal" cells: dashed border, `+` icon, hover green fill

---

## Interactions & Micro-animations

### Save Button — Pac-Man Eating Animation
When a save/submit button is clicked:
1. Button disables immediately
2. Button label fades out
3. A Pac-Man character appears, eating small food dots (●●●) moving left to right
4. On success: Pac-Man finishes, button turns green with a checkmark ✓
5. On error: button pulses red, label returns with error message

*Annotate in Figma with a multi-frame component showing the states.*

### Add Food / Create Meal Plan — Drop-in Success Alert
When a food or meal plan is successfully added:
1. A toast/modal slides down from the top-center of the screen
2. Inside: a food icon (e.g., 🍗) drops into a pot/bowl icon with a bounce animation
3. Message: `"Chicken added to your foods!"` with a green checkmark badge
4. Auto-dismisses after 3s, or user can click ✕

*Annotate in Figma showing the keyframes: icon falling → landing in bowl → bounce settle.*

---

## Figma File

**File:** Meal Planner — UI Redesign
**URL:** https://www.figma.com/design/BtGWahc9aN1XkhxnhKLLYu

### Pages planned
- `Meal Plans — List` (in progress)
- `Meal Plans — Populated` (TODO)
- `Meal Plan Detail` (TODO)
- `Foods Management` (TODO)
- `Components & Tokens` (TODO)
- `Interaction Annotations` (TODO)

---

## Open Questions / Next Iterations

- [ ] Confirm card gradient direction and colors with user
- [ ] Decide on icon style: emoji-based vs. custom SVG icons
- [ ] Mobile breakpoint layout for sidebar (drawer/hamburger vs. bottom nav)
- [ ] Confirm whether nutritional info (calories/macros) should be prominent on cards
- [ ] Logo refinement: bowl+leaf SVG vs. emoji placeholder

---

## Session Notes (added 2026-04-16)

### Screens Completed in Penpot

All four screens below live in the same Penpot file, laid out side-by-side on the canvas (1520px apart horizontally):

| Screen | Penpot Frame ID | Canvas position |
|---|---|---|
| Meal Plans — Empty State | `59defdbc-d725-8095-8007-e18ec818d2a8` | x=0, y=0 |
| Meal Plans — Populated State | `59defdbc-d725-8095-8007-e190b416474f` | x=1520, y=0 |
| Meal Plan Detail — Grid View | `59defdbc-d725-8095-8007-e19283114be8` | x=3040, y=0 |
| Meal Plan Detail — List View | `59defdbc-d725-8095-8007-e195cfb1c87c` | x=4560, y=0 |

### Design Decisions Made

- **Emoji icons confirmed** — all nav items, food pills, and meal type indicators use emojis (not custom SVGs)
- **Meal Plan card names** — use real names ("Family Meal Plan", "Kadie's Weekly Plan", "Quick & Easy Plan") instead of date ranges in the card title
- **Single "View →" button per card** — removed Edit button to keep cards clean
- **List view approach** — hybrid list/calendar: large date number + day name, color-coded food pills per meal type, week groupings with vertical week-range label on the left
- **Food pill colors** — yellow (#FEF3C7) = Breakfast, green (#DCFCE7) = Lunch, purple (#EDE9FE) = Dinner, pink (#FCE7F3) = Snack
- **Today row highlight** — green left border stroke + green bg (#F0FDF4) + green date number
- **No drop shadows on week cards** — Penpot renders drop shadows against the bounding box rectangle, not the rounded corners, producing an ugly rectangular halo. Shadows removed entirely for a cleaner look.
- **View toggle** — Grid / List toggle lives in the page header next to the plan title

### Known Penpot Limitations

- Drop shadows do **not** follow rounded corners — they render on the bounding box. Avoid shadows on rounded cards.
- `penpot.library.local.tokens` API (`addSet`) is non-functional — use hardcoded hex values throughout.
- `penpot.createText()` requires a string argument; returns null otherwise.
- `text.align` is the correct property (not `text.textAlign`).
- After calling `shape.resize()`, `growType` resets to `"fixed"` — reset explicitly if auto-sizing is needed.

### Next Screen to Build

**Foods Management** (see Section 3 in this file):
- Search bar at top (rounded, 🔍 icon)
- Filter chips: All · Proteins · Vegetables · Grains · Fruits · Dairy
- Food cards: emoji + name + macro info (calories, protein, carbs, fat) + add button
- Suggested canvas position: x=6080, y=0

### Remaining Screens (after Foods Management)

- **Meal Settings** — not yet specced, needs design discussion
- **Components & Tokens page** — document reusable Penpot components once screens are stable
- **Interaction Annotations page** — Pac-Man save animation, drop-in success toast (see design.md for specs)
