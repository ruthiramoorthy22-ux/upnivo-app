# Database Health Check Guide

## Goal

Verify that the app remains healthy locally without altering production data or exposing private information.

## Suggested checks

### 1. Table existence

```sql
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
```

Expected tables include:
- users
- internships
- tasks
- applications
- submissions
- payments
- settings
- notifications
- push_subs
- audit_logs

### 2. Duplicate account detection

```sql
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

### 3. Orphaned references

```sql
SELECT a.id, a.user_id
FROM applications a
LEFT JOIN users u ON u.id = a.user_id
WHERE u.id IS NULL;
```

```sql
SELECT s.id, s.application_id
FROM submissions s
LEFT JOIN applications a ON a.id = s.application_id
WHERE a.id IS NULL;
```

```sql
SELECT p.id, p.application_id
FROM payments p
LEFT JOIN applications a ON a.id = p.application_id
WHERE a.id IS NULL;
```

### 4. Application count sanity check

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM applications;
SELECT COUNT(*) FROM submissions;
SELECT COUNT(*) FROM payments;
```

### 5. Admin presence

```sql
SELECT id, email, role, active FROM users WHERE role = 'admin';
```

### 6. Index and FK review

Use SQLAlchemy inspection or database metadata to verify the application has the expected indexes and foreign keys.

## Operational advice

- Run this check on a sandbox or local development database only.
- Keep all production checks outside the current machine and require explicit approval before execution.
- Investigate missing or duplicate records before making a schema change.

## Local test status

The current verification used a local SQLite database in the project workspace and did not modify production data.
