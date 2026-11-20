# Database Migration Guide

## Goal

Provide a safe and transparent migration path from the current codebase to a PostgreSQL-ready deployment without risking data loss or destructive schema changes.

## Current migration model

The project currently relies on SQLAlchemy `Base.metadata.create_all(engine)` during application startup, followed by a lightweight runtime `migrate()` function that adds columns to older schemas when they are missing. This is a pragmatic migration approach for local and small deployment scenarios.

## Safety rules

- Never run destructive migrations on an existing production database.
- Never drop tables or columns without explicit backup and approval.
- Never delete student records during schema migration.
- Prefer additive migrations over destructive edits.
- Always test migrations against a local SQLite or local PostgreSQL clone before production use.

## Recommended migration approach

### Option A: keep the low-risk runtime migration pattern
This is the current project pattern and is acceptable for a small app while keeping data intact.

Advantages:
- minimal change to the existing architecture
- additive schema changes only
- straightforward for local development

Cautions:
- runtime column checks can accumulate complexity over time
- production migration permissions and logs should still be reviewed carefully

### Option B: add Alembic for stricter schema control
For production readiness, Alembic is the preferred long-term option if the team wants more formal migration management.

Suggested setup:
- install Alembic
- initialize Alembic in the project
- create a baseline revision from the current schema
- add only additive revision files for new columns or indexes
- review each migration with a local test database before production use

## Recommended migration checklist

Before deploying any migration:
- create a database backup
- confirm the exact version in use
- run the migration against a local test copy
- validate user, enrollment, submission, and payment counts before and after
- confirm no data is silently deleted
- record the migration in an operational runbook

## Known compatibility

The existing schema is compatible with PostgreSQL for a standard SQLAlchemy application. The important constraint is to execute migrations only when the environment is declared and approved for production use.

## Production decision

A production migration is not executed in this phase. This remains a manual upgrade step that requires the operator to confirm the target environment, data backup, and service owner approval.
