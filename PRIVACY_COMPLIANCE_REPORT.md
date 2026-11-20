# Privacy Compliance Report

## Executive summary
The current application includes a student account deletion flow, a public self-service deletion page, and an in-app profile privacy section. The overall design is privacy-aware, but certain personal data and verification records are retained intentionally for certificate integrity, payment support, and legal compliance.

## Personal data categories in use

### Direct user data
- Name
- Email address
- Mobile number
- College / degree / department / year
- City / state / country
- Profile photo
- About text
- Password hash

### Student and internship history
- Enrollment records
- Task submissions and notes
- Mentor feedback
- Offer letter and start-date records
- Certificate status and certificate reference

### Payment and verification data
- UTR / payment metadata
- Certificate fee records
- Admin review records

### Uploaded files and media
- Profile image URLs
- Task screenshot URLs
- Uploaded static files under `uploads/`
- External object-storage URLs

## Privacy design result
- Passwords are hashed via Argon2.
- The account deletion flow anonymizes the user row and disables the account.
- The public deletion request requires the account email and password.
- Work records and certificate records remain for verification and business integrity.

## Retention posture
The app keeps some records longer than the account itself, especially when needed for:
- certificate verification
- payment disputes
- internal audit or support history
- legal or regulatory obligations

This is aligned with a privacy-friendly, compliance-focused approach: active personal data is removed from the account record, while immutable verification records remain in minimized, non-identifying form whenever necessary.

## User-facing policy status
The app’s in-page Privacy Policy and Delete Account instructions have been reviewed and updated to explain:
- what data is processed
- why it is processed
- how deletion works
- why some verification records may be retained

## Result
- PASS: account data is scrubbed on account deletion
- PASS: privacy policy and account-deletion guidance are present
- PASS: retention rationale is documented
- BLOCKED: live legal review is required before production launch
- NOT TESTED: third-party legal counsel review for a final regional compliance sign-off
