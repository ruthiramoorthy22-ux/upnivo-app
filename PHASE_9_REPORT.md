# Phase 9 Report — Google Play Store Compliance

**Status: PARTIAL.** Research, audit, drafts and fixes are done. **The app is not ready to submit**; several items are yours or need decisions. Nothing was submitted and Google has approved nothing.

## Work completed
- Researched current official requirements (target API 36 from 2026-08-31; payments, India billing; testing requirements; UGC; account deletion).
- Data Safety draft built from the code, with evidence table and known gaps.
- Compliance audit across all 18 requested areas.
- Store listing, reviewer access guide, release checklist.
- Fixed compliance-relevant defects found along the way:
  - Account deletion now removes associated data (it previously left submissions, notifications and push registrations).
  - Public deletion page rewritten (overflow fix; names the app/package; states what is deleted and kept; confirmation checkbox).
  - Privacy policy corrected: it claimed a certificate-verification feature that does not exist and omitted push registrations, Razorpay, hosting and Google Fonts; it claimed device/login data that is not collected.
  - `/privacy`, `/terms`, `/refund` are now standalone server-rendered HTML pages (previously redirects into a JavaScript route).
  - Support email is configurable (`SUPPORT_EMAIL`); the `admin@yourdomain.com` placeholder remains until you set it.
- Generated Play assets from the real app: 6 phone screenshots (1080×1920) and a feature graphic (1024×500).

## Files created
`GOOGLE_PLAY_COMPLIANCE_AUDIT.md`, `GOOGLE_PLAY_DATA_SAFETY_DRAFT.md`, `GOOGLE_PLAY_STORE_LISTING.md`, `GOOGLE_PLAY_REVIEWER_ACCESS_GUIDE.md`, `GOOGLE_PLAY_RELEASE_CHECKLIST.md`, `PHASE_9_REPORT.md`, `play_store_assets/` (7 PNGs)

## Files modified
`main.py` (policy pages, SUPPORT_EMAIL injection, deletion purge), `static/app.html` (policy text), `static/delete-account-request.html`, tests.

## Tests
Backend tests for deletion purge, policy pages, support-email injection and policy/code consistency: PASS (see FINAL_INTEGRATION_TEST_REPORT.md).

## Blockers before submission
1. **Payment route decision** (Play Billing vs India user-choice billing vs free certificate). Razorpay/UPI inside the Android app is likely non-compliant.
2. Real support email and developer/entity name in the policy and listing.
3. Reviewer account (needs your live site).
4. Signing key, real Android build, asset links (Phase 8).
5. Closed-testing requirement if your developer account is a personal one created after 2023-11-13.
6. Decide retention period and cloud-image deletion (Data Safety gaps).
7. Target-audience decision (policy says 16+).

## NOT VERIFIED
Exact current wording of every official page (several were read via search excerpts, not in full); account-deletion rules were confirmed from Google's 2023 announcement, not the current Play Console page; UGC conclusion is my reading, not Google's.

## Approvals / paid
Google Play Console registration fee (yours). Publishing needs your explicit approval.
