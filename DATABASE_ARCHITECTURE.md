# Database Architecture

## Overview

The Upnivo app uses SQLAlchemy ORM models with a SQLite-first development configuration and a PostgreSQL-ready production model. The architecture is centered around users, internships, task progression, applications, submissions, and payments.

## Core entities

### User
- Represents student and admin accounts.
- Stores profile data and authentication metadata.
- Uses Argon2 hashed password storage.
- A unique `email` index prevents duplicate account creation.

### Internship
- Stores the internship definition, metadata, and plan capacity.
- Contains category, duration, skills, outcomes, and published state.
- Task generation relies on this metadata during startup seeding.

### Task
- One task per day per plan for each internship.
- Ordered by `months` and `day` to unlock tasks in sequence.
- Task content includes `title`, `submit`, `brief`, `image`, and `resource`.

### Application
- Links a student to an internship enrollment.
- Stores enrollment status, planned duration, and offer/start data.
- The unique `(user_id, internship_id)` rule prevents duplicate enrollments.

### Submission
- Represents a student’s submission for a specific task in a specific application.
- Stores the demo GitHub link, notes, screenshot, and review feedback.
- The unique `(application_id, task_id)` rule prevents duplicate task submission rows.

### Payment
- Tracks certificate fees and UPI/Razorpay verification state.
- Linked to an application record so payment status can unlock or block certificate generation.

### Settings
- Stores configuration values for templates, payment, and certificate metadata.
- Allows admin control without changing code.

## Relationship flow

1. A user registers. A `users` row is created.
2. A student applies to an internship. An `applications` row is created.
3. The app retrieves tasks for the selected plan and adds or reads `tasks` rows.
4. The student submits work to the current task via `submissions`.
5. The admin reviews `submissions` and sets statuses such as Approved/Rework.
6. When the internship completes and the certificate fee is paid, a `payments` row is created and verified.
7. Offer letters, notifications, and certificate generation depend on `applications`, `users`, and `settings`.

## Local vs production model

### Local SQLite
- Used for development and tests.
- Acceptable for development speed and local verification.
- Not used for production deployment.

### PostgreSQL production
- Intended production database.
- Should run with explicit `DATABASE_URL` set and a managed secret source.
- Must not silently fall back to SQLite in production.

## Transaction safety

The current app uses individual SQLAlchemy sessions and commits after each significant workflow, which is appropriate for a single-service app. The most critical transactions are:
- student registration
- internship enrollment
- task submission
- payment verification
- account deletion request

These operations should remain wrapped in transactions in future migrations when more complex consistency checks are added, especially around certificate unlocks and payment settlement.

## Current schema assessment

The database is already well aligned with the business workflow. It is not excessively complex and remains compatible with PostgreSQL. The main hardening tasks are:
- enforce production-only DB configuration
- add more explicit indexes for common filters
- document safe migration steps
- manage account deletion and retention rules carefully

## Conclusion

The app’s data model is consistent with its business functionality and ready for a controlled PostgreSQL production migration, but it must be staged carefully with explicit environment configuration and without any destructive schema changes.
