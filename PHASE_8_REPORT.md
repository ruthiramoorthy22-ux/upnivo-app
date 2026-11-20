# Phase 8 Report — Android TWA Application

**Status: PARTIAL.** The Android project is generated and its configuration is verified by tests, but **nothing was compiled**: the Android SDK, Gradle and Maven hosts are unreachable from the sandbox. No signed AAB exists.

## Work completed
- PWA audit; manifest corrected (theme/background colour aligned with the page, `id` added, `any` and `maskable` icon purposes separated using the existing real icons).
- Real TWA project generated with Bubblewrap Core 1.27.0 into `android/` (package `com.upnivo.app`, **targetSdk 36**, versionCode 1 / 1.0.0, notification delegation, no WebView shortcut).
- Digital Asset Links endpoint hardened (format validation, multi-fingerprint, no-invented-values) and tested.
- Guides: setup, asset links, signing, AAB build, audit.

## Files inspected
`static/manifest.webmanifest`, `static/sw.js`, icons, `main.py` (assetlinks route), Bubblewrap templates.

## Files created
`android/` (41 generated files incl. Gradle wrapper, `twa-manifest.json`, resources, `.gitignore`), `ANDROID_TWA_AUDIT.md`, `ANDROID_TWA_SETUP_GUIDE.md`, `DIGITAL_ASSET_LINKS_GUIDE.md`, `ANDROID_SIGNING_GUIDE.md`, `AAB_BUILD_GUIDE.md`, `PHASE_8_REPORT.md`, `tests/test_assetlinks_pwa.py` (11 tests)

## Files modified
`static/manifest.webmanifest`, `static/sw.js`, `main.py` (assetlinks validation), `.gitignore` (keystores/AAB/APK), `.env.example` (`ANDROID_PACKAGE`, `ANDROID_SHA256`, `SUPPORT_EMAIL`)

## Verified (PASS)
- Manifest fields and icons exist on disk (test).
- Service worker registers, activates and serves the start URL offline (real browser).
- Generated project: package, targetSdk ≥ 36, version, no secrets, no keystore (test).
- Asset links: empty until configured; valid config produces correct JSON; malformed package/fingerprints rejected (7 tests).

## BLOCKED / NOT DONE
| Item | Why |
|---|---|
| Android build (debug or release) | SDK/Gradle/Maven unreachable; project never compiled |
| Signed AAB | no signing key exists, by design; you must create it |
| Real fingerprints / live `assetlinks.json` | need your key; deploying needs your approval |
| Device test (full-screen, notifications) | no device |
| Live domain check (HTTPS, hosting) | sandbox cannot resolve `onrender.com` |
| Custom domain decision | business/DNS decision; recommended before first release |

## Risks recorded
`jcenter()` in generated root Gradle file; Bubblewrap project generated without its final live-manifest fetch (regenerate with `bubblewrap update`); free-tier cold starts; payment-policy decision affects whether the app can ship as is.

## Paid services / approvals
Google Play developer account fee (yours); optional custom domain. No paid service was activated.
