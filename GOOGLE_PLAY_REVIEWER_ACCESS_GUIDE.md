# Google Play Reviewer Access Guide

Play reviewers must be able to use every part of the app that needs a login. Provide this in **Play Console → App content → App access** ("All or some functionality is restricted" → add instructions).

## Create the reviewer account (you do this on the live site, after approving deployment)
1. In the app, register a normal student: name e.g. `Play Reviewer`, an email address **you control** (e.g. a mailbox you create for review), a password you generate. **Do not reuse a real password; do not commit it anywhere.**
2. Sign in to `/admin`, open **Enrollments**, approve the reviewer's enrollment, and **send the offer letter** so tasks unlock.
3. Optionally submit and approve a few tasks so the progress screens are populated.
4. To show the certificate flow without a real payment, complete all tasks and mark the certificate fee as paid from **Payments** only if you use a test/UPI-manual path; never expose live payment credentials to reviewers.
5. Keep the account active for the whole review period; reviewers may test deletion, so keep a spare.

## Text to paste into Play Console (fill the bracketed values)
```
Upnivo requires a student account.
Email: [REVIEWER EMAIL]
Password: [REVIEWER PASSWORD]
Steps: open the app → Log in → Home shows internship domains → My Programs shows an enrolled
program → open it to see daily tasks, the offer letter and notifications → Profile → "Delete my account"
shows the in-app account deletion flow (please do not use it with this reviewer account).
Account deletion web page: https://upnivo-intern.onrender.com/delete-account-request
No special hardware, location or SMS/OTP is required. Payment for the certificate: [DESCRIBE THE ROUTE YOU CHOOSE].
```

## Rules
- No 2-factor or OTP on this account (none exists in the app today).
- The Render service must be awake during review; cold starts on the free tier can make the first load slow, which looks like a crash to reviewers.
- Admin credentials must never be given to reviewers.
