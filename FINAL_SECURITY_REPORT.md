# Final Security Report (Phase 10)

Scope: backend (`main.py`), frontend pages, payment flow, Android TWA config. Method: code review, 84 automated tests (SQLite + PostgreSQL 16), real-browser runs. **Not** a penetration test and not an independent audit.

## Issues found and fixed during Phases 6–10
| Severity | Issue | Fix |
|---|---|---|
| **High** | If `ADMIN_PASSWORD` was unset, startup created **and on every restart reset** the admin account to the public default `change-me-in-production` | Default now allowed only for local SQLite development; otherwise admin is not created/changed and an error is logged (tested) |
| High | Admin endpoint could overwrite gateway-confirmed payments and unpaid orders | Gateway payments immutable; UPI reviewed once |
| High | Webhook had no amount/currency check, no replay protection, ignored refunds | Signed, size-capped, deduped, amount/currency-validated, refunds recorded |
| High | Abandoned checkout blocked a student from ever paying again | Open order reused; stale ones expire; late payment honoured |
| High (data) | Account deletion left submissions, notifications, push registrations, screenshots and admin-side copies of name/email | Purged (tested; other users untouched; path traversal blocked) |
| High (data) | Deleting an internship also deleted students' applications and **paid payment records** | Refused with 409 when paid/refunded payments exist (unpublish instead) |
| Medium | No security headers | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, HSTS over HTTPS |
| Medium | Non-ASCII signature header caused HTTP 500 | Byte-safe constant-time compare |
| Medium | Razorpay/Cloudinary/S3 error text returned to clients | Logged server-side, generic message |
| Medium | Payment endpoints not rate limited; UTR reusable | Limited; duplicate UTR refused |
| Medium | `postgres://` DB URL crashed startup | Normalised to the installed psycopg 3 driver (tested) |
| Medium | Privacy policy made false claims (certificate verification, device data) and omitted processors | Corrected |
| Low | No health endpoint | `/api/health` (DB ping, no details) |
| Low | Missing `alt`/labels/keyboard access | see ACCESSIBILITY_AUDIT.md |

## Residual risks (unfixed)
1. **No Content-Security-Policy.** Pages use inline scripts/handlers and Razorpay Checkout loads third-party frames; a CSP must be developed and tested against a real test-mode payment first. Stored-content XSS is mitigated by escaping (not audited exhaustively here).
2. **`SECRET_KEY` fallback**: if unset, a random key is generated per process, so logins break on every restart and across multiple workers. Always set it on Render.
3. **JWTs last 7 days and are stateless**: "logout" does not revoke a stolen token; deactivating/deleting the account does (tested). No refresh/rotation.
4. **Rate limiter** is in memory per process and trusts `X-Forwarded-For`; use a shared store/edge limiting if you scale out.
5. **Passwords**: Argon2 hashing; minimum length enforced; no breached-password check, no email verification, **no self-service password reset** (support-assisted only, via an email address that is currently a placeholder), no 2FA (also means web account deletion needs the password).
6. **Admin UI uses the same origin and a localStorage token** (XSS would expose it).
7. Cloud-stored images are not removed on account deletion; retention periods are undefined.
8. Google Fonts leaks visitor IPs to Google (self-host to remove).
9. Razorpay: `verify` trusts the signed browser callback; amount integrity relies on the server-created order and webhook check; auto-capture and webhook settings unverified; real webhook payloads untested.
10. Uploads: type and size validated; no antivirus scanning; images served from the same origin when local (production forces cloud storage).
11. `DELETE`/destructive admin actions have no audit trail beyond the basic log.
12. Dependencies were not scanned for CVEs (no network access to advisory databases was used).

## Secrets handling
No secrets in the repo (pattern scan), no `.env`, keystores ignored by git. Test credentials are obvious fixtures. Reports contain no secret values.
