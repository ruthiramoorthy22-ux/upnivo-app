# Razorpay Security Audit (Phase 6)

Date: 2026-11-19 · Scope: `main.py` payment code, `static/app.html` checkout, `static/admin.html` payment screens.
Method: code read-through, then fixes, then 32 automated tests with a mocked gateway. **No real Razorpay call and no real payment was made. No secret was read or printed.**

## Findings before changes (original code)

| # | Finding | Severity |
|---|---|---|
| F1 | An abandoned checkout left a `Created` row forever; `razorpay-order` then returned 409 permanently, so the student could never retry. | High (functional) |
| F2 | `PUT /api/admin/payments/{id}` could set **any** payment, including gateway-confirmed Razorpay ones and unpaid `Created` orders, to Paid or Rejected, with no state checks. | High |
| F3 | Webhook did not check amount or currency, had no event-id dedupe, and ignored failed, refund and expired cases. | High |
| F4 | `hmac.compare_digest` was given `str` values; a non-ASCII signature header raises `TypeError` (HTTP 500). | Medium |
| F5 | Razorpay error bodies (first 200 chars) were returned to the browser. | Medium |
| F6 | UPI UTRs were not checked for reuse across students. | Medium |
| F7 | Payment endpoints had no rate limiting. | Medium |
| F8 | Paid/Created transitions were read-then-write (race between browser callback and webhook). | Medium |
| F9 | Order creation did not validate that Razorpay's reply matched the requested amount/currency. | Low |
| F10 | No record of currency, paise amount, provider or refunds. | Low |

## Requirement checklist (your 15 points)

| # | Requirement | Result | Evidence |
|---|---|---|---|
| 1 | Backend calculates amounts | PASS | Amount from `fee()` setting; request body ignored. `test_order_amount_is_set_by_the_server`, `test_client_supplied_amount_is_ignored` |
| 2 | Frontend not trusted for amount/status | PASS | Frontend sends only Razorpay's callback fields; status is set only after HMAC check or signed webhook |
| 3 | Order tied to correct student/enrollment | PASS | `own_app()` ownership check + lookup scoped to `application_id`. `test_other_students_order_cannot_be_verified` |
| 4 | Payment signature verification | PASS | HMAC-SHA256 on `order_id\|payment_id`, constant-time, bytes-safe. `test_bad_signature_*`, `test_non_ascii_*` |
| 5 | Webhook signature verification | PASS | HMAC over raw body bytes; 503 if secret unset. `test_webhook_needs_configuration_*`, `test_webhook_bad_signature_and_oversize` |
| 6 | No duplicate webhook processing | PASS | `webhook_events.event_id` unique key, inserted in the same transaction. `test_webhook_unlocks_once_*` |
| 7 | No duplicate payment records | PASS (SQLite) | Unique index on `rzp_payment_id`; one open order per application (partial unique index + app check) |
| 8 | No unauthorized verification | PASS | Auth + ownership + signature required |
| 9 | Pending/failed/success/refunded handled | PASS | States: Created, Expired, Pending, Paid, Rejected, Refunded. Tests for failed, late, refund |
| 10 | Atomic updates | PASS on SQLite; NOT TESTED on PostgreSQL | Single conditional `UPDATE ... WHERE status IN (...)`; the winner (rowcount 1) alone sends notifications |
| 11 | Replay / order reuse | PASS | Paid order cannot take a different payment id (409); same confirmation is idempotent. `test_replay_*` |
| 12 | Currency and amount validation | PASS | Webhook compares amount and currency to stored values; order reply validated. `test_webhook_amount_or_currency_mismatch_never_unlocks`, `test_gateway_response_mismatch_is_rejected` |
| 13 | Test/live keys separate | PARTIAL | Mode detected from the key prefix, shown in admin settings, and a warning is logged on mismatch (live keys with `APP_ENV!=production`, test keys in production). **Deliberately not enforced**: your Render service may not set `APP_ENV=production`, and a hard failure could take the site down. |
| 14 | Admin payment endpoints protected | PASS | Admin-only; gateway payments cannot be overridden; UPI reviewed once only. `test_admin_*` |
| 15 | Errors do not leak secrets | PASS | Gateway errors logged server-side, generic message to client. `test_gateway_errors_do_not_leak_details`, `test_admin_settings_expose_mode_but_never_secrets` |

## Residual risks (not fixed or not verifiable here)

1. **PostgreSQL**: *(updated in Phase 10)* the full payment suite and a concurrent-confirmation test pass on a local PostgreSQL 16.15, and the partial unique index exists there. Your production database is still unverified.
2. **Index creation is best-effort.** If legacy data prevents a unique index, startup continues with a logged warning and app-level checks only.
3. **Verify trusts the signed callback.** It does not call Razorpay to re-fetch the payment. This is Razorpay's documented pattern; amount integrity comes from the server-created order and the webhook amount check.
4. **Auto-capture** must be confirmed in the Razorpay dashboard; a payment that is only authorized could otherwise be treated as paid on the browser callback. NOT VERIFIED.
5. **Rate limiter** is in-memory per process (not shared across workers or restarts) and keys on the `X-Forwarded-For` header, which a client can spoof if the proxy does not overwrite it. Pre-existing; affects limiting only.
6. **Refunds are made in the Razorpay dashboard.** The app records them via webhook; it cannot initiate a refund. Only `refund.processed` is handled.
7. **Webhook endpoint** is intentionally not rate limited (Razorpay retries); body capped at 256 KB and signature checked first.
8. **Real webhook payloads not tested.** Event names match Razorpay's published list; entity field layout follows the documented `payload.<entity>.entity` shape, but a real Razorpay test-mode delivery should be done once. NOT TESTED.
9. **UPI manual flow** remains inherently weaker (free-text UTR verified by an admin by eye).
10. **Admin UI** wording for new statuses (Refunded) and button visibility were not browser-tested. NOT TESTED.
11. Deployment state of `RAZORPAY_WEBHOOK_SECRET` on Render and the dashboard webhook URL are unknown. NOT VERIFIED.
