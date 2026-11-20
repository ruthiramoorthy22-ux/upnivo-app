# Phase 6 Report — Razorpay Security and Google Play Billing Policy

**Status: PASS for local code and tests; PARTIAL overall** (policy classification needs Google confirmation; PostgreSQL, live-gateway and browser checks not done).

## Starting state
Phase 6 had left no files behind (no report, no payment changes). Working tree already contained uncommitted Phase 2–5 work (modified `main.py`, `app.html`, `README.md`, etc.). Backup of the whole project (excluding `.git` and caches) was made outside the project folder before any edit. Baseline: 5/5 existing tests passed.

## Work completed
- Audited the payment code; found 10 issues (see RAZORPAY_SECURITY_AUDIT.md), including a permanent "payment already in progress" lock for students who closed checkout, and an admin endpoint able to overwrite gateway-confirmed payments.
- Fixed all of them in `main.py` with additive database changes only.
- Wrote 32 payment tests and mutation-checked them.
- Researched current official Google Play payment policy and India programs; produced options and a backend plan. Nothing billing-related was faked or implemented.

## Files inspected
`main.py`, `programs.py` (header only), `requirements.txt`, `.env.example`, `.gitignore`, `static/app.html` and `static/admin.html` (payment sections), `tests/test_verification.py`, `static/` listing, git status.

## Files created
`tests/test_payments.py`, `RAZORPAY_SECURITY_AUDIT.md`, `PAYMENT_FLOW_DOCUMENTATION.md`, `GOOGLE_PLAY_BILLING_POLICY_REVIEW.md`, `PAYMENT_TEST_REPORT.md`, `PHASE_6_REPORT.md`

## Files modified
- `main.py`: Payment model columns, `WebhookEvent` table, migration + indexes, payment rate limits, hardened Razorpay helpers, rewritten order/verify/webhook, admin payment review, UPI duplicate-UTR check, admin settings (mode only).
- `.env.example`: added `RAZORPAY_ORDER_TTL_HOURS`.

## Files deleted
None.

## API compatibility
All existing routes and response shapes are unchanged. `razorpay-order` now returns the existing open order on retry instead of 409. `PUT /admin/payments/{id}` now returns 409 for gateway payments and already-reviewed payments. `/admin/settings` gained `razorpay_mode` and `razorpay_webhook`. No frontend file changed.

## Tests
PASS: 37/37 (5 existing + 32 new). FAIL: 0. NOT TESTED / BLOCKED: see PAYMENT_TEST_REPORT.md.

## Remaining manual work
1. Review and merge the changes; deploy only when you approve.
2. In Razorpay: webhook URL + secret, confirm auto-capture, do one **test-mode** payment end to end.
3. Test on PostgreSQL before production.
4. Decide Option A/B/C/D for Android billing and, ideally, get Google Play support to confirm.

## Paid-service / approval requirements
None activated. Production deploy, live Razorpay and Play Console actions all need your explicit approval.

## Decisions I made that you may want to change
- Test/live key mismatch only warns (does not stop startup), to avoid taking the site down if `APP_ENV` is unset on Render.
- Full refund re-locks the certificate.
- Unpaid orders are reused for 24h rather than recreated.
