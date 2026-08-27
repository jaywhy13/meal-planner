# Meal Planner — Product Overview

> A meal-planning companion for organized parents of young kids, where artificial intelligence
> upgrades their existing planning system rather than replacing it, and a tablet-friendly cook
> mode turns weekend dinners into bonding time with the kids.

---

## 1. Vision

The category-defining meal-planning app for **organized parents of young children (ages 3–8)** who
already plan their meals — in Excel, on a whiteboard, in a Notes app, or in their head — and want
a single trusted system that absorbs what they already do, learns their kids deeply, and turns
weekly meal orchestration into a 10-minute ritual instead of a 90-minute Sunday chore.

The app is not a chaos saver, not a "let us decide what you eat" service, and not a generic family
recipe library. It is **a power tool for a parent who already takes meal planning seriously**, and
a **delightful tablet companion** when that parent cooks with their kid on a Saturday morning.

---

## 2. Target user

### Primary segment (the only segment v1 markets to)

**The organized parent of one or two kids aged 3–8** who:

- Already plans meals weekly using some artifact — spreadsheet, paper list, Notes, mental model
- Is the household's primary meal lead (cognitive load of "what are we eating this week")
- Has a partner who follows the plan but doesn't own it
- Treats meal planning as a real job worth doing well, not a chore to outsource
- Is decisive, results-oriented, and impatient with friction
- Will pay $5.99/month if the product saves 60+ minutes a week and improves what they're already doing
- Cooks with their kid occasionally on weekends and wants those moments to be easier and more fun

This is a sharp psychographic narrowing — sometimes labelled "choleric" in the four-temperaments
typology. It is deliberate. The product copy, design density, and feature priorities all assume
this user.

### Secondary considerations (planned for, not marketed to)

- Single-parent households (data model supports)
- Caregiver execution (nanny, grandparent, au pair cooks tonight's meal via a share-link)
- Dietary-restricted adult eaters (gluten-free spouse, low-carb partner)
- Travel-frequent partners (per-meal eater attendance toggle)

### Out of scope for v1

- Parents of infants under 12 months (different product — allergen schedules, purees, choking
  hazards). Solid Starts owns this category.
- Households whose primary pain is "I don't plan at all" (chaos-stressed beginners). The
  artifact-import onboarding does not work for them; they need a different product.
- Co-parents alternating across two households (real pain, beautiful problem, deferred to a future
  phase to avoid diluting the primary wedge).

---

## 3. The hook and the trust model

### The hook

Two moments, sharpened over the course of the week:

1. **Sunday weekly planning becomes a 10-minute ritual.** The parent opens the app, the app
   knows the household, the AI drafts a week from their preferences and pantry, the parent edits
   inline, the shopping list falls out the other side. This is the primary acquisition driver and
   the moment the choleric segment converts.

2. **Saturday cook mode with the kid becomes effortless.** A recipe the kid likes, a tablet on
   the counter, large kid-readable steps, the app reads the step out loud, soft background music.
   Kid taps "next" when they're done. Parent and kid cook together without the parent shouldering
   the whole cognitive load. This is the differentiator that no competitor offers.

The Tuesday-5pm pre-dinner pivot (the original "firefighting" use case) is a *supporting* flow,
not the hook. It's high-value but lower-frequency than the weekly loop.

### The trust model

**The promise is "always recovers," not "always nails it."**

The app does not over-promise on prediction. Recommender systems are wrong sometimes, kids are
chaos, and trust extends slowly and revokes instantly. Three principles bake this into the
product:

1. **Safe meals are first-class.** Every suggestion ships with two backup options from the
   household's explicit safe-meals registry, one tap away. Failure is normalized into the UI.

2. **Suggestions are always explained, never asserted.** Never "Maya will love this." Instead:
   "Suggesting tonight because Maya rated last Friday's similar dish 5⭐ and you have chicken."
   When the user can see the reasoning, a wrong suggestion feels like a smart guess, not a
   failure.

3. **Cold start is a feature, not a hidden state.** The first-week onboarding *is* the bonding
   moment. The app earns the right to know the family; it does not pretend to know them on day 1.

---

## 4. The narrative spine of a week

The app is built around three moments per week. The home screen, the notification strategy, and
the navigation all serve these moments first.

### Sunday evening — weekly planning (primary)

- **Trigger:** Push notification at the household's chosen Sunday time (default: 6pm). User may
  also open proactively.
- **Home screen:** A "This Week" view. Big primary card prompts the weekly draft. Strip of last
  week's hits surfaces what the kids actually liked.
- **Flow:** Tap to draft → AI proposes a week (drawn from curated library + imported recipes,
  scoped to household preferences and pantry) → parent edits inline → confirms → shopping list
  generated automatically and grouped by aisle.
- **Time budget:** 10 minutes for an experienced user.

### Tuesday 5:15pm — pre-dinner pivot (supporting)

- **Trigger:** Push notification one hour before the household's usual dinner time (learned over
  the first weeks of use).
- **Home screen:** "Tonight" view. Card shows tonight's planned dinner with kid acceptance
  prediction (with reasoning visible). Two primary actions: start cooking, or swap.
- **Flow:** Either tap to cook (entering recipe mode, optionally kid cook mode) — or swap for a
  pre-loaded backup matched to current pantry and time available.

### Saturday morning — cook with the kid (delight)

- **Trigger:** Usually pull (parent opens the app deliberately). Optional configurable nudge if
  the household hasn't cooked together in a while.
- **Home screen:** Browse personal recipes, "stuff Maya loves," or the curated library. Tap a
  recipe → tap "Cook with [Kid]."
- **Cook mode (tablet, landscape):** Kid mode activates. Big illustration. Step language tuned for
  the kid's age. App reads the step aloud (text-to-speech, one-way — kid does not speak to the
  app). Kid taps a giant next arrow to advance. Spotify plays softly when the assistant isn't
  speaking.

### Push notification policy

- **Sunday weekly-planning push: on by default.** This is the engagement loop.
- **Tuesday dinner pre-empt and Saturday cook nudge: opt-in.** Default off to respect
  notification-fatigued parents; opt-in inside settings.
- **All notification times configurable.**

---

## 5. Onboarding — the choleric conversion moment

The first 5 minutes determine whether a choleric parent commits. They will not start from scratch.
They already have an artifact — a spreadsheet, a whiteboard, a list, a confident mental rotation
of 12 dinners. The onboarding **respects and absorbs that artifact, then asks for follow-up
detail**.

### The onboarding flow

1. **"What does your current plan look like?"** — pick an input method:
   - Photo of a whiteboard, paper list, or handwritten plan (optical character recognition + AI
     structure extraction)
   - Paste from a doc, spreadsheet, or Notes
   - URL list of recipes the parent cooks regularly (bulk URL ingestion)
   - Manual "list my 10 go-to dinners"

2. **AI structures the input.** Recipes are matched against the curated library where possible,
   and new ones are imported (URL-scraped with attribution to the source website). Ingredients
   are normalized. Cuisine and dietary tags are inferred.

3. **"Tell us about the eaters."** Names, ages, allergens, top dislikes, cultural/dietary context
   (kosher, halal, vegetarian, Caribbean, South Asian — anything that helps the AI infer at scale).
   Optional but encouraged.

4. **"Here's your week, drafted from what you already cook."** Editable. Confirm.

5. **Shopping list generated.** First week of value delivered before the user has spent more than
   a few minutes.

Traditional "answer 20 questions about your kids" onboarding does not work for this segment —
it feels like work without payoff. The artifact-first approach **gives value first** and earns
the right to ask follow-up questions later.

---

## 6. Data model

```
Account (1)  ←  the primary planner (the choleric parent), owns authentication
   │
   └── Household (1)
          │
          ├── Eaters (1..N)   ← profiles, NOT accounts
          │     - Maya (kid, age 5, no onions, hates mushy textures)
          │     - Jordan (kid, age 7, peanut allergy, loves spice)
          │     - Dad (adult, low-carb)
          │     - Mom (the planner, also an eater)
          │
          ├── Recipe Library
          │     - Curated recipes (shared across all households)
          │     - Imported recipes (private to this household, attributed to source)
          │
          ├── Plans (weekly, with per-meal eater attendance)
          ├── Pantry (lightweight inventory)
          ├── Shopping Lists (generated from plans minus pantry)
          └── Safe Meals Registry (per-eater fallback set)
```

### Why no second adult login in v1

Cholerics own the planning. Their partner needs to *follow* the plan, not co-create it. Sharing
artifacts (shopping list, weekly plan, single recipe) via share-link covers 95% of the partner
collaboration need. A second adult login becomes a v2+ premium feature.

---

## 7. Recipe sourcing

Two sources only. **No AI-generated recipes from scratch.**

| Source | Role | Why |
|---|---|---|
| **Curated library** | Foundation, ~150 recipes at launch | Quality floor — every recipe tested, accurate nutrition, accurate cooking time. Non-negotiable for a product parents trust to feed kids. |
| **User-imported** | Personal cookbook | URL paste in v1; Chrome extension in v2. Each imported recipe attributes the source website prominently. |

### AI's role with recipes

AI **modifies** existing recipes; it never generates them from scratch. Specifically:

- **Scale** (double, halve, "I'm cooking for 5 tonight")
- **Substitute** ("no yogurt — what works?")
- **Kid-friendlify** (per-recipe toggle: simplifies steps, adapts language, adjusts seasoning)
- **Cultural / dietary adaptation** (deferred to v1.5: "make this kosher," "Caribbean protein
  swap")

This bounds hallucination risk (a critical concern when feeding kids), keeps inference costs
predictable, and gives the curated library a sustainable quality floor.

### Recipe attribution

Imported recipes credit the source website prominently — link, byline, "via [domain]." This is
both legally correct and a deliberate community-building lever: food bloggers should *want* their
recipes featured to a paying parent audience.

---

## 8. Artificial intelligence scope

What AI does in this product:

| Capability | Phase | Why it matters |
|---|---|---|
| Conversational weekly planning | v1 | Replaces the "filter chips and forms" pattern of competitors. Natural language fits cholerics. |
| Recipe selection from library | v1 | Cheap inference, high frequency. The everyday workhorse. |
| Recipe modification (scale, substitute, kid-friendlify) | v1 | The core AI value proposition. Bounded, predictable, safe. |
| Text-to-speech narration in cook mode | v1 | Brings the cook-with-kid moment to life. One-way only — no kid voice input. |
| Pattern detection insights ("Maya rejected anything green for 3 weeks") | v1.5 | Requires ~6 weeks of usage data to be valuable. Ship the data collection in v1; surface insights in v1.5. |
| Multi-kid optimization (one meal, both kids satisfied) | v1.5 | High-value differentiator, complex prompt engineering, depends on having 2 kids in the profile. |
| Pantry vision (photo your fridge, AI extracts) | v1.5 | High computer-vision build cost; v1 pantry uses photo + shopping confirmation + recipe decrement. |
| Cultural / dietary adaptation | v1.5 | Valuable, deferrable — manual ingredient substitution covers most cases in v1. |
| Age-adapted instructions per kid | v1.5 | v1 cook mode is one register; per-age adaptation is a polish. |

**What AI does NOT do in this product:**

- It does not generate recipes from scratch.
- It does not listen to children (no microphone input in kid cook mode).
- It does not store voice recordings of kids ever.
- It does not assert preferences as fact ("Maya will love this") — it explains its reasoning.

---

## 9. Pantry — the keystone, kept light

The whole weekly loop is gated on pantry awareness. Without pantry, you can't omit owned items
from the shopping list, can't suggest recipes that fit what's there, can't do mid-week pivots.
But every meal-planning app that asks users to manually maintain an inventory dies, because the
data goes stale in three days.

**The model: three layered inputs, no manual taps.**

1. **Pantry-by-photo on demand.** Snap fridge and pantry occasionally. AI extracts what's there.
   Takes 30 seconds, runs before Sunday planning. v1 is light — photos when the user feels like
   it, no nag.
2. **Pantry-by-shopping-list.** When the user confirms a shopping trip ("got everything"), those
   items become pantry items automatically. Free signal.
3. **Pantry-by-recipe-decrement.** When the user marks a meal cooked, the recipe's ingredients
   are subtracted from pantry. Approximate but good enough.

Net result: pantry stays usefully fresh with **one ~30-second photo every now and then** and zero
per-item taps.

---

## 10. Shopping list

A first-class output of the weekly plan, not an afterthought.

### v1

- Auto-generated from confirmed weekly plan minus current pantry
- Grouped by store aisle
- Checkbox UI for in-store use
- Export to anywhere (copy, share to Notes, share to SMS)
- **Share-link, co-editable.** Anyone with the link can add/check items in real time. Partner
  collaboration without a second login.

### Deferred to v2

- Grocery delivery integrations (Instacart, Walmart+, Amazon Fresh). Each is real engineering
  (API mapping, SKU resolution, out-of-stock substitution) and cholerics often prefer in-person
  shopping anyway.

---

## 11. Cook mode

The kid cook mode is a **per-recipe toggle**, not a separate section of the app. Open any recipe,
tap "Make it kid-friendly," and the recipe transforms: simpler language, larger illustrations,
the app reads each step aloud, kid taps to advance.

### v1 cook mode

- **Tablet-fit, landscape primary canvas.** Phone supported as fallback. Designed for an iPad
  on the counter.
- **One step at a time.** Large illustration, large type, single primary action.
- **One-way text-to-speech narration.** App reads the step aloud; kid does not speak to the app.
- **Kid taps to advance.** Giant next-step button.
- **Spotify SDK integration.** Optional background music plays softly when the assistant isn't
  narrating. User brings their own Spotify Premium account.

### Deferred to v1.5

- Per-kid age adaptation (a 4-year-old sees different step language than a 7-year-old)
- Character / sound design / motion polish for kid mode
- Per-recipe "what your kid can help with" callouts based on age
- Photo "show me" capture (kid snaps the step they just finished)

### Why no kid voice input

A deliberate privacy choice. Voice recordings of minors carry meaningful legal and ethical
weight even with parental consent. The product avoids the category entirely. Kid cook mode is
**one-way TTS, kid taps to advance** — full stop.

---

## 12. Design — three registers

The product runs three distinct visual registers in one product. Each has its own surface and
each must be deliberate.

| Register | Audience | Vibe | Where it lives |
|---|---|---|---|
| **Power surface** | Choleric parent in planning mode | Dense, efficient, keyboard-friendly, dashboards, bulk edits, visible structure | Sunday planning, weekly view, shopping list, pantry, eater management |
| **Warm brand expression** | Same parent, emotional layer | Food iconography, family photos, "Maya cooked her first pancake" moments, warm color palette | Cards, badges, microcopy, onboarding moments, kid profile pages |
| **Kid cook mode** | The kid on a tablet | Big, playful, illustrative, voice-narrated, large touch targets, music | Inside cook mode only |

The existing design overview (`designs/overview.md`) covers the warm brand expression well but
**does not yet cover the power surface or kid cook mode**. Both need their own design pass before
v1 can ship. Specifically:

- The current home (a "Meal Plans" list) is wrong for the proactive product — the home should
  become a **"This Week"** dashboard with a **"Tonight"** card pinned.
- Kid cook mode is a new canvas (tablet, landscape) that the desktop-first design system doesn't
  cover.

---

## 13. Sharing model

No second login in v1. Three share-link types cover the partner / caregiver collaboration cases:

| Share | Permission | Use case |
|---|---|---|
| **Weekly plan share** | Read-only | Partner sees the week without editing |
| **Shopping list share** | Read + write | Either partner adds items; real-time collaborative |
| **Single recipe share** | Read-only, enters cook mode | Nanny cooks tonight's dinner without seeing the rest of the household data |

---

## 14. Privacy and child data

Even without kid accounts, the product handles preference data about children. Posture:

- **No voice recordings of minors, ever.** Kid cook mode is one-way text-to-speech only.
- **No kid microphone input.** No speech-to-text on minors. No feedback collection via voice.
- **Kid preference data is profile-attached and editable/deletable by the account holder at any
  time.**
- **Account holder controls all sharing.** Share-links can be revoked.
- **No third-party advertising on kid-facing surfaces.** No advertising in the product at all.

---

## 15. Business model

### Pricing

- **$5.99 per month**, or annual equivalent (TBD with conventional ~33% annual discount)
- **7-day free trial, no credit card required**
- **No freemium tier**
- **No advertising of any kind**

Pricing matches Mealime exactly — deliberate competitive positioning. Cholerics will pay this
price for time saved and will not tolerate ads.

### Future tier

- **Family Plan** (~$14.99/mo) lands in v2+, unlocking:
  - Second adult login (true co-planner)
  - Co-parent across two households
  - Advanced caregiver permissions
  - Possibly: extended AI features (higher modification limits, faster vision processing)

---

## 16. v1 scope

### What ships in v1

- Choleric-targeted artifact-import onboarding (photo, URL paste, manual list)
- Curated recipe library (~150 recipes at launch)
- URL recipe import with source attribution
- Conversational weekly planning (Sunday flow)
- Recipe modification AI: scale, substitute, kid-friendlify
- Per-meal eater attendance toggle
- Shopping list: generate, export, share-link co-edit
- Pantry: photo + shopping confirmation + recipe decrement
- "This Week" / "Tonight" home screen
- Sunday push notification (primary); Tuesday and Saturday opt-in
- Cook mode v1: one-way text-to-speech, kid taps to advance, tablet layout
- Spotify SDK background music integration (cook mode only)
- Single design system covering power surface + warm brand
- Up to three eater profiles per household (soft default)
- 7-day trial, $5.99/month subscription

### Out of scope for v1 (deferred to v1.5)

- Multi-kid optimization
- Pantry vision (computer vision over fridge photos)
- Cultural / dietary adaptation
- Pattern detection insights (data collection ships in v1; surfacing in v1.5)
- Age-adapted recipe difficulty per kid
- Character / sound design polish for kid cook mode
- Library expansion beyond initial 150 recipes

### Out of scope for v1 (deferred to v2)

- Grocery delivery integrations
- Chrome extension for recipe save
- Second adult login (Family Plan tier)
- Co-parent across two households
- Bulk recipe import beyond manual URL paste

### Permanently out of scope

- AI-generated recipes from scratch (modification only)
- Kid voice input (no microphone access for kids; one-way text-to-speech only)
- Voice recordings of minors stored anywhere
- Advertising of any kind
- Infant-feeding features (different product)
- B2B / enterprise (consumer only)

---

## 17. Open questions

- **Curated library acquisition.** Who builds the initial 150 recipes? Freelance recipe
  developer, partnership with food bloggers, dietitian contractor? Cost and timing implications.
- **Annual pricing point.** Conventional 33% discount on $5.99/mo gives ~$48/year. Worth
  benchmarking against Mealime's annual pricing.
- **Trial-to-paid conversion target.** Industry benchmark for productivity-style consumer
  subscriptions is 5–15% of free trials converting. Need to set a v1 conversion target to inform
  acquisition spend.
- **Optical character recognition vendor for onboarding photo ingest.** Open AI vision,
  Google Cloud Vision, or in-house? Affects cost-per-onboard.
- **Plus Jakarta Sans for kid cook mode.** Current type system is one font; kid mode may benefit
  from a more playful display face. Design pass needed.
- **Tablet-fit canvas dimensions for kid cook mode.** Existing design overview is 1440×900
  desktop; cook mode needs a landscape tablet canvas (likely 1180×820 iPad reference).
- **Geographic launch.** US-first, English-only, imperial units? Or also metric / multilingual?
  Affects recipe library and unit handling.

---

## 18. References

- Existing design language and Penpot screens: [`designs/overview.md`](designs/overview.md)
- Backend / frontend architecture: [`docs/architecture.md`](docs/architecture.md)
- Engineering conventions: [`docs/coding_conventions.md`](docs/coding_conventions.md)
- Testing conventions: [`docs/testing.md`](docs/testing.md)
- Inspiration: [mealime.com](https://mealime.com), [eatthismuch.com](https://eatthismuch.com)
