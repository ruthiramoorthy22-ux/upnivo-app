# Final Play Store Release Checklist

This is the go/no-go view. Detailed steps: `GOOGLE_PLAY_RELEASE_CHECKLIST.md`, `FINAL_DEPLOYMENT_GUIDE.md`.

**Can the app be submitted to Google Play now? No.** See the blockers.

## Hard blockers (must be resolved)
| # | Blocker | Owner |
|---|---|---|
| 1 | **Payment route decision.** Certificate fee via Razorpay/UPI inside the Android app likely needs Google Play Billing or an enrolled India user-choice-billing programme (or make the certificate free in the app) | You (+ Google support) |
| 2 | **No built or signed AAB.** Build blocked in my sandbox; you must create the signing key | You |
| 3 | **Digital Asset Links** not configured or verified (needs your key fingerprints + deployment) | You |
| 4 | **Real support email and developer name** in the privacy policy, listing and deletion page (`SUPPORT_EMAIL` not set; placeholder in use) | You |
| 5 | **Reviewer test account** does not exist | You |
| 6 | **Production deployment** of these changes, PostgreSQL, cloud storage, Razorpay webhook are unverified | You |
| 7 | Closed-testing requirement (12 testers × 14 days) if your developer account is personal and created after 2023-11-13 | You |

## Strong recommendations (not hard blockers)
- Attach a custom domain before building the app (domain change later = new app release).
- Decide retention periods; purge cloud-stored files on deletion.
- Build certificate verification (with unguessable IDs) only if you want to advertise it.
- Self-host fonts; add a CSP after a test-mode payment run.
- Test on at least one real Android phone and with TalkBack.

## Verified ready
Target API 36 configured · account deletion in-app + web with data purge · privacy/terms/refund as standalone pages · data safety draft · listing text · screenshots and feature graphic · security headers · health check · payment hardening · tests on SQLite and PostgreSQL 16.

## Verified NOT ready / not done
Build · signing · asset links · live domain/HTTPS · real-device tests · live Razorpay test · cloud storage test · Play Console forms.
