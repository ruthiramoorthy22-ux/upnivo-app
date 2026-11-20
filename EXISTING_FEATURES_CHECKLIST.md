# Existing Features Checklist

This checklist classifies the current platform features against the requested Google Play / production-readiness requirements.

## Student features

| Feature | Status | Notes |
| --- | --- | --- |
| Student registration | Working | `POST /api/register` creates users and hashes passwords with Argon2. |
| Student login | Working | JWT-based login is implemented with role checks. |
| Dashboard | Working | Student-facing app pages and API data are present. |
| Profile management | Working | `PUT /api/me` updates fields, including photo. |
| Internship domain selection | Working | Multiple domains and categories exist in the app and database. |
| Enrollment flow | Working | Enrollment API supports 1, 2, and 3 month program selection. |
| Offer letters | Working | Offer generation and sending endpoints exist. |
| Daily tasks | Working | Task unlocking follows a chronological progression. |
| Submission notes and links | Working | GitHub/demo/other link validation exists. |
| Screenshot uploads | Working | Local upload processing exists. |
| Notifications | Working | In-app notifications and optional push are supported. |
| Course completion and certificate flow | Working | Payment status and certificate unlock logic exist. |
| Privacy and Terms pages | Working | Routes exist for privacy and terms redirection. |
| Account deletion | Needs improvement | In-app deletion is implemented; public web deletion flow added for compliance. |

## Admin features

| Feature | Status | Notes |
| --- | --- | --- |
| Admin login | Working | Admin-only route protection exists. |
| Admin dashboard | Working | Aggregate stats and admin endpoints are present. |
| Student management | Working | Student list, detail, edit, and activation flows exist. |
| Internship management | Working | Add/edit/delete internships and tasks are supported. |
| Submission review | Working | Approve/rework actions exist. |
| Offer letter management | Working | Admin sends and reuses offer templates. |
| Certificate management | Working | Payment verification logic and settlement management exist. |
| Payment verification | Working | Payment review endpoints exist. |
| Messaging | Working | Announcements can be sent to all students or selected groups. |
| Notification management | Working | Notification reads and broadcast flows exist. |

## Platform / deployment features

| Feature | Status | Notes |
| --- | --- | --- |
| FastAPI backend | Working | App is a single-file API service with static assets. |
| PWA manifest | Working | `manifest.webmanifest` exists and `sw.js` is mounted. |
| Service worker | Working | Cache and offline-ready patterns are present. |
| Web push support | Needs improvement | VAPID config required for production use. |
| PostgreSQL support | Needs improvement | Code supports PostgreSQL URL but must not silently fall back to SQLite in production. |
| Persistent upload storage | Needs improvement | Local disk storage must be replaced or complemented with a cloud-backed provider. |
| Secret hygiene | Broken | Previous env example leaked credentials and insecure defaults. |
| Play Store packaging | Requires external configuration | Package name and SHA256 certificate required. |

## Preserved domains

- Full Stack Development
- Python Development
- Java Development
- AI & Machine Learning
- UI/UX Design
- Cyber Security
- Data Analytics
- Digital Marketing
- Mobile App Development
- Cloud & DevOps

These domains are present in the application and seed data.
