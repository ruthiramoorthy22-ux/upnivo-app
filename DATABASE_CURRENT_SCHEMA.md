# Database Current Schema

This document summarizes the current SQLAlchemy schema used by the Upnivo app and its local SQLite development database.

## Database engine

- Local development: SQLite (`sqlite:///./upnivo.db`)
- Production target: PostgreSQL (`postgresql://user:pass@host:5432/upnivo`)
- Database configuration is driven by `DATABASE_URL` from environment variables.
- The project intentionally does not silently fall back to SQLite in production because the app now enforces `APP_ENV=production` + `DATABASE_URL` requirements.

## Tables

### users

Columns:
- `id` (PK)
- `name`
- `email` (unique index)
- `mobile`
- `college`
- `degree`
- `department`
- `year`
- `about`
- `city`
- `state`
- `country`
- `gender`
- `pw` (hashed password)
- `photo`
- `role` (`student` or `admin`)
- `active`
- `created`

Notes:
- `email` has a unique index and is used as the stable account identifier.
- `pw` is Argon2-hashed and not plain text.
- `active` controls account suspension and deletion state.

### internships

Columns:
- `id` (PK)
- `title`
- `org`
- `category`
- `duration`
- `mode`
- `skills`
- `description`
- `outcomes`
- `eligibility`
- `published`
- `is_sample`
- `method`
- `roles`
- `tools`
- `final`
- `roadmap`
- `image`
- `plans`

Notes:
- Internship categories include the 10 preserved domains.
- `plans` stores the enabled plan options such as `1,2,3`.

### tasks

Columns:
- `id` (PK)
- `internship_id` (FK -> internships.id)
- `months`
- `day`
- `theme`
- `title`
- `submit`
- `brief`
- `image`
- `resource`

Notes:
- Data is organized per internship and plan duration (`months`).
- `day` is the sequence within a given plan.
- The project currently keeps a composite index on `internship_id` and relies on the order-by sequence for task unlocking logic.

### applications

Columns:
- `id` (PK)
- `user_id` (FK -> users.id)
- `internship_id` (FK -> internships.id)
- `months`
- `status`
- `note`
- `created`
- `offer_date`
- `offer_ref`
- `start_date`
- `offer_note`
- `offer_snap`

Notes:
- There is a unique constraint on `(user_id, internship_id)`.
- This prevents duplicate enrollment in the same internship.
- The app uses application status tracking for review, offer, and completion flow.

### submissions

Columns:
- `id` (PK)
- `application_id` (FK -> applications.id)
- `task_id` (FK -> tasks.id)
- `link`
- `notes`
- `image`
- `github`
- `video`
- `status`
- `feedback`
- `created`

Notes:
- There is a unique constraint on `(application_id, task_id)`.
- This avoids duplicate task submissions per application.

### payments

Columns:
- `id` (PK)
- `application_id` (FK -> applications.id)
- `amount`
- `utr`
- `status`
- `note`
- `created`

Notes:
- Payment records are used for certificate unlock and admin verification.
- `status` values include Pending, Created, Paid, Rejected.

### settings

Columns:
- `key` (PK)
- `value`

Notes:
- Used for template settings, fee values, UPI configuration, and app settings.

### notifications

Columns:
- `id` (PK)
- `user_id`
- `to_admin`
- `title`
- `body`
- `link`
- `read`
- `created`

Notes:
- Indexed by `user_id` for retrieval efficiency.

### push_subs

Columns:
- `id` (PK)
- `user_id`
- `endpoint`
- `p256dh`
- `auth`
- `created`

Notes:
- Stores browser push subscription metadata for web notifications.

### audit_logs

Columns:
- `id` (PK)
- `actor`
- `action`
- `created`

Notes:
- Useful for review and forensic tracking of user/admin actions.

## Integrity review

### Strong points
- Primary keys are present on all tables.
- Foreign key relationships exist for applications, tasks, payments, and submissions.
- Unique constraints protect users and application/task submission duplication.
- `email` uniqueness prevents duplicate accounts.
- `application_id + internship_id` uniqueness prevents duplicate enrollment records.
- `application_id + task_id` uniqueness prevents duplicate submissions.

### Observed gaps / caution points
- Some tables rely on `nullable` data rather than strict non-null constraints, which is acceptable for a flexible app but should be tightened in a carefully controlled migration.
- There are no explicit composite indexes on common queries such as `applications(user_id, internship_id)` and `submissions(application_id, status)`.
- `status` strings are currently text values; for PostgreSQL, an enum could be introduced later if desired, but this would be a non-destructive but schema-level migration.
- `notifications` and other tables are not currently normalized for tenant-specific use, which is fine for a single app instance but worth noting for multi-tenant future-proofing.

## Production recommendation

For PostgreSQL, the current schema is compatible with a standard SQLAlchemy ORM and should work with the app as-is, provided the app is configured with a real `DATABASE_URL` and production secret management. The app should not silently fallback to SQLite.
