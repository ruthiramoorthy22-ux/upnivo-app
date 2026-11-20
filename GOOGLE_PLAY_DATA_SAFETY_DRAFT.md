# Google Play Data Safety Draft

**Draft only. Not submitted, not reviewed by Google. You are legally responsible for the final answers.** It was built from the code (models, endpoints, frontend, libraries) as of 2026-11-19. Re-check it whenever data handling changes, and compare against Google's current form (Play Console → App content → Data safety).

## What the code actually does (evidence)
| Fact | Evidence |
|---|---|
| Account fields: name, email, mobile, college, degree, department, year (required); city, state, gender, about, photo (optional) | `User` model, `/api/register`, `/api/me` |
| Password stored as Argon2 hash | `PasswordHasher` in `main.py` |
| Student submissions: links, GitHub, demo/video links, notes, screenshots | `Submission` model, `/api/upload` |
| Payments: card/UPI details are entered on Razorpay's checkout; the server stores only order/payment ids, amount, status, and for manual UPI the user-typed UTR | `Payment` model, Razorpay endpoints |
| Push registrations (endpoint + keys) only if the user enables notifications | `PushSub`, `enableNotif()` |
| Notifications, admin audit log | `Notification`, `AuditLog` |
| IP address used for rate limiting in memory only; not stored by the app (the host's access logs may contain it) | `client_ip()` / rate limiter |
| **Not collected**: location, contacts, advertising ID, device IDs, analytics, crash SDK, ads | no such code or libraries (grep of frontend and `requirements.txt`) |
| Third-party endpoints contacted by the pages | Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`: receives IP/user agent), Razorpay Checkout (only when paying), Render (hosting), optional Cloudinary/S3 for images if configured |
| Encryption in transit | HTTPS on Render; HSTS header sent over HTTPS. Not verified on the live site from this sandbox. |
| Deletion | in-app + web page; removes profile, notifications, push, submission content, local screenshot files (tested) |

## Proposed answers

### Overview questions
| Question | Draft answer |
|---|---|
| Does the app collect or share any of the required user data types? | Yes |
| Is all collected data encrypted in transit? | Yes (confirm HTTPS on the live domain first) |
| Do you provide a way for users to request deletion? | Yes. In-app: Profile → Delete my account. Web: `https://upnivo-intern.onrender.com/delete-account-request` (or your custom domain) |

### Data types
"Collected" = transmitted off the device to you or a processor. "Shared" in Google's definition excludes transfers to a **service provider processing on your behalf**; whether Razorpay counts as such for payment data is a judgement you must confirm against Google's definitions. I marked it conservatively.

| Category → type | Collected | Shared | Required / optional | Purpose |
|---|---|---|---|---|
| Personal info → Name | Yes | No (processors only) | Required | Account management, App functionality |
| Personal info → Email address | Yes | No | Required | Account management, Communications |
| Personal info → Phone number | Yes | No | Required (registration form) | Account management |
| Personal info → Other info (college, degree, department, year, city, state, gender, bio) | Yes | No | College/degree/department/year required; rest optional | App functionality |
| Personal info → User IDs | Yes (internal account id) | No | Required | Account management |
| Financial info → Purchase history / payment info | Yes (payment ids, amount, status; UTR) | **Decide**: Razorpay processes the payment itself | Only if user pays the certificate fee | App functionality (certificate unlock), Fraud prevention/security |
| Photos and videos → Photos | Yes (profile photo, task screenshots) | No (stored by host/storage provider on your behalf) | Optional photo; screenshots optional per task | App functionality |
| App activity → Other user-generated content | Yes (notes, links, GitHub/demo links) | No | Optional per task | App functionality |
| App info and performance → Diagnostics | No code collects crash/diagnostic data (host logs aside) | - | - | - |
| Device or other IDs | **No** by the app. Push registrations contain a push endpoint token if the user enables notifications | No | Optional | Communications |
| Location, Contacts, Health, Audio, Files, Calendar, Web browsing, Messages (SMS) | No | - | - | - |
| Authentication data (password) | Yes, collected for sign-in; Play has no separate password category, so describe within Personal info/Account management and in the privacy policy | No | Required | Account management, Security |

### Security practices
- Data encrypted in transit: Yes (HTTPS).
- Users can request deletion: Yes (links above).
- Independent security review: **No**.
- Follows Play Families policy: **Not applicable** (not designed for children; policy states 16+; see compliance audit on target audience).

## Known gaps you must resolve before publishing
1. **Retention period is undefined.** Deleted accounts keep a minimal enrollment record, payment record and audit log with no stated duration. Decide a period (and legal basis) and state it in the policy.
2. **Cloud-stored images are not purged on deletion.** Local files are deleted (tested); files uploaded to Cloudinary/S3 are not removed by the code. If you use those providers, add provider deletion or declare the limitation.
3. **Google Fonts** sends visitors' IPs to Google. Either self-host the fonts (recommended; removes a third party) or keep it disclosed.
4. **Support email in the policy** is a placeholder until you set `SUPPORT_EMAIL`.
5. Confirm Razorpay's role (processor vs. independent controller) for the "shared" answer.
6. No data-processing agreements reviewed; hosting region unknown (Render region should be recorded for any cross-border statement).
