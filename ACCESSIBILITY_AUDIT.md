# Accessibility Audit (Phase 7)

Target: WCAG 2.2 Level AA as a goal. **This is an automated and keyboard-driven audit; it is not a full manual or screen-reader audit and does not certify conformance.**

| Check | Before | After | How verified |
|---|---|---|---|
| Form controls without an accessible name | **195** across 135 measurements (login, register, search, profile, every admin form) | **0** | DOM scan; a small script links `label`↔`input` or adds `aria-label` from placeholder/id, and re-applies when screens re-render |
| `<img>` without `alt` | 110 | **0** (brand logo "UPNIVO INTERN"; decorative = `alt=""`; document logo/signature alt added in server templates) | DOM scan |
| Clickable `<a onclick>` / `<div onclick>` not reachable by keyboard | Not reliably measurable (see correction) | **0 on every audited page** | DOM scan + real keyboard test: focus a bottom-nav item, press Enter → navigates; domain card + Enter → opens detail |
| Visible keyboard focus | none for links, buttons, cards | 3 px `#0ea5e9` outline on all focusable elements, inputs and the search bar | first-Tab computed style; inputs verified after their 150 ms transition |
| Dialog semantics | plain `div` | `role="dialog"`, `aria-modal`, focus moved in, **Esc closes** | browser test |
| Live regions | toasts silent | toasts `role="status"`; deletion page result `aria-live="polite"` | DOM / browser test |
| Landmarks | none | app root `role="main"`; deletion/policy pages use `<main>` | DOM |
| Reduced motion | ignored | `prefers-reduced-motion` honoured | CSS |
| Icon-only admin navigation | no accessible name on phones | named from its hidden label | DOM scan (11/11 named) |
| Page language / title | `lang="en"` and titles present | unchanged | DOM |

### Correction to my own measurement
My first "keyboard reachability" counter treated `tabIndex < 0` as "not focusable". In Chrome an `<a>` **without `href` reports `tabIndex 0`** even though it cannot receive focus, so every bottom-nav item stayed unreachable and my numbers undercounted them. A real keyboard test failed (Enter on the Profile tab did nothing), I fixed the script to test the `tabindex` attribute, and re-ran everything. All figures above are from the corrected check.

## Known remaining items (not fixed)
1. **Headings**: most app screens have no `<h1>` (titles are styled `div`/`h2`). Needs template edits to each screen.
2. **Colour contrast** was not measured numerically. Light-on-gradient hero text and grey helper text should be checked with a contrast tool.
3. **Screen-reader testing** (TalkBack) was not done.
4. **Focus order after route changes**: focus is not moved to the new page heading.
5. Client-side `role="button"`/`role="link"` are added by script rather than written as real `<button>`/`<a href>` elements; the semantic fix is to change the templates.
6. Admin row action buttons are small on phones.
