# Play Store Readiness Audit

## Executive summary

The project is a FastAPI + SQLite-first internship platform with an installable PWA shell and admin/student flows already implemented. It has the core business features for student registration, internship management, tasks, submissions, payments, notifications, and certificate generation. The application is far enough along to be publication-ready only after environment hardening, production database configuration, secure secret management, external deletion flows, and persistent upload storage are addressed.

## Status summary

- Core student flow: Working
- Admin flow: Working
- PWA / installability: Working
- Security hardening: Needs improvement
- Production DB configuration: Needs improvement
- Upload persistence: Needs improvement
- Account deletion compliance: Needs improvement
- Secret management: Broken (previously exposed in the example environment file)

## Audit by area

| Area | Status | Notes |
| --- | --- | --- |
| Student registration and login | Working | Password hashing is implemented via Argon2, and JWT tokens are issued. |
| Admin login | Working | Admin-only guard exists for administrative routes. |
| Internship catalog and plans | Working | 1 / 2 / 3 month program logic is present for multiple domains. |
| Daily task flow | Working | Task unlocking and submission logic is implemented. |
| Offer letter generation | Working | PDF/HTML offer letter generation exists with templating. |
| Certificate generation | Working | Certificate status and payment verification appear implemented. |
| Payment verification | Working | UPI and Razorpay support exists. |
| File uploads | Needs improvement | Local uploads are supported, but persistent cloud storage and validation are not fully productionized. |
| Push notifications | Needs improvement | PWA push support exists when VAPID keys are configured. |
| PWA manifest and service worker | Working | Installable app shell is present. |
| Android TWA configuration | Requires external configuration | `ANDROID_PACKAGE` and `ANDROID_SHA256` must be set for the Play Store. |
| Account deletion | Needs improvement | In-app deletion exists, but public external deletion flow should be clearly exposed. |
| Secret handling | Broken | Example env file previously contained real credentials and insecure defaults. |
| Production database | Needs improvement | Project defaults to SQLite and must require a production PostgreSQL URL in non-local deployments. |
| CORS and rate limiting | Needs improvement | Basic CORS is now configured; stricter request throttling should be maintained. |

## Feature classification summary

### Working
- Student registration and login
- Student profile management
- Internship enrollment and plan selection
- Daily task progression
- Admin review flow
- Notifications and announcement system
- PWA manifest / service worker
- Offer letter and certificate logic

### Needs improvement
- File uploads and storage persistence
- Secret handling and env hygiene
- Production database enforcement
- External deletion experience
- PWA / Play Store metadata configuration

### Broken
- Secret defaulting and credential exposure in the repo

### Not implemented
- None of the major business features are absent; this is a completed MVP with operational hardening needed.

### Requires external configuration
- PostgreSQL production database
- Google Play package + SHA256 signing certificate
- VAPID keys for push notifications
- Razorpay live keys if using online payments
- Cloudinary or S3-compatible storage for persistent uploads
