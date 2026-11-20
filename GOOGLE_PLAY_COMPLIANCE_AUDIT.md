# Google Play Compliance Audit (Phase 9)

Date 2026-11-19. **This reports verified readiness only. It is not an approval and Google has reviewed nothing.**

Sources actually fetched/read: Android Developers "Meet Google Play's target API level requirement" (updated 2026-10-28); Play Console Help: Payments (9858738), User choice billing (13821247), India billing (13306652). Seen in search results (official pages, not fully read): app testing for new personal accounts (14151465), User Generated Content (9876937, 12923286). Account-deletion rules were confirmed from Google's own 2023 announcement as quoted by several outlets, **not** from the current Play Console page. Re-read every official page before submission.

| # | Requirement | Finding | Status |
|---|---|---|---|
| 1 | **Target API level** | New apps and updates must target **API 36** from 2026-08-31. Generated project targets 36 (compileSdk 36). Not compiled here. | READY (unbuilt) |
| 2 | **Minimum functionality / not a bare web wrapper** | It is a TWA of your own site with accounts, tasks, uploads, notifications, certificates: real functionality. I did not re-read the Spam/Minimum Functionality policy text. | LIKELY OK, UNCONFIRMED |
| 3 | **Account creation → in-app deletion** | In-app `Profile → Delete my account` works (tested). | PASS (tested locally) |
| 4 | **Account deletion → web link** | `/delete-account-request` page works, names the app and package, lists deleted/kept data (tested at 320px, flows tested). Enter this URL in the Data safety form. **Gaps**: developer name not shown (placeholder needed), retention duration undefined, requires the password (no self-service reset exists; users are told to email support), cloud-stored files not purged. | PARTIAL |
| 5 | **Privacy Policy** | Now a **standalone server-rendered HTML page at `/privacy`** (also `/terms`, `/refund`), generated from the same text as the in-app page (tested; no JavaScript needed). Text corrected to match the code. **Remaining blockers**: contact email is `admin@yourdomain.com` until you set `SUPPORT_EMAIL`; the policy must name the developer/entity (not invented). | **BLOCKER until contact + developer name are real** |
| 6 | **Data safety form** | Draft in GOOGLE_PLAY_DATA_SAFETY_DRAFT.md. Not submitted. | DRAFT |
| 7 | **Permissions** | Only `POST_NOTIFICATIONS` is declared. No location, camera, contacts. (`INTERNET` is a normal permission.) | PASS (by inspection of generated manifest) |
| 8 | **Push notification permission** | Android 13+ runtime permission is requested by the TWA's notification delegation. The web app shows its own opt-in banner rather than prompting on launch. Not tested on a device. | NOT TESTED |
| 9 | **User-generated content** | Official UGC policy concerns content that **other users** can see. Student submissions are visible only to the student and admins; messages go admin→student only; no student-to-student content. So the in-app report/block duties most likely do not apply. Admin review exists (approve/rework). I do **not** claim compliance; confirm with the content-rating questionnaire and policy text. | LIKELY N/A, UNCONFIRMED |
| 10 | **Payments policy** | Certificate fee paid by Razorpay/UPI inside the TWA may violate the Play Billing requirement. **Unresolved decision.** See GOOGLE_PLAY_BILLING_POLICY_REVIEW.md. | **BLOCKER (decision)** |
| 11 | Subscriptions | None in the code. | N/A |
| 12 | **App access for reviewers** | Login required. Needs a dedicated reviewer account and instructions (GOOGLE_PLAY_REVIEWER_ACCESS_GUIDE.md). Credentials do not exist yet. | TODO |
| 13 | **Store listing** | Drafted. Needs real contact details, screenshots, 512×512 icon, 1024×500 feature graphic. | DRAFT |
| 14 | **Signing** | Play App Signing + your own upload key. None exists. | TODO (yours) |
| 15 | **App content declarations** | Privacy policy URL, ads (none), app access, content rating (IARC questionnaire), target audience, data safety, financial features declaration. All to be completed by you in Play Console. | TODO (yours) |
| 16 | **Ads** | No ad SDK or ad code. Declare "No ads". | PASS (by inspection) |
| 17 | **Developer contact** | Email required; address/phone rules depend on account type. None invented. | TODO (yours) |
| 18 | **Testing requirement** | Personal developer accounts created after 2023-11-13 must run a closed test with ≥12 opted-in testers for 14 continuous days before applying for production. Check your account type. | TODO (yours) |

## Other compliance observations
- Audience: the policy says students 16+. Play requires an accurate target-age declaration; apps accepting minors have extra obligations. Decide deliberately (18+ is simplest).
- Payment copy in-app and refund policy should match whatever billing route you choose.
- The privacy policy said certificates can be "verified by anyone" (no such feature exists): corrected, not implemented (see FINAL_FEATURE_VERIFICATION.md).
- Android "developer verification" requirements for distributing outside Play were not researched.

## Verdict
**Not ready to submit.** Blockers: payment-policy decision (#10), standalone privacy policy URL with real contact/developer name (#5), reviewer access (#12), signing key and a real build (#14, Phase 8), account/testing requirements (#18).
