# Design System: Editorial Precision for Rental Data

## 1. Overview & Creative North Star
The core objective of this design system is to transform raw price data into an authoritative, premium narrative. We are moving away from the "utility dashboard" aesthetic toward **"The Digital Aviator"**—a Creative North Star that prioritizes high-contrast legibility, sophisticated depth, and a sense of high-velocity precision.

The system breaks the standard "bootstrap" mold by utilizing intentional asymmetry in its layouts and a aggressive typographic scale. By leveraging deep obsidian surfaces (`#0e0d14`) against vibrant amber (`#fe9821`) and electric violet (`#a68cff`) accents, we create a high-fidelity environment where users don't just "track prices," but "oversee a market."

---

## 2. Colors: Tonal Architecture
Color in this system is not decorative; it is structural. We define boundaries through luminosity shifts rather than lines.

### Surface Hierarchy & The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to section off UI components. Boundaries must be defined through background color shifts or tonal transitions.
- **Base Layer:** Use `surface` (`#0e0d14`) for the main canvas.
- **Primary Containers:** Use `surface_container` (`#1a1921`) for main content areas to create a soft lift.
- **Nested Elements:** Use `surface_container_highest` (`#26252f`) for interactive elements like input fields or cards sitting inside a primary container.

### The "Glass & Gradient" Rule
To elevate the experience, floating elements (like price-drop alerts or modal overlays) should utilize **Glassmorphism**. Apply a backdrop-blur (12px–20px) to `surface_container_low` with a 70% opacity. 

Main CTAs must use a **Signature Texture**: a linear gradient from `primary` (#fe9821) to `primary_container` (#ea8908). This provides a "physical" presence that flat hex codes lack.

---

## 3. Typography: Editorial Authority
We use a dual-font strategy to balance character with data density.
- **Headlines (Manrope):** Our "voice." Used for high-level data like `display-lg` (3.5rem) and `headline-md` (1.75rem). This font's geometric construction feels modern and engineered.
- **Body & Labels (Inter):** Our "engine." Inter is used for all tabular data, labels, and fine print. It is chosen for its exceptional legibility at small scales (0.75rem `label-md`) and its neutral, "pro" feel.

**Hierarchy Note:** Prices should always use `display-sm` or `headline-lg` to ensure they are the first thing a user sees. Use `on_surface_variant` (`#ada9b3`) for labels to create a clear visual distinction from the primary data.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are largely prohibited. We achieve hierarchy through the **Layering Principle**.

*   **Tonal Stacking:** Place a `surface_container_lowest` card on a `surface_container` section to create a "recessed" look. Place a `surface_bright` element to indicate a "hovered" or "active" state.
*   **Ambient Shadows:** If a floating effect is required (e.g., a "Car Category" picker), use a shadow with a 32px blur, 0px offset, and 8% opacity. The shadow color must be a tinted version of `surface_container_lowest`, never pure black.
*   **The "Ghost Border" Fallback:** If accessibility requires a border, use the `outline_variant` (#49474f) at 15% opacity. This creates a "suggestion" of a boundary without cluttering the high-contrast aesthetic.

---

## 5. Components: Precision Primitives

### Buttons
- **Primary:** Gradient fill (`primary` to `primary_container`), `on_primary` text, `rounded-md` (0.75rem).
- **Secondary:** Surface-tinted (`surface_container_highest`), no border, `on_surface` text.
- **Tertiary:** Ghost style, `on_surface_variant` text, turns to `on_surface` on hover.

### Price Tracker Cards
- **Constraint:** Strictly no divider lines. 
- **Style:** Use `spacing-6` (1.3rem) of vertical whitespace to separate the car image from the price graph. 
- **Background:** Use `surface_container_low` with a subtle 2px `rounded-lg` corner.

### Data Visualization (The "Pulse" Graph)
- **Primary Line:** Use `primary` (#fe9821) with a 3px stroke width.
- **Area Fill:** A gradient transition from `primary` (20% opacity) at the top to `surface` (0% opacity) at the baseline.
- **Highlight:** Use `tertiary` (#81ecff) for "Best Price Found" markers to provide a vibrant "pop" against the dark theme.

### Inputs & Search
- Use `surface_container_highest` for the input field background.
- Typography: `body-md` (Inter).
- Active state: Change "Ghost Border" to 40% opacity of `primary`.

---

## 6. Do's and Don'ts

### Do
- **Do** use `rounded-xl` (1.5rem) for large dashboard containers to soften the high-contrast "tech" look.
- **Do** use `spacing-10` and `spacing-12` to allow data-heavy views to "breathe."
- **Do** use `secondary` (#a68cff) for "Luxury" or "Premium" car categories to denote status.

### Don't
- **Don't** use pure white (#ffffff) for text. Always use `on_surface` (#f4eff9) to reduce eye strain on dark backgrounds.
- **Don't** use 1px dividers. If you feel you need one, increase the spacing by two increments on the scale instead.
- **Don't** use standard "Success Green." Use `tertiary` (#81ecff) for positive trends and `error` (#ff7351) for price hikes to maintain the signature palette.