# Google Play Release Checklist

Legend: [x] done and verified locally · [ ] not done / yours to do. Nothing here was published.

## Product and code
- [x] Payment hardening and 74+ automated tests (see FINAL_INTEGRATION_TEST_REPORT.md)
- [x] Mobile responsiveness verified in a real browser at 320–1280 px
- [x] Account deletion in-app and on the web; associated data removed (tested)
- [x] Standalone privacy/terms/refund pages; privacy text matches the code
- [x] Security headers, health check, rate limits
- [ ] **Decide the payment route** (Play Billing / India user choice billing / free certificate) and implement it
- [ ] Decide on certificate verification (feature does not exist)
- [ ] Self-host Google Fonts (removes a third-party IP disclosure) - optional
- [ ] Test a Razorpay **test-mode** payment end to end with the webhook
- [ ] Run the tests against PostgreSQL

## Deployment (needs your approval)
- [ ] Custom domain attached on Render (decide before building the app)
- [ ] `DATABASE_URL` (PostgreSQL), `SECRET_KEY`, `ADMIN_*`, `RAZORPAY_*`, `SUPPORT_EMAIL`, `ALLOWED_ORIGINS` set on Render
- [ ] Cloud storage configured and a real upload test passed
- [ ] `/api/health` returns ok on the live site; HTTPS + HSTS verified

## Android
- [ ] Upload keystore created and backed up by you
- [ ] `bubblewrap update` + `bubblewrap build` run; AAB produced and validated
- [ ] APK tested on a real phone: no address bar, login, upload, notifications, offline start
- [ ] `ANDROID_PACKAGE` / `ANDROID_SHA256` set (upload key **and** Play App Signing key) and assetlinks verified

## Play Console
- [ ] Developer account verified; account type known (personal vs organisation)
- [ ] Privacy policy URL, account deletion URL entered
- [ ] Data safety form submitted (from the draft, after resolving its gaps)
- [ ] Content rating, target audience, ads = No, app access instructions, financial features declaration
- [ ] Store listing: real contact email/address, screenshots, feature graphic, 512 icon
- [ ] Internal testing → closed testing (≥12 testers × 14 days for new personal accounts) → production
- [ ] Re-read all policies on the submission day
