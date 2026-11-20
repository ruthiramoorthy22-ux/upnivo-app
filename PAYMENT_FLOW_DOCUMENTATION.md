# Payment Flow Documentation (as implemented after Phase 6)

## What is sold
Only the **certificate fee** (`cert_fee` setting, default ₹199, `CERT_FEE` env). Enrollment and internship tasks are not charged in the code. The fee unlocks viewing/printing the certificate once every task of the plan is submitted.

## Payment record states (`payments.status`)

| Status | Meaning | Set by |
|---|---|---|
| Created | Razorpay order exists, not yet paid (student may retry on the same order) | `razorpay-order` |
| Expired | Unpaid order older than `RAZORPAY_ORDER_TTL_HOURS` (24h); a late payment is still honoured | next `razorpay-order` call |
| Pending | UPI payment submitted, awaiting admin check | `pay` |
| Paid | Confirmed (Razorpay signature/webhook, or admin for UPI) | verify / webhook / admin |
| Rejected | Admin rejected a UPI payment | admin |
| Refunded | Fully refunded in Razorpay; certificate locks again | webhook `refund.processed` |

Allowed transitions: Created/Expired → Paid; Paid → Refunded (webhook only); Pending → Paid/Rejected (admin, once). Anything else is refused with 409.

## Razorpay flow
1. Student opens a finished program → `POST /api/applications/{aid}/razorpay-order` (login required, must own application, all tasks done).
   Server computes paise from the fee, calls Razorpay `/orders`, checks the reply (amount, currency, `order_` id), stores a `Created` row. If an open order exists it is returned again.
2. Browser opens Razorpay Checkout with `order_id`/`key_id` (public key only).
3. On success the browser calls `POST /api/applications/{aid}/razorpay-verify` with order id, payment id, signature. Server checks HMAC-SHA256(`order_id|payment_id`, key secret), checks the order belongs to this application, then performs one conditional UPDATE to Paid.
4. In parallel Razorpay posts to `POST /api/razorpay-webhook`. Server: secret configured? → size ≤ 256 KB → HMAC of raw body → dedupe on `x-razorpay-event-id` → handle event → commit. A handler failure rolls back the dedupe row so Razorpay's retry works.

Webhook events handled: `payment.captured`, `order.paid` (settle after amount and currency match), `payment.failed` (note only, order stays open), `refund.processed` (adds to `refunded_paise`; full refund → Refunded). Others are acknowledged and ignored.

Whichever of steps 3/4 arrives first wins; the other is a harmless no-op. Duplicate payment on one application: both kept, admin is alerted to refund one.

## UPI flow (unchanged behaviour)
Admin "send payment details" → student pays and enters UTR (≥6 chars, not already used) → status Pending → admin marks Paid/Rejected once.

## Database changes (additive only)
`payments` gains nullable columns `provider, order_id, rzp_payment_id, currency, amount_paise, refunded_paise, updated`; new table `webhook_events`; indexes `ix_payments_order_id`, unique `uq_payments_rzp_payment_id`, unique partial `uq_payments_one_open_per_app`. Applied automatically at startup by `migrate()`/`create_all`; nothing is dropped or rewritten. Legacy rows (order id stored in `utr`) still resolve; tested in `test_existing_database_is_upgraded_without_losing_payments`.

## Operator checklist (not done by me)
- Razorpay dashboard: webhook URL `https://<your-domain>/api/razorpay-webhook`, events above, secret = `RAZORPAY_WEBHOOK_SECRET`.
- Confirm auto-capture is on. Keep test keys (`rzp_test_`) for testing; live keys only in production.
- Refunds: Razorpay dashboard.
- `GET /api/admin/settings` shows `razorpay_mode` and whether the webhook secret is set.
