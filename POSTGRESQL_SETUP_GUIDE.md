# PostgreSQL Setup Guide

## Purpose

This guide explains how to configure PostgreSQL for the existing Upnivo application without altering the current local SQLite workflow.

## Safety requirements

- Never connect to or modify a real production database during local validation.
- Keep real credentials in the deployment environment, not in source code.
- Use local SQLite for development unless an isolated PostgreSQL test database is explicitly configured.
- Never commit `.env` or `.env.*` files with real credentials.

## Recommended local PostgreSQL container

A safe local PostgreSQL container can be used for testing before production deployment. Example:

```powershell
docker run --name upnivo-postgres -e POSTGRES_USER=upnivo -e POSTGRES_PASSWORD=replace-with-strong-local-password -e POSTGRES_DB=upnivo -p 5432:5432 -d postgres:16
```

Then set the environment variable:

```powershell
$env:DATABASE_URL = 'postgresql://upnivo:replace-with-strong-local-password@localhost:5432/upnivo'
$env:APP_ENV = 'production'
```

## Required environment variables

Example values:

```powershell
$env:APP_ENV = 'production'
$env:DATABASE_URL = 'postgresql://user:strong-password@host:5432/upnivo'
$env:SECRET_KEY = 'long-random-secret'
$env:ADMIN_EMAIL = 'admin@yourdomain.com'
$env:ADMIN_PASSWORD = 'replace-with-strong-admin-password'
```

## PostgreSQL compatibility notes

The app uses SQLAlchemy ORM models with standard SQLite-compatible types plus a few `TEXT` columns. PostgreSQL is compatible with the current schema and ORM model. The major production requirement is to ensure the runtime environment actually sets `DATABASE_URL` and does not default silently to SQLite.

## Connection pooling and timeouts

For production hosting, it is advisable to use application-level pooling and connection retries. Suggested settings:

- pool_pre_ping: enabled
- statement timeouts: set in the host service where applicable
- connection retry on startup: enabled in app server or hosting layer
- avoid connection leakage by closing sessions in `db()` dependency finalizers

The project already uses a SQLAlchemy sessionmaker and a `db()` generator that closes sessions promptly.

## Recommended production deployment configuration

- Use PostgreSQL managed by the hosting provider or a secure external database service.
- Keep secrets in the deployment environment secret store.
- Ensure `APP_ENV=production` is set explicitly.
- Keep local development SQLite as a separate, non-production path.

## Validation checklist

Before moving to a live PostgreSQL deployment, confirm:
- `DATABASE_URL` is defined
- `APP_ENV=production` is set
- the app starts without SQLite fallback
- the app can create/validate tables with the target database
- a local test user can register and log in
- admin routes remain accessible
- seed data and migration scripts do not remove existing records

## Critical restriction

This phase intentionally does not connect to or modify the real production database. Production database provisioning and migration must be approved before deployment.
