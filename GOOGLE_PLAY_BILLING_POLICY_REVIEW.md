# Google Play Billing Policy Review (Phase 6)

Researched 2026-11-19 from official Play Console Help pages fetched that day:
- Payments policy: https://support.google.com/googleplay/android-developer/answer/9858738
- User choice billing overview: https://support.google.com/googleplay/android-developer/answer/13821247
- India program: https://support.google.com/googleplay/android-developer/answer/13306652
- Not fetched (NOT VERIFIED): FAQ/timelines page `/answer/10281818` beyond a search snippet, the service-fee pages (`/answer/112622`, `/answer/16954621`), and the alternative billing API developer docs.

**This is a research summary, not legal advice or a ruling by Google.** Policies change; re-read them before release.

## What the policy says (paraphrased)
- Play-distributed apps that require or accept payment for in-app features, services, app functionality, digital content or goods must use Play's billing system (Payments policy §2). Listed examples include education and other content subscriptions, app functionality or content, and cloud services.
- Play Billing must **not** be used for primarily physical goods/services, P2P payments, gambling, and some other categories (§3). None of these fits a certificate fee.
- Apps may not lead users to another payment method via listing, promotions, in-app webviews, buttons, links or messaging, or sign-up flows (§4), except where §3, §8 or §9 apply.
- §8/§9: developers in eligible countries may offer an alternative billing system or lead users outside the app, **only if enrolled in the applicable program**.
- Per the official overview page, India has a **user choice billing** program: an alternative billing system **alongside** Google Play's, for mobile and tablet users; the service fee is reduced by 4% when the user pays via the alternative. Requirements listed: enroll in Play Console (Alternative billing page), accept terms and set up a payment profile, certify PCI DSS compliance, give users a way to report fraudulent transactions, integrate the alternative billing APIs, manage per-app settings, **report every authorised transaction to Google within 24 hours**, and pay the adjusted service fee on invoiced transactions. The page says web-based payment in an embedded webview is allowed under the program, subject to the same requirements.
- The overview page lists the India API "Manual Sunset Date" as TBA.
- The external offers / link-out programs shown in the pages I read name other markets (e.g. the United States). I found nothing granting India link-out rights, so **do not assume it**.

## Applying it to Upnivo

| Question | Assessment | Confidence |
|---|---|---|
| Is internship access a digital service? | The internship content (briefs, tasks, review) is delivered digitally, but the code charges nothing for enrollment. A free service involves no in-app purchase. | Medium: depends on you staying free |
| Is the certificate fee a payment for a digital service? | It unlocks an in-app digital document (view/PDF). That is most naturally "app functionality or content" under §2. An argument exists that it certifies a real-world programme, but none of the §3 exclusions fits. **Treat as in scope.** | Medium; only Google can give a binding answer |
| Is Play Billing required per flow? | Enrollment: no payment, so no. Certificate fee via Razorpay or UPI **inside the Android app**: yes unless an enrolled alternative-billing program applies. | Medium |
| Does the TWA change anything? | A TWA shows your website inside a Play-distributed app. §4 names in-app webviews, buttons and links, so the conservative reading is that the website's payment UI **is** in-app payment UI. I found no official statement exempting TWAs. | Medium-low |
| India alternative billing | Available to any developer for India mobile/tablet users, but alongside Play Billing, not instead of it; needs enrollment, PCI DSS certification, fraud-reporting mechanism, API integration and 24h reporting. **Eligibility is not claimed**; it depends on your account and onboarding. | High on what the page says; unverified for your account |
| Fees | Standard Play service fee applies, 4% lower on alternative-billing transactions. I did not verify current fee percentages. | Not verified |
| Website payment vs in-app | A purchase consumed only outside a Play app is not covered, but the same website flow opened inside the app is. A user who pays on the website in a normal browser is outside the policy; **promoting that from inside the app is restricted by §4**. | Medium |

## Options (decision needed from you)

| Option | What it means | Effort | Risk |
|---|---|---|---|
| A. Play Billing for the certificate in the Android app | Create a one-time product in Play Console; in the TWA use the browser Digital Goods + Payment Request APIs (verify current Chrome/TWA support before committing); backend verifies purchases. Razorpay/UPI remain on the website only and are **hidden inside the app**. | Medium-high | Lowest policy risk |
| B. India user choice billing | Offer Razorpay alongside Play Billing for India users. Needs enrollment, PCI DSS certification, fraud reporting, alternative billing APIs. The APIs are described in terms of the native Play Billing Library; **whether they can be used from a TWA is NOT VERIFIED** and may need native code. | High | Medium; heavy compliance duty |
| C. No purchase in the app | Android app shows certificates only to users already entitled; no payment UI and no mention of paying elsewhere. Users pay on the website. | Low | Medium: §4 restricts steering, and a locked certificate with no explanation hurts UX/review |
| D. Make the certificate free (at least in the app) | Removes the billing question. Business decision. | Lowest | Lowest |

**Recommendation:** decide between A and D for the first release. Ask Google Play support (contact link on the India page) to confirm how they classify a certificate fee in a TWA before building.

## Architecture if Play Billing is required (Option A) — plan only, nothing implemented
1. Play Console: create a managed (one-time) product, e.g. `certificate_unlock`, priced in INR; price shown in-app must match Play's.
2. Client (TWA page): detect it is running inside the Play app, then use Digital Goods API `getDetails` and Payment Request with the Play Billing method to get a **purchase token**.
3. Backend: new endpoint receives `{application_id, product_id, purchase_token}` (login + ownership required). It calls the Google Play Developer API `purchases.products.get` with a service account (credentials in env, never in code) and checks: purchase state is purchased, product id matches, token not already used (unique constraint), obfuscated account id matches the user.
4. Entitlement: record a `Payment` row with `provider="play"`, `rzp_payment_id`-style unique token column, then mark Paid with the same atomic conditional UPDATE already used.
5. **Acknowledge** the purchase via the API; unacknowledged purchases are refunded by Google after a short window (check current length in docs).
6. Refunds/cancellations: subscribe to Real-time Developer Notifications (Pub/Sub) and/or poll the voided-purchases API; on void, set Refunded and lock the certificate.
7. Hide Razorpay/UPI UI when running inside the app; keep them on the website.
8. Tests need Play's licence testers and an internal testing track. Cannot be done locally.

I will not add placeholder or fake verification code; Option A needs your Play Console account, service account and a test track.

## Open items
- Confirm the classification with Google Play support.
- Verify fee pages and (for B) whether alternative billing APIs work from a TWA.
- If B: confirm PCI DSS obligations when using Razorpay's hosted checkout.
- Re-check the policy immediately before submission.
