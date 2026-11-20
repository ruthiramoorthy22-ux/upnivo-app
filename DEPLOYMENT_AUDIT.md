# Deployment Audit

## Required production environment variables

Set these in the deployment environment, not in source control.

- `APP_ENV=production`
- `DATABASE_URL=postgresql://user:password@host:5432/upnivo`
- `SECRET_KEY=<long-random-secret>`
- `ADMIN_EMAIL=admin@yourdomain.com`
- `ADMIN_PASSWORD=<strong-admin-password>`
- `JWT` values are derived from `SECRET_KEY`; no separate JWT secret is required.
- `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` for live payments
- `RAZORPAY_WEBHOOK_SECRET` if using webhooks
- `VAPID_PRIVATE_KEY` and `VAPID_PUBLIC_KEY` for push notifications
- `ANDROID_PACKAGE` and `ANDROID_SHA256` for the Play Store TWA metadata
- `UPLOAD_STORAGE_PROVIDER=local|s3`
- `AWS_S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` when using S3
- `ALLOWED_ORIGINS=https://your-domain.com,https://app.your-domain.com`

## Production deployment guidance

1. Manage secrets in your hosting provider secret store.
2. Use PostgreSQL instead of SQLite in any public deployment.
3. Mount a persistent volume or object storage for uploaded files.
4. Keep upload storage behind a secure backend and avoid local disk-only storage in managed hosting.
5. Ensure the app is served over HTTPS.
6. Turn on `Cache-Control` and gzip only for static assets; keep API responses non-cacheable.
7. Back up the database and configure automated database migrations.

## Deployment checklist

- [ ] Production `DATABASE_URL` configured
- [ ] `SECRET_KEY` set and unique
- [ ] `ADMIN_PASSWORD` set to strong password
- [ ] TLS enabled
- [ ] Push notification keys configured if required
- [ ] TWA package metadata configured
- [ ] Persistent upload backend configured
- [ ] `APP_ENV=production` set
- [ ] No `.env` file committed to git

## Local development

For local development, the project can remain SQLite-based and use a local uploads directory. Set `.env` locally without checking it into source control. The example file is a template only.
