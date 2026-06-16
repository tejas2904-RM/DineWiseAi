# Google Stitch Prompt — DineWise AI (Phase 8, Next.js)

> Paste the block below into **Google Stitch** (stitch.withgoogle.com) to
> generate UI mockups / images for the Phase 8 frontend.
> Stitch works best with one screen request per prompt — sections are
> separated by `---` so you can submit them individually if needed.

---

## Master prompt (paste this first)

```
Design a modern, premium restaurant-recommendation web app called
"DineWise AI". The frontend is built with Next.js 14 (App Router),
TypeScript, and Tailwind CSS. The look should feel calm, editorial,
and trustworthy — like a cross between Airbnb and Linear, with a hint
of food-magazine warmth.

Brand & visual system
- App name: DineWise AI. Tagline: "The art of restaurant selection."
- Primary accent color: deep blue #2563EB (light mode) / soft blue
  #60A5FA (dark mode).
- Background light mode: #F7F8FB (page), #FFFFFF (cards).
- Background dark mode: #0B1120 (page), #111827 (cards).
- Borders: #E2E8F0 light / #1F2937 dark. Rounded radius 14 px on
  cards, 10 px on buttons/inputs.
- Subtle card shadow (0 4px 14px rgba(15,23,42,0.06)).
- Typography: Inter or system sans-serif. Generous line-height,
  comfortable reading width (max 1100 px content).
- Iconography: lucide-react line icons (24 px), thin strokes.
- Pill-shaped chips for tags (cuisine, budget, rating).
- Skeleton shimmers while data is loading.
- Always-visible focus rings; AA contrast in both light & dark.

Global layout
- Sticky top navbar with: app logo + "DineWise AI", nav links
  Dashboard / History / Favorites, theme toggle (sun/moon), and
  installable-PWA hint.
- Footer: "DineWise AI · Phase 8 · Personalized recommendations".
- Mobile-first responsive — single column under 768 px, 2-3 column
  card grid above.
```

---

## Screen 1 — Dashboard (home `/`)

```
Generate the Dashboard screen for DineWise AI.

Top section (greeting hero card):
- Time-aware greeting "Good evening, Tejas" with a sparkle icon.
- Subtitle: "Tell us what you're craving and we'll handpick the
  best spots for you."
- Editable user name (pencil icon).

Preference form (card, two-column on desktop):
- Location: dropdown menu (select) populated with Bangalore
  neighborhood names like Indiranagar, Koramangala, HSR, Bellandur,
  Whitefield, JP Nagar, Jayanagar, BTM, Frazer Town. Show a "Loading
  locations…" placeholder state and an empty-state variant.
- Cuisine: dropdown menu (select) populated from the Zomato dataset
  with ~105 cuisine types (e.g. North Indian, South Indian, Italian,
  Chinese, Biryani, Mughlai, Cafe, Pizza, Thai, Mexican, Seafood).
  Show a "Loading cuisines…" placeholder state and an empty-state
  variant with a Retry link.
- Budget: select with options Low (< ₹500), Medium (₹500–1500),
  High (> ₹1500).
- Minimum rating: numeric input 0–5 step 0.1, default 4.0.
- Top K results: numeric input 1–20, default 5.
- Primary submit button "Find restaurants" with a search icon and
  a loading spinner state ("Searching…").

Recent searches strip:
- Horizontal row of pill-shaped chips, each chip shows
  "Indiranagar · north indian · medium". Clicking re-runs that search.

Results section:
- Header: "5 recommendations · AI-generated · 1234 ms".
- View toggle (segmented control) with List / Map tabs.
- List view: 3-column responsive card grid. Each card has:
    • Restaurant name (large), cuisine subtitle.
    • Rating chip (★ 4.5), price chip (₹ 700), small reason
      paragraph.
    • Bottom action row: heart (favorite), thumbs-up,
      thumbs-down, share icon.
- Map view: full-width OpenStreetMap-style map with numbered
  pin markers (1–5) clustered around the searched neighborhood,
  side-panel list synchronized with markers.

Empty / loading / error states:
- Skeleton shimmer cards while fetching.
- Empty state: a sparkle illustration with "Ready when you are".
- Error state: red-bordered card "Something went wrong" + retry.
```

---

## Screen 2 — History page (`/history`)

```
Generate the Search History page for DineWise AI.

- Page title "Your search history" with a clock icon.
- Subtitle "Past recommendation requests, most recent first."
- Stack of history cards (full-width, vertical list).
- Each card shows:
    • Top row of chips: location (with map-pin icon), cuisine,
      budget (₹ icon), "≥ 4.0 ★".
    • Right-aligned timestamp ("May 10, 2026, 14:32").
    • Below: numbered list of the top 5 recommended restaurants
      with name, cuisine, rating ★ and ₹ cost, separated by middle
      dots.
- Hover state: lift the card slightly, increase shadow.
- Empty state: centered card "No history yet — Run a recommendation
  from the dashboard and it will appear here."
- Loading: 4 stacked shimmer placeholders.
```

---

## Screen 3 — Favorites page (`/favorites`)

```
Generate the Favorites page for DineWise AI.

- Page title "Your favorites" with a filled heart icon in accent
  color.
- Subtitle "Restaurants you've saved for later."
- Responsive 3-column card grid.
- Each favorite card has:
    • Restaurant name + cuisine subtitle.
    • Trash icon top-right (with tooltip "Remove").
    • Rating chip "★ 4.5" and cost chip "₹ 700".
    • Tiny "Added May 5, 2026" caption.
- Empty state (card, centered): big heart icon, "No favorites yet
  — Tap the heart on any recommendation to save it here."
- Loading: 3 shimmer placeholder cards.
```

---

## Screen 4 — Recommendation card detail (component close-up)

```
Generate a close-up of a single Recommendation Card component for
DineWise AI.

- White card (or dark-mode equivalent), 14 px corners, soft shadow.
- Header: restaurant name in semi-bold 18 px, cuisine label in
  muted gray.
- Body: a 2–3 sentence "Why you'll like it" paragraph (the AI
  reason).
- Chip row: cuisine tag, rating ★ chip, price ₹ chip.
- Action row at bottom: filled heart toggle (favorite),
  thumbs-up/down icons (feedback), share icon (Web Share / copy
  link). Each action has a subtle tooltip on hover.
- Show two variants side-by-side: default and "favorited"
  (heart filled in accent color).
```

---

## Screen 5 — Dark mode variants

```
Recreate the Dashboard, History, and Favorites screens in dark
mode using these tokens:
- Page background #0B1120, card background #111827.
- Text primary #F1F5F9, secondary #CBD5E1, muted #64748B.
- Border #1F2937. Accent #60A5FA. Soft accent #1E293B.
- Danger #F87171, Success #4ADE80, Warning #FBBF24.
- Shadow 0 4px 14px rgba(0,0,0,0.45).
Make sure focus rings, chips, and skeletons remain visible and
WCAG-AA compliant.
```

---

## Screen 6 — Mobile + PWA install banner

```
Generate the mobile (375 × 812) version of the Dashboard for
DineWise AI:
- Single-column layout.
- Hamburger replaced by a bottom tab bar: Dashboard, History,
  Favorites, Theme.
- Above the form, a slim banner: "Install DineWise AI for the best
  experience" with an "Install" button (PWA install prompt).
- Form fields stack vertically; full-width submit button.
- Result cards take full width with horizontal scroll for chips.
```

---

## Optional polish prompts

```
- Generate a custom 512×512 app icon: monogram "DW" inside a
  rounded square, accent blue #2563EB background, white glyph,
  flat / modern.
- Generate an empty illustration for "No history yet" — a small
  isometric line drawing of an open notebook with sparkles.
- Generate a hero illustration for the greeting card — minimalist
  table setting (plate, chopsticks, cup) in two-tone accent blue
  on cream.
```

## Tips for using these prompts in Stitch

1. Submit the **Master prompt** first and let Stitch lock in the
   visual system.
2. Then submit each Screen prompt one at a time so Stitch focuses
   on layout for that screen.
3. If colors drift, re-paste the "Brand & visual system" section
   at the top of any follow-up.
4. Ask Stitch for both **light** and **dark** variants explicitly —
   it tends to default to light.
5. For map views, mention "OpenStreetMap-style tiles with numbered
   pins" so Stitch doesn't render Google Maps branding.
