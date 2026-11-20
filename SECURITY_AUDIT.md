# Security Audit

## Findings

### 1. Secrets were exposed in the repo example file
The previous `.env.example` included production-looking credentials and a default admin password. This is not acceptable for source control and can lead to account takeover if reused in a real environment.

Resolution:
- Removed hardcoded secret-like values from `.env.example`.
- Replaced with placeholder values and comments.
- Kept production values out of the repository.

### 2. Insecure secret fallbacks existed in code
The application previously defaulted `SECRET_KEY` and `ADMIN_PASSWORD` to hardcoded values. That pattern is unsafe in production and makes deployments easier to compromise.

Resolution:
- `SECRET_KEY` now falls back to a generated value when absent.
- `ADMIN_PASSWORD` now creates a generated temporary admin password if unset and warns in startup logs.
- Production environments should still set both explicitly in the environment.

### 3. No explicit production guard for database choice
The app defaulted to SQLite without a production environment check.

Resolution:
- `APP_ENV=production` now requires `DATABASE_URL` to be present.
- SQLite remains allowed for local development only.

### 4. Upload validation needed stricter configuration
The app already validates a subset of image types and sizes, but storage handling is not yet hardened and should support cloud-backed persistence.

Resolution:
- Added a configurable upload provider (`UPLOAD_STORAGE_PROVIDER`).
- Kept local uploads as default for development.
- Added server-side validation and size enforcement.
- Added S3-compatible storage support when credentials are configured.

### 5. Public account deletion was required for compliance
The app already had an in-app deletion path, but the Play Store-style external deletion flow needed a public endpoint and UI.

Resolution:
- Added a public account deletion API route.
- Added a public HTML page at `/delete-account-request`.

## Additional hardening actions taken

- Added CORS configuration with allow-list semantics.
- Added basic rate limiting for sensitive authentication endpoints.
- Added no-store caching headers for API responses and privacy/account-deletion routes.
- Preserved admin-only route protection.
- Kept the frontend and API contract stable.

## Recommended next steps

1. Set real values in a production environment file that is never committed.
2. Use PostgreSQL instead of SQLite in hosted production.
3. Configure a persistent upload backend such as S3 or Cloudinary.
4. Set VAPID keys for web push notifications.
5. Configure Google Play package name and signing SHA256.
6. Rotate any real secret that was previously exposed in the repository or in deployment logs.
