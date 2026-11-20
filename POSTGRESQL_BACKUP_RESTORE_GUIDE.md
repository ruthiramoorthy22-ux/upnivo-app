# PostgreSQL Backup and Restore Guide

## Backup

For a PostgreSQL database, use a full logical dump during a controlled maintenance window.

Example:

```powershell
pg_dump -h host -U user -d upnivo -f upnivo_backup.sql
```

If the database is local and accessible via Docker:

```powershell
docker exec -t upnivo-postgres pg_dump -U upnivo -d upnivo > upnivo_backup.sql
```

## Restore

```powershell
psql -h host -U user -d upnivo < upnivo_backup.sql
```

Or for a local container:

```powershell
type upnivo_backup.sql | docker exec -i upnivo-postgres psql -U upnivo -d upnivo
```

## Safety notes

- Do not run backup or restore commands against the real production database during this verification phase.
- Keep a backup before any production migration or replica cutover.
- Validate the restored database by checking counts for `users`, `applications`, `submissions`, and `payments` before releasing the service.
- Never restore over a live production database without an approved maintenance window.

## Recommended verification after restore

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM applications;
SELECT COUNT(*) FROM submissions;
SELECT COUNT(*) FROM payments;
SELECT COUNT(*) FROM internships;
```

## Critical restriction

This guide documents the standard operational path but does not execute live backup or restore operations in the current environment.
