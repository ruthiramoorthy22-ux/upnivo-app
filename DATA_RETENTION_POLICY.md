# Data Retention and Deletion Policy

## Purpose
This document defines what data is deleted immediately when a student account is removed, and what records are retained for legal, verification, or support reasons.

## Data deleted on account closure
When a user deletes an account, the app anonymizes the following account fields:
- name
- email
- mobile
- college
- degree
- department
- year
- city
- state
- gender
- about
- photo
- password hash

The account is marked inactive and `deletion_status` is set to `completed`.

## Data retained for business and legal reasons
The following are not fully removed during deletion because they support verification and compliance:
- application history and internship status
- payment references and certificate fee status
- certificate IDs and verification records
- audit log events tied to the account
- admin review metadata

These records are kept in a minimal form and are not used for unrelated marketing or profiling.

## Storage files and media
Uploaded files linked to the user are removed from active use by clearing the active profile URL and deactivating the account. Existing object-store files may remain in storage until a later provider cleanup policy is implemented. For a production deployment, the storage-layer cleanup must be explicitly configured.

## Admin authorization and ownership
- In-app deletion requires the account owner to be authenticated and to provide the current password.
- Public deletion requires the correct email and password for that account.
- Admins do not have a bulk deletion workflow in the app.

## Status and completion
The account deletion flow is recorded with a clear status value:
- `active` while the account is live
- `completed` after the anonymous deletion is processed

This gives a clear completion state for operational review and privacy handling.

## Policy result
- PASS: deletion behavior is documented and aligned with in-app privacy controls
- PASS: retention rationale is explicit
- BLOCKED: final legal retention wording requires product policy review before production launch
