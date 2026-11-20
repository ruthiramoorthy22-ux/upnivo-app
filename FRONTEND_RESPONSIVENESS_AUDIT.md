# Frontend Responsiveness Audit (Phase 7)

Date 2026-11-19. Method: the real app served locally on a seeded throw-away database and driven by a **real headless Chromium** (not just CSS reading), mobile emulation with touch for phones.

Viewports: 320×568 (small phone), 360×740, 412×915 (Android), 768×1024 (tablet), 1280×800 (desktop).
Pages (15 student + 10 admin tabs + admin login + deletion page = 27) × 5 viewports = **135 measurements before and after**; a third, corrected-metric run covered 360 and 1280 (54 measurements).
Screenshots from each run were kept in the working folder (not shipped).

## Starting point
The student app is already a mobile-first design (fixed bottom navigation on phones, sidebar on desktop, safe-area insets, fluid cards). Zero console errors and zero failed network requests were seen anywhere. The design was **preserved**; only defects were fixed.

## Findings and fixes

| Area | Before | After | Fix |
|---|---|---|---|
| Horizontal overflow | **3 pages overflowed** (`/delete-account-request` at 320/360/412) | **0** | Page rewritten with `box-sizing: border-box` and `width: min(100%, 520px)`; the box used `content-box` + padding so it exceeded narrow screens |
| Zero-count notification badge | A red **"0"** badge always showed on Alerts (and on admin) | hidden when zero | The `hidden` attribute was overridden by `.bdg{display:flex}`; added `[hidden]{display:none!important}` |
| Touch targets < 44 px | 1,597 of 1,940 interactive elements | 644 of 1,945 | `.chip`, `.btn.sm`, bottom-nav items, back buttons, info links, plan links raised to ≥ 44 px |
| Touch targets < 24 px (WCAG 2.2 AA minimum) | 179 | 52 | remaining: inline links inside paragraphs (exempt under WCAG 2.5.8) and the admin Certificate-table links |
| Images | `logo.png` was 526 KB at 1254² shown at ≈ 40–130 px | `icon-512.png` (98 KB) for app screens; original kept for printed documents | −428 KB on first load; service-worker cache bumped to `upnivo-v5` |
| Admin phone navigation | icon-only bottom bar; labels hidden, so unnamed for screen readers | named via `aria-label`, ≥ 44 px, focusable | see ACCESSIBILITY_AUDIT.md |
| Loading / error / empty states | Spinner, toasts and "no items" states already present | unchanged | none needed |

## Not changed / remaining
- Admin tables on phones scroll horizontally inside their own container (no page overflow). Many admin row buttons are still < 44 px (advisory; the admin area is desktop-oriented).
- Banner on a completed program still says "Unlock your certificate below" after the certificate has been paid (cosmetic wording; not changed).
- App-wide `maximum-scale` is not restricted, so pinch-zoom works (good).
- Load: `app.html` is 82 KB (26 KB gzipped, GZip middleware active); fonts load from Google Fonts (third-party; see Data Safety draft). Lazy loading is not used for the few images.
- Real devices were not available; emulation is not a substitute for testing on at least one physical Android phone.
