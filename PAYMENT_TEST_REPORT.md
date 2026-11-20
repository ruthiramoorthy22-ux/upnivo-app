# Payment Test Report (Phase 6)

Run date: 2026-11-19 · Python 3.12.3 · pytest · SQLite (throw-away database per test) · Razorpay replaced by a mock · credentials are fixtures (`rzp_test_FIXTURE`, etc.), not real.

## Summary
- Full suite: **============================= 37 passed in 23.74s ==============================**
- Baseline before changes: 5 passed (existing tests, still passing).
- New: 32 tests in `tests/test_payments.py`, all passed.
- `python -m py_compile main.py`: PASS.

## Mutation check (do the tests actually catch regressions?)
| Weakened behaviour | Result |
|---|---|
| Webhook amount/currency check removed | 1 test failed (caught) |
| Webhook duplicate-event guard removed | 1 test failed (caught) |
| Admin gateway-override guard removed | Not caught: the later "only Pending can be reviewed" rule blocks the same action, so the guard is redundant defence in depth, not a gap |

## Results
- PASS `test_payments.py::test_order_amount_is_set_by_the_server`
- PASS `test_payments.py::test_client_supplied_amount_is_ignored`
- PASS `test_payments.py::test_order_requires_login_and_ownership`
- PASS `test_payments.py::test_abandoned_checkout_can_be_resumed_not_stuck`
- PASS `test_payments.py::test_stale_order_expires_and_a_new_one_is_issued`
- PASS `test_payments.py::test_gateway_response_mismatch_is_rejected`
- PASS `test_payments.py::test_gateway_errors_do_not_leak_details`
- PASS `test_payments.py::test_order_not_available_until_all_tasks_done`
- PASS `test_payments.py::test_valid_signature_unlocks_certificate`
- PASS `test_payments.py::test_bad_signature_is_rejected_and_nothing_changes`
- PASS `test_payments.py::test_non_ascii_signature_does_not_crash`
- PASS `test_payments.py::test_other_students_order_cannot_be_verified`
- PASS `test_payments.py::test_replay_is_idempotent_but_a_different_payment_id_is_refused`
- PASS `test_payments.py::test_oversized_identifiers_rejected`
- PASS `test_payments.py::test_webhook_needs_configuration_and_a_valid_signature`
- PASS `test_payments.py::test_webhook_bad_signature_and_oversize`
- PASS `test_payments.py::test_webhook_unlocks_once_and_duplicate_delivery_is_ignored`
- PASS `test_payments.py::test_webhook_then_browser_verify_do_not_double_apply`
- PASS `test_payments.py::test_webhook_amount_or_currency_mismatch_never_unlocks`
- PASS `test_payments.py::test_webhook_unknown_order_and_unknown_event_are_acknowledged`
- PASS `test_payments.py::test_full_refund_locks_certificate_partial_refund_does_not`
- PASS `test_payments.py::test_late_payment_on_an_expired_order_is_still_honoured`
- PASS `test_payments.py::test_double_payment_is_flagged_for_refund`
- PASS `test_payments.py::test_admin_cannot_override_gateway_payments`
- PASS `test_payments.py::test_admin_payment_endpoints_require_admin`
- PASS `test_payments.py::test_upi_flow_is_reviewed_once`
- PASS `test_payments.py::test_admin_cannot_review_unpaid_gateway_orders`
- PASS `test_payments.py::test_same_utr_cannot_be_used_by_two_students`
- PASS `test_payments.py::test_payment_endpoints_are_rate_limited`
- PASS `test_payments.py::test_admin_settings_expose_mode_but_never_secrets`
- PASS `test_payments.py::test_existing_database_is_upgraded_without_losing_payments`
- PASS `test_verification.py::test_production_requires_database_url`
- PASS `test_verification.py::test_cors_and_admin_gate`
- PASS `test_verification.py::test_upload_validation_and_account_delete`
- PASS `test_verification.py::test_storage_security_validates_paths`
- PASS `test_verification.py::test_local_dev_database_is_safe`

## NOT TESTED
- Real Razorpay test-mode checkout, real webhook delivery, real refunds.
- *(Updated in Phase 10)* PostgreSQL: the whole suite, including the payment tests and a concurrent-confirmation race, now passes on a local PostgreSQL 16.15 and the partial unique index was confirmed to exist. Your **production** PostgreSQL is still not verified.
- Concurrent requests from multiple processes/threads (atomicity is by design of the conditional UPDATE, not load-tested).
- Browser checkout UI and admin payment screens (frontend files were not changed).
- Razorpay auto-capture setting; dashboard webhook configuration; Render environment.
- Google Play Billing (not implemented; see policy review).

## BLOCKED
- Anything needing real Razorpay or Play Console credentials (by your safety rules).
